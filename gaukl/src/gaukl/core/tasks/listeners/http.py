import urllib.request
from typing import Dict, Callable, List, Any

from gevent.pywsgi import WSGIServer
from requests import Request, Session

from gaukl.core.context.context import Context
from gaukl.core.tasks.listener import listener, on_request
from gaukl.core.tasks.task import task, Roles


@listener(shortname='http_listener')
def listener(context: Context, port: int = None) -> None:
    server = WSGIServer(('', port), http_on, environ={'context': context})
    server.serve_forever()


@on_request()
def handle_req(context: Context, env: Dict) -> Context:
    # Body
    data = env['wsgi.input'].readline().decode()
    context['request']['body']['raw'] = data

    # TODO: Headers as list of tuples etc. everywhere
    # Headers
    context.parsed_request_header({})
    context.parsed_response_header({})
    for k, v in env.items():
        if k.startswith('HTTP_'):
            context.parsed_request_header()[k.replace('HTTP_', '').replace('_', '-')] = v
    context.parsed_request_header()['gaukl_method'] = env['REQUEST_METHOD']

    context.parsed_request_header()['gaukl_method_path'] = f'{env["PATH_INFO"]}' \
                                                           f'{env["QUERY_STRING"] if env["QUERY_STRING"] else ""} ' \
                                                           f'{env["SERVER_PROTOCOL"]}'
    return context


def http_on(env: Dict, start_response: Callable[[str, List], Any]) -> List[bytes]:
    context = handle_req(env['context'], env)
    # Set default headers
    if 'gaukl_status' not in context.parsed_response_header():
        context.parsed_response_header()['gaukl_status'] = '200 OK'
    resp_headers = []
    for k, v in context.parsed_response_header().items():
        if not k.startswith('gaukl'):
            resp_headers.append((str(k), str(v)))
    start_response(context.parsed_response_header()['gaukl_status'], resp_headers)

    return [bytes(context.raw_response_body() or '', 'UTF-8')]


@task(shortname='http_forwarder', role=Roles.WORKFLOW, async=False)
def forwarder(context: Context, only_not_matched: bool = True, url: str = None, request_parser: str = None, response_parser: str = None) -> Context:
    # TODO: Not flexible enough. @forward annotation to handle parsers?
    if only_not_matched and context.is_matched():
        return context
    context = context['environment']['tasks'][request_parser](context)

    headers = {k: v for k, v in context.parsed_request_header().items() if k not in ['gaukl_method', 'gaukl_method_path', 'HOST', 'gaukl_status']}
    req = Request(context.parsed_request_header()['gaukl_method'], url, data=context.raw_request_body(), headers=headers).prepare()
    resp = Session().send(req)
    
    context.parsed_response_header({})
    for k, v in resp.headers.items():
        context.parsed_response_header()[k] = v
    
    context.parsed_response_header()['gaukl_status'] = str(resp.status_code)
    context.raw_response_body(resp.text)
    
    return context['environment']['tasks'][response_parser](context)


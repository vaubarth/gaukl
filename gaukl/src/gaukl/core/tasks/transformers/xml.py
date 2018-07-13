import xmltodict

from gaukl.core.context.context import Context
from gaukl.core.tasks.task import task, Roles


# TODO: Prettier handling of namespaces

@task(shortname='request_from_xml', role=Roles.TRANSFORMATION, async=False)
def request_from_xml(context: Context) -> Context:
    context.parsed_request_body(xmltodict.parse(context.raw_request_body(), process_namespaces=True))
    return context


@task(shortname='request_to_xml', role=Roles.TRANSFORMATION, async=False)
def request_to_xml(context: Context) -> Context:
    context.raw_request_body(xmltodict.unparse(context.parsed_request_body(), pretty=True))
    return context


@task(shortname='response_to_xml', role=Roles.TRANSFORMATION, async=False)
def response_to_xml(context: Context) -> Context:
    context.raw_response_body(xmltodict.unparse(context.parsed_response_body(), pretty=True))
    return context


@task(shortname='response_from_xml', role=Roles.TRANSFORMATION, async=False)
def response_from_xml(context: Context) -> Context:
    context.parsed_response_body(xmltodict.parse(context.raw_response_body(), process_namespaces=True))
    return context

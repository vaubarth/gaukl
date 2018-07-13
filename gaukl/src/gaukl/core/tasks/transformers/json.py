import json

from gaukl.core.context.context import Context
from gaukl.core.tasks.task import task, Roles


@task(shortname='request_from_json', role=Roles.TRANSFORMATION, async=False)
def request_from_json(context: Context) -> Context:
    context.parsed_request_body(json.loads(context.raw_request_body()))
    return context


@task(shortname='request_to_json', role=Roles.TRANSFORMATION, async=False)
def request_to_json(context: Context) -> Context:
    context.raw_request_body(json.dumps(context.parsed_request_body()))
    return context


@task(shortname='response_from_json', role=Roles.TRANSFORMATION, async=False)
def response_from_json(context: Context) -> Context:
    context.parsed_response_body(json.loads(context.raw_response_body()))
    return context


@task(shortname='response_to_json', role=Roles.TRANSFORMATION, async=False)
def response_to_json(context: Context) -> Context:
    context.raw_response_body(json.dumps(context.parsed_response_body()))
    return context



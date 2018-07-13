import dpath
import requests

from gaukl.core.context.context import Context
from gaukl.core.tasks.task import task, Roles
from gaukl.core.store import kvstore


@task(shortname='set_value', role=Roles.MANIPULATION, async=False)
def set_value(context: Context, selector: str, set_to: object) -> Context:
    dpath.set(context, selector, set_to, separator='.')
    return context


@task(shortname='set_variable', role=Roles.MANIPULATION, async=False)
def set_variable(context: Context, name: str, set_to: object) -> Context:
    kvstore.insert(context, name, set_to)
    return context


@task(shortname='set_global_variable', role=Roles.MANIPULATION, async=False)
def set_global_variable(context: Context, name: str, set_to: object) -> Context:
    requests.post(f'{context["environment"]["config"]["internal"]["juggler"]["path"]}/api/vars',
                  json={'key': name, 'value': set_to})
    return context

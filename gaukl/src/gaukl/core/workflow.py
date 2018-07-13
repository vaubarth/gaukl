from collections import OrderedDict
from typing import Optional, Dict, List

import yaml
from gaukl.core.context.context import Context
from gaukl.core.store.varfilters import GetVarExtension
from gevent.threading import Thread
from jinja2 import Environment, FunctionLoader, FileSystemLoader
from yaml import resolver


def _get_rendered_value(value, context: Context):
    env = Environment(loader=FunctionLoader(lambda x: x), extensions=[GetVarExtension])
    env.context = context
    try:
        return env.get_template(value).render()
    except:
        return value


def _execute_task(context: Context, task: dict) -> Context:
    expanded_args = {key: _get_rendered_value(value, context) for key, value in task['options'].items()}

    if task['function'].async:
        task_thread = Thread(group=None, target=task['function'], args=[context], kwargs=expanded_args)
        task_thread.start()
    else:
        context = task['function'](context, **expanded_args)
    return context


def load_yaml_tpl(search_path: str, file_name: str, context: Optional[Context]) -> Dict:
    """Loads a given file, expands it if it contains template elements.
    The expanded content is then loaded in an OrderedDict and returned.
    """
    yaml.add_constructor(resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                         lambda loader, node: OrderedDict(loader.construct_pairs(node)))
    expanded = Environment(loader=FileSystemLoader(search_path)).get_template(file_name).render({'context': context})
    return yaml.load(expanded)


def get_callable(action: dict, task_map: dict) -> dict:
    if isinstance(action, dict):
        key, args = list(action.items())[0]
        func_dict = {'function': task_map[key], 'options': args}
    else:
        func_dict = {'function': task_map[action], 'options': {}}
    return func_dict


def build_workflow(workflow: list, task_map: dict) -> list:
    """Builds a wofkflow - a list of dicts in the form of {'function': callable, 'options': arguments for the callable}
    :param workflow: ex. [{'http_listener': {'port': 8080}}]
    :param task_map: ex. {'http_listener': {'package': 'gaukl.core.tasks.listeners.http', 'function': 'listener'}}
    :return: final workflow
    """
    return [get_callable(action, task_map) for action in workflow]


def execute_workflow(context: Context, workflow: List[dict]) -> Context:
    """Execute all functions in a given workflow with context, workflows are a list of dicts:
    {'function': the function, 'options': the kwargs of the function}
    Needs to be called on every request from a client against any simulation.
    """
    for task in workflow:
        context = _execute_task(context, task)
    return context

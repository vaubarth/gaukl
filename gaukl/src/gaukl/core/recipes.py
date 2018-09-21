import importlib
import logging
import os

from gaukl.core.context.context import get_default_context
from gaukl.core.store import eventstore, kvstore
from gaukl.core.tasks.listener import _listener
from gaukl.core.tasks.task import _tasks
from gaukl.core.workflow import get_callable, load_yaml_tpl


def run_recipe(config: dict, recipe_file_name: str) -> None:
    """Loads the recipe with which gaukl is started. This is the entry point for everything.
    Starts the listener as defined in the recipe as well as the internal API.
    Also constructs the environment which defines relevant extensions etc. as defined in the config.
    """
    recipe = load_yaml_tpl(config['paths']['recipes_path'], recipe_file_name, None)

    config['active_recipe'] = recipe_file_name

    logging.basicConfig(level=config['internal']['logging']['log_level'],
                        format=config['internal']['logging']['log_format'])
    logger = logging.getLogger('gaukl.global')

    # Import all tasks, functions and listeners
    [[importlib.import_module(ext) for ext in config[entry]] for entry in ['extensions', 'listeners']]

    # Build all workflows
    build = lambda tasks: {reg.shortname or reg.__module__ + '.' + reg.__name__: reg for reg in tasks}
    task_map = build(_tasks)
    listener = build(_listener)

    context = get_default_context({
        'tasks': task_map,
        'recipe': recipe,
        'config': config,
        'environ': os.environ
    })

    # Clear the databases
    eventstore.purge(context)
    kvstore.purge(context)

    # Start the listener
    call = get_callable(recipe['listen'], listener)
    logger.info(f'Started listener for recipe {recipe}')
    call['function'](context, **call['options'])

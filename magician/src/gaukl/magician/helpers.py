import importlib
import hashlib
import inspect
from pathlib import Path

from gaukl.core.tasks.task import _tasks
from gaukl.core.helper.files import load_yaml_path


def get_snippets(config_path: Path, for_roles: list) -> list:
    config = load_yaml_path(config_path)
    [importlib.import_module(ext) for ext in config['extensions']]

    task_map = {reg.shortname: list(filter(lambda x: x != 'context', inspect.signature(reg).parameters.keys()))
                for reg in _tasks if reg.role.name in for_roles}

    snippets = []
    for task, params in task_map.items():
        snippets.append(f'snippet {task}\n\t{task}')
        if params:
            for i, k in enumerate(params):
                snippets.append('\n\t\t%s: ${%i:%s}' % (k, i, k))
        snippets.append('\n')

    return snippets


def get_recipes(path: Path) -> dict:
    config = load_yaml_path(path)
    recipes = path.parent.joinpath(config['paths']['recipes_path']).glob('*.yaml')

    return {
        'configdir': str(path.resolve()),
        'recipes': [{'name': str(recipe.name),
                     'path': str(recipe.parent),
                     'id': hashlib.sha224(bytes(str(recipe), 'utf-8')).hexdigest()}
                    for recipe in recipes]
    }


def get_file_for_type(config_path, filetype, filename):
    if filetype == 'config':
        file = config_path
    else:
        config = load_yaml_path(config_path)
        file = config_path.parent.joinpath(config['paths'][f'{filetype}s_path'], filename)
    return file

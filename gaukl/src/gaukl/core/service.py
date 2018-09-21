import argparse
import logging
import multiprocessing as mp
from pathlib import Path

import requests
from gaukl.core.api.web import api
from gaukl.core.context.context import get_default_context
from gaukl.core.recipes import run_recipe
from gaukl.core.workflow import load_yaml_tpl


def run_gaukl(config_file_path: str) -> None:
    path = Path(config_file_path)
    config = load_yaml_tpl(str(path.parent), str(path.name), None)

    for sub_path in ['recipes_path', 'rulesets_path', 'responses_path']:
        if not Path(config['paths'][sub_path]).is_absolute():
            config['paths'][sub_path] = str(path.parent.joinpath(config['paths'][sub_path]).resolve())

    recipes = path.parent.joinpath(config['paths']['recipes_path']).glob('*.yaml')

    logging.basicConfig(level=config['internal']['logging']['log_level'],
                        format=config['internal']['logging']['log_format'])
    logger = logging.getLogger('gaukl.global')

    listener_processes = {}
    recipe_names = []

    for recipe in recipes:
        listener_process = mp.Process(group=None, target=run_recipe, args=[config, recipe.name])
        listener_process.start()
        logger.info(f'Loading recipe {recipe.name}')
        recipe_names.append(recipe.name)
        listener_processes[recipe.name] = listener_process.pid

    # Register with juggler
    if config['internal']['juggler']['enabled']:
        requests.put(f'http://{config["internal"]["juggler"]["path"]}/api/services',
                     json={'host': '', 'port': config['internal']['api']['server.socket_port']})

    # Start internal REST API
    logger.info('Starting API')
    api.run(get_default_context({'config': config}), recipe_names, listener_processes)


if __name__ == '__main__':
    mp.freeze_support()
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file_path", help="Path to the config file, ex. ./examples/config.yaml")
    args = parser.parse_args()

    run_gaukl(args.config_file_path)

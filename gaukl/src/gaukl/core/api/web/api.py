import signal
import os
from multiprocessing import Process
from collections import OrderedDict
from pathlib import Path

from flask import Flask, jsonify, request, abort

from gaukl.core.store import eventstore, kvstore
from gaukl.core.helper.files import load_yaml_path
from gaukl.core.context.context import Context
from gaukl.core.recipes import run_recipe

app = Flask(__name__)


def run(context: Context, recipes: list, listener_processes: dict):
    app.config['recipes'] = recipes
    app.config['listener_processes'] = listener_processes
    app.config['context'] = context
    app.run(port=app.config['context']['environment']['config']['internal']['api']['server.socket_port'])


@app.route('/api/recipe/<recipe>/state', methods=['GET'])
def get_state(recipe: str):
    if recipe not in app.config['recipes']:
        abort(404)

    if recipe in app.config['listener_processes']:
        state = 'running'
    else:
        state = 'stopped'
    return jsonify({'recipe': recipe, 'state': state})


@app.route('/api/recipe/<recipe>/state/shutdown', methods=['POST'])
def stop_recipe(recipe):
    if recipe not in app.config['recipes']:
        abort(404)
    try:
        pid = app.config['listener_processes'][recipe]
    except KeyError:
        return jsonify({'recipe': recipe, 'state': 'stopped'})

    os.kill(pid, signal.SIGTERM)
    app.config['listener_processes'].pop(recipe)
    return jsonify({'recipe': recipe, 'state': 'stopped'})


@app.route('/api/recipe/<recipe>/state/start', methods=['POST'])
def start_recipe(recipe):
    if recipe not in app.config['recipes']:
        abort(404)
    listener_process = Process(group=None, target=run_recipe,
                               args=[app.config['context']['environment']['config'], recipe])
    listener_process.start()
    app.config['listener_processes'][recipe] = listener_process.pid
    return jsonify({'recipe': recipe, 'state': 'started'})


@app.route('/api/recipe/<recipe>', methods=['GET'])
def get_recipe(recipe):
    config = app.config['context']['environment']['config']
    try:
        recipe = load_yaml_path(Path(config['paths']['recipes_path']).joinpath(recipe))
    except FileNotFoundError:
        abort(404)
    expanded_rulesets = OrderedDict()  # type: OrderedDict

    for ruleset_file in recipe['rulesets']:
        ruleset = load_yaml_path(Path(config['paths']['rulesets_path']).joinpath(ruleset_file))
        response = load_yaml_path(Path(config['paths']['responses_path']).joinpath(ruleset['use']))

        ruleset['use'] = {ruleset['use']: response}
        expanded_rulesets[ruleset_file] = ruleset

    recipe['rulesets'] = expanded_rulesets
    return jsonify(recipe)


@app.route('/api/event/<event>', methods=['GET'])
def get_events(event: str):
    return jsonify(eventstore.count(app.config['context'], event))


@app.route('/api/var/<key>', methods=['GET'])
def get_variables(key: str):
    result = kvstore.select(app.config['context'], key)
    return jsonify({'value': result['value'], 'key': result['key']})


@app.route('/api/vars/<key>', methods=['POST'])
def post_variables(key: str):
    value = request.json['value']
    kvstore.insert(app.config['context'], key, value)
    return jsonify({'success': True})

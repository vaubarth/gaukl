import argparse
from pathlib import Path

import requests
from flask import request, jsonify, Flask

from gaukl.core.helper.files import load_yaml_path
from gaukl.core.context.context import get_default_context
import gaukl.resources
from gaukl.core.store import kvstore

app = Flask(__name__, static_folder=str(Path(gaukl.resources.__file__).parent.joinpath('resources/static').resolve()))


def run(juggler_config):
    app.config['services'] = set()
    app.config['juggler'] = juggler_config
    app.config['base_path'] = Path(gaukl.resources.__file__).parent.resolve()
    app.use_reloader = False
    app.debug = False
    app.run(port=juggler_config['api']['port'])


def get_config_context():
    return get_default_context({'config': {'internal': {'vardb_path': app.config['juggler']['vardb_path']}}})


@app.route('/', methods=['GET'])
def get_index():
    return app.config['base_path'].joinpath('resources/html/juggler/juggler.html').read_text()


@app.route('/api/state', methods=['GET'])
def get_state():
    service = request.args.get('services')
    try:
        r = requests.get('http://' + service + '/api/state').json()
    except Exception:
        r = {'state': 'down'}

    return jsonify({'service': service, 'response': r})


@app.route('/api/state', methods=['POST'])
def change_service_state():
    services = app.config['services']
    data = request.json
    responses = []
    if data['services'] == '*':
        to_shutdown = services
    else:
        to_shutdown = data['services']

    for service in to_shutdown:
        try:
            r = requests.post('http://' + service + '/api/state').json()
        except Exception:
            r = None
        responses.append({'service': service, 'response': r})

    return jsonify(responses)


@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    service = request.args.get('services')
    try:
        r = requests.get('http://' + service + '/api/recipe').json()
    except Exception:
        r = None

    return jsonify({'service': service, 'response': r})


@app.route('/api/services', methods=['GET'])
def get_services():
    return jsonify(list(app.config['services']))


@app.route('/api/services', methods=['PUT'])
def register_service():
    data = request.json
    host = data['host'] if data['host'] else request.remote_addr
    app.config['services'].add(host+':'+str(data['port']))
    return jsonify(list(app.config['services']))


@app.route('/api/vars', methods=['GET'])
def get_variables():
    result = kvstore.select(get_config_context(), request.args.get('key'))
    return jsonify({'value': result['value'], 'key': result['key']})


@app.route('/api/vars', methods=['POST'])
def post_variables():
    data = request.json
    kvstore.insert(get_config_context(), data['key'], data['value'])
    return jsonify({'success': True})


@app.route('/api/events', methods=['GET'])
def get_events():
    service = request.args.get('services')
    try:
        r = requests.get('http://' + service + '/api/events?event=' + request.args.get('event')).json()
    except Exception:
        r = None
    return jsonify({'service': service, 'response': r})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file_path", help="Path to the config file, ex. ./examples/config.yaml")
    args = parser.parse_args()

    config = load_yaml_path(Path(args.config_file_path))

    kvstore.purge(get_default_context({'config': {'internal': {'vardb_path': config['vardb_path']}}}))
    gaukl.juggler.api.run(config)

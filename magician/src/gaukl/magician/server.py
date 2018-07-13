import argparse
import hashlib
import importlib
import logging
import secrets
from collections import OrderedDict
from pathlib import Path

import yaml
from flask import jsonify, Flask, request, session, redirect, url_for, render_template
from upersetter.make import SetUp

import gaukl.resources
from gaukl.core.context.context import get_default_context
from gaukl.magician import helpers
from gaukl.core.helper.files import load_yaml_path


# noinspection PyUnresolvedReferences
resources_path = Path(gaukl.resources.__file__).parent.resolve()

app = Flask(__name__, static_folder=str(resources_path.joinpath('static').resolve()), template_folder=resources_path.joinpath('html','magician','templates'))
app.secret_key = secrets.token_urlsafe()

app.config['base_path'] = resources_path
app.config['user_token'] = secrets.token_urlsafe()


def check_auth():
    if app.config['unsafe']:
        return
    if (request.path.startswith('/static') or request.path == '/auth'):
        return
    if session.get('user_token', None) != app.config['user_token']:
        return render_template('auth.html')


app.before_request(check_auth)


# Start the server
def run(config_path: str, host: str, port: int, unsafe: bool):
    decor = f'{"*"*50}\n{"*"*50}'
    print(f'\n{decor}')
    print(f'Your user token is:\n{app.config["user_token"]}')
    print(f'{decor}\n')

    if config_path is not None:
        config_path = Path(config_path)
    app.config['unsafe'] = unsafe
    app.config['config_path'] = config_path
    app.run(host=host, port=port)


@app.route('/', methods=['GET'])
def get_editor():
    return render_template('main.html')


@app.route('/auth', methods=['POST'])
def authenticate():
    if request.form.get('usertoken') == app.config['user_token']:
        session['user_token'] = app.config['user_token']
    return redirect(url_for('get_editor'))


# Snippets
@app.route('/api/snippets/<roles>', methods=['GET'])
def get_tasks(roles: str):
    snippets = helpers.get_snippets(app.config['config_path'], roles.split(','))
    return jsonify({'snippets': ''.join(snippets)})


# Files/Content
@app.route('/api/<filetype>/<file>', methods=['GET'])
def get_content(filetype: str, file: str) -> dict:
    file = helpers.get_file_for_type(app.config['config_path'], filetype, file)
    return jsonify({'content': file.read_text()})


@app.route('/api/<filetype>/<file>', methods=['POST'])
def save_content(filetype: str, file: str):
    data = request.json
    helpers.get_file_for_type(app.config['config_path'], filetype, file).write_text(data['content'])
    return jsonify({})


# Recipes
@app.route('/api/recipes', methods=['GET'])
def load_recipes() -> dict:
    return jsonify(helpers.get_recipes(app.config['config_path']))


@app.route('/api/recipes/<recipe>', methods=['GET'])
def get_recipe(recipe: str) -> dict:
    config = load_yaml_path(app.config['config_path'])
    recipe = load_yaml_path(app.config['config_path'].parent.joinpath(
        config['paths']['recipes_path'], recipe)
    )
    expanded_rulesets = []
    responses = []

    for ruleset_file in recipe['rulesets']:
        ruleset = load_yaml_path(app.config['config_path'].parent.joinpath(
            config['paths']['rulesets_path'], ruleset_file)
        )
        response_path = app.config['config_path'].parent.joinpath(config['paths']['responses_path'], ruleset['use'])
        response = load_yaml_path(response_path)

        response_restr = {
            'path': ruleset['use'],
            'id': hashlib.sha224(bytes(str(response_path.resolve()), 'utf-8')).hexdigest(),
            'name': ruleset['use'],
            'content': response
        }

        ruleset['path'] = ruleset_file
        ruleset['id'] = hashlib.sha224(bytes(ruleset['path'], 'utf-8')).hexdigest()
        ruleset['name'] = ruleset_file
        ruleset['use'] = response_restr

        if response_restr not in responses:
            responses.append(response_restr)
        expanded_rulesets.append(ruleset)

    recipe['rulesets'] = expanded_rulesets
    recipe['responses'] = responses
    return jsonify(recipe)

# Config
@app.route('/api/config', methods=['GET'])
def get_config() -> dict:
    if app.config['config_path'] is not None:
        response = jsonify({
            'error': False,
            'path': str(app.config['config_path'].resolve()),
            'config': load_yaml_path(app.config['config_path'])
        })
    else:
        response = jsonify({'error': True})
    return response


@app.route('/api/config', methods=['POST'])
def set_config():
    path = Path(request.json['path'])
    helpers.get_recipes(path)
    app.config['config_path'] = Path(path)
    return jsonify({})


# Project
@app.route('/api/project/create', methods=['POST'])
def create_project() -> dict:
    template_path = app.config['base_path'].joinpath('project_setup')

    options = load_yaml_path(Path(template_path).joinpath('options.yaml'))
    options['project']['name'] = request.json['name']

    outdir = Path(request.json['path']).resolve()
    print(outdir)

    SetUp(options=options,
          structure=str(Path(template_path).joinpath('structure.yaml')),
          templates=str(Path(template_path).joinpath('templates')),
          metadata=str(Path(template_path).joinpath('metadata.yaml')),
          out_dir=outdir,
          unsafe=False).setup()
    # TODO: Override project name 'new_project' <- read options.yaml and make dict to override
    file_path = outdir.joinpath(options['project']['name'], 'config.yaml').resolve()
    app.config['config_path'] = file_path
    return jsonify(helpers.get_recipes(file_path))


@app.route('/api/listfolder', methods=['GET'])
def list_folder():
    path = Path(request.args.get('path'))
    return jsonify({
        'entries': [{
            'name': p.name,
            'path': str(p.resolve()),
            'file': p.is_file(),
            'dir': p.is_dir()
        } for p in path.iterdir()],
        'parent': {
            'path': str(path.resolve().parent.resolve()),
            'dir': True
        },
        'path': {
            'path': str(path.resolve()),
            'dir': True
        }
    })


@app.route('/api/transform', methods=['POST'])
def transform() -> dict:
    ctx = get_default_context({})
    ctx['response']['body']['raw'] = request.json['text']

    split = request.json['transformer'].split('.')
    mod = importlib.import_module('.'.join(split[:len(split) - 1]))
    fun = getattr(mod, split[len(split) - 1:len(split)][0])
    ctx = fun(ctx)

    yaml.add_representer(OrderedDict, lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items()))
    return jsonify({'text': yaml.dump(ctx['response']['body']['parsed'], default_flow_style=False)})


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', '-c', help='Path to the config file', default=None)
    parser.add_argument('--host', help='For which host to listen', default='localhost')
    parser.add_argument('--port', help='On which port to listen', default=5000)
    parser.add_argument('--unsafe', help='This option sets magician to unsafe mode.', action='store_true')
    args = parser.parse_args()

    logger.debug('Starting server')
    run(args.config, args.host, args.port, args.unsafe)

import unittest
from collections import OrderedDict
from pathlib import Path

from gaukl.core.context.context import get_default_context
from gaukl.core.workflow import load_yaml_tpl, build_workflow


class TestWorkflow(unittest.TestCase):
    def test_build_workflow_simple(self):
        expected = [
            {'function': {'function': 'request_parse', 'package': 'gaukl.core.tasks.transformers.json'}, 'options': {}},
            {'function': {'function': 'request_parse', 'package': 'gaukl.core.tasks.transformers.xml'}, 'options': {}},
        ]

        tasks = ['request_from_json', 'request_from_xml']
        task_map = {
            'request_from_json': {'package': 'gaukl.core.tasks.transformers.json', 'function': 'request_parse'},
            'request_from_xml': {'package': 'gaukl.core.tasks.transformers.xml', 'function': 'request_parse'},
        }

        workflow = build_workflow(tasks, task_map)
        self.assertEqual(expected, workflow)

    def test_build_workflow_kwargs(self):
        expected = [{'function': {'package': 'gaukl.core.tasks.listeners.http', 'function': 'listener'},
                     'options': {'port': 8080}},
                    {'function': {'package': 'gaukl.core.tasks.transformers.json', 'function': 'request_parse'},
                     'options': {}}]

        tasks = [{'http_listener': {'port': 8080}}, 'request_from_json']
        task_map = {
            'http_listener': {'package': 'gaukl.core.tasks.listeners.http', 'function': 'listener'},
            'request_from_json': {'package': 'gaukl.core.tasks.transformers.json', 'function': 'request_parse'}
        }

        workflow = build_workflow(tasks, task_map)
        self.assertEqual(expected, workflow)


class TestLoadYaml(unittest.TestCase):
    def test_load(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = 'parsed'
        search_path = str(Path('resources').resolve())
        file_name = 'template.yaml'

        expected = {'expand': 'parsed', 'key': 'value', 'list': ['test']}
        expanded = load_yaml_tpl(search_path, file_name, context)
        self.assertDictEqual(expected, expanded)

    def test_ordered(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = 'parsed'
        search_path = str(Path('resources').resolve())
        file_name = 'template.yaml'

        expected = OrderedDict([('key', 'value'), ('list', ['test']), ('expand', 'parsed')])
        expanded = load_yaml_tpl(search_path, file_name, context)
        self.assertEqual(expected, expanded)

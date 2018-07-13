import unittest

from gaukl.core.context.context import get_default_context
from gaukl.core.tasks.transformers.json import request_from_json, response_to_json, request_to_json, response_from_json


class TestParsingJsonRequest(unittest.TestCase):
    def test_parse(self):
        context = get_default_context({})
        context['request']['body']['raw'] = '{"key": "value"}'
        self.assertEqual({'key': 'value'}, request_from_json(context)['request']['body']['parsed'])

    def test_unparse(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'key': 'value'}
        self.assertEqual('{"key": "value"}', request_to_json(context)['request']['body']['raw'])


class TestUnParsingJsonResponse(unittest.TestCase):
    def test_parse(self):
        context = get_default_context({})
        context['response']['body']['raw'] = '{"key": "value"}'
        self.assertEqual({'key': 'value'}, response_from_json(context)['response']['body']['parsed'])

    def test_unparse(self):
        context = get_default_context({})
        context['response']['body']['parsed'] = {'key': 'value'}
        self.assertEqual('{"key": "value"}', response_to_json(context)['response']['body']['raw'])

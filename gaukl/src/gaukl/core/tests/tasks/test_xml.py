import unittest

from gaukl.core.context.context import get_default_context
from gaukl.core.tasks.transformers.xml import response_to_xml, request_from_xml, request_to_xml, response_from_xml


class TestParsingXmlRequest(unittest.TestCase):
    def test_parse(self):
        context = get_default_context({})
        context['request']['body']['raw'] = '<key>value</key>'
        self.assertEqual({'key': 'value'}, request_from_xml(context)['request']['body']['parsed'])

    def test_unparse(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'key': 'value'}
        self.assertEqual('<?xml version="1.0" encoding="utf-8"?>\n<key>value</key>',
                         request_to_xml(context)['request']['body']['raw'])


class TestUnParsingXmlResponse(unittest.TestCase):
    def test_parse(self):
        context = get_default_context({})
        context['response']['body']['raw'] = '<key>value</key>'
        self.assertEqual({'key': 'value'}, response_from_xml(context)['response']['body']['parsed'])

    def test_unparse(self):
        context = get_default_context({})
        context['response']['body']['parsed'] = {'key': 'value'}
        self.assertEqual('<?xml version="1.0" encoding="utf-8"?>\n<key>value</key>',
                         response_to_xml(context)['response']['body']['raw'])

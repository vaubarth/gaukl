import unittest

from gaukl.core.context.context import get_default_context
from gaukl.core.functions.manipulations import set_value


class TestSetValue(unittest.TestCase):
    def test_set(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 'value'}}

        context_exp = get_default_context({})
        context_exp['request']['body']['parsed'] = {'dict': {'key': 'anothervalue'}}

        selector = 'request.body.parsed.dict.key'
        set_to = 'anothervalue'

        self.assertEqual(context_exp, set_value(context, selector=selector, set_to=set_to))

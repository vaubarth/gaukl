import unittest

from gaukl.core.context.context import get_default_context
from gaukl.core.functions.tests import compare, is_numeric, matches_regex, starts_with


class TestIsEqual(unittest.TestCase):
    def test_equal(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 'value'}}

        selector = 'request.body.parsed.dict.key'
        compare_to = 'value'

        self.assertEqual(context, compare(context, selector=selector, comparator='==', compare_to=compare_to))

    def test_equal_list(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': [1, 2]}}

        selector = 'request.body.parsed.dict.key'
        compare_to = [1, 2]

        self.assertEqual(context, compare(context, selector=selector, comparator='==', compare_to=compare_to))

    def test_not_equal(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 'value'}}

        selector = 'request.body.parsed.dict.key'
        compare_to = '!value'

        self.assertRaises(AssertionError, compare, context, selector=selector, comparator='==', compare_to=compare_to)


class TestIsGreater(unittest.TestCase):
    def test_greater(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 2}}

        selector = 'request.body.parsed.dict.key'
        compare_to = 1

        self.assertEqual(context, compare(context, selector=selector, comparator='>', compare_to=compare_to))

    def test_smaller(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 2}}

        selector = 'request.body.parsed.dict.key'
        compare_to = 3

        self.assertRaises(AssertionError, compare, context, selector=selector, comparator='>', compare_to=compare_to)


class TestIsSmaller(unittest.TestCase):
    def test_smaller(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 1}}

        selector = 'request.body.parsed.dict.key'
        compare_to = 2

        self.assertEqual(context, compare(context, selector=selector, comparator='<', compare_to=compare_to))

    def test_greater(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 2}}

        selector = 'request.body.parsed.dict.key'
        compare_to = 1

        self.assertRaises(AssertionError, compare, context, selector=selector, comparator='<', compare_to=compare_to)


class TestIsSmallerOrEqual(unittest.TestCase):
    def test_smaller(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 1}}

        selector = 'request.body.parsed.dict.key'
        compare_to = 2

        self.assertEqual(context, compare(context, selector=selector, comparator='<=', compare_to=compare_to))

    def test_equal(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 2}}

        selector = 'request.body.parsed.dict.key'
        compare_to = 2

        self.assertEqual(context, compare(context, selector=selector, comparator='<=', compare_to=compare_to))

    def test_greater(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 2}}

        selector = 'request.body.parsed.dict.key'
        compare_to = 1

        self.assertRaises(AssertionError, compare, context, selector=selector, comparator='<=', compare_to=compare_to)


class TestIsGreaterOrEqual(unittest.TestCase):
    def test_greater(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 2}}

        selector = 'request.body.parsed.dict.key'
        compare_to = 1

        self.assertEqual(context, compare(context, selector=selector, comparator='>=', compare_to=compare_to))

    def test_equal(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 2}}

        selector = 'request.body.parsed.dict.key'
        compare_to = 2

        self.assertEqual(context, compare(context, selector=selector, comparator='>=', compare_to=compare_to))

    def test_smaller(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 1}}

        selector = 'request.body.parsed.dict.key'
        compare_to = 2

        self.assertRaises(AssertionError, compare, context, selector=selector, comparator='>=', compare_to=compare_to)


class TestIsNumeric(unittest.TestCase):
    def test_int(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 2}}

        selector = 'request.body.parsed.dict.key'

        self.assertEqual(context, is_numeric(context, selector=selector))

    def test_float(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 2.1}}

        selector = 'request.body.parsed.dict.key'

        self.assertEqual(context, is_numeric(context, selector=selector))

    def test_leading_zero(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': '02'}}

        selector = 'request.body.parsed.dict.key'

        self.assertEqual(context, is_numeric(context, selector=selector))

    def test_string(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 'a'}}

        selector = 'request.body.parsed.dict.key'

        self.assertRaises(ValueError, is_numeric, context, selector=selector)


class TestMatchesRegex(unittest.TestCase):
    def test_match(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 'AString'}}

        selector = 'request.body.parsed.dict.key'
        pattern = '.Str.*'

        self.assertEqual(context, matches_regex(context, selector=selector, pattern=pattern))

    def test_no_match(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 'AString'}}

        selector = 'request.body.parsed.dict.key'
        pattern = 'Foo.*'

        self.assertRaises(AssertionError, matches_regex, context, selector=selector, pattern=pattern)


class TestStartsWith(unittest.TestCase):
    def test_match(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 'StartEnd'}}

        selector = 'request.body.parsed.dict.key'
        start = 'Start'

        self.assertEqual(context, starts_with(context, selector=selector, start=start))

    def test_no_match(self):
        context = get_default_context({})
        context['request']['body']['parsed'] = {'dict': {'key': 'StartEnd'}}

        selector = 'request.body.parsed.dict.key'
        start = 'End'

        self.assertRaises(AssertionError, starts_with, context, selector=selector, start=start)

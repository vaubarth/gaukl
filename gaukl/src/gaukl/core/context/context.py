from typing import Dict


class Context(dict):

    # Shortcut getter
    def parsed_request_body(self, value=None):
        if value:
            self['request']['body']['parsed'] = value
        return self['request']['body']['parsed']

    def parsed_request_header(self, value=None):
        if value:
            self['request']['header']['parsed'] = value
        return self['request']['header']['parsed']

    def parsed_response_body(self, value=None):
        if value:
            self['response']['body']['parsed'] = value
        return self['response']['body']['parsed']

    def parsed_response_header(self, value=None):
        if value:
            self['response']['header']['parsed'] = value
        return self['response']['header']['parsed']

    def raw_request_body(self, value=None):
        if value:
            self['request']['body']['raw'] = value
        return self['request']['body']['raw']

    def raw_request_header(self, value=None):
        if value:
            self['request']['header']['raw'] = value
        return self['request']['header']['raw']

    def raw_response_body(self, value=None):
        if value:
            self['response']['body']['raw'] = value
        return self['response']['body']['raw']

    def raw_response_header(self, value=None):
        if value:
            self['response']['header']['raw'] = value
        return self['response']['header']['raw']

    def is_matched(self, value=None):
        if value:
            self['is_matched'] = value
        return self['is_matched']


def reset_context(context: Context) -> Context:
    context['request'] = {
        'header': {
            'raw': None,
            'parsed': {},
        },
        'body': {
            'raw': None,
            'parsed': {},
        }
    }
    context['response'] = {
        'header': {
            'raw': None,
            'parsed': {},
        },
        'body': {
            'raw': None,
            'parsed': {},
        }
    }
    context['is_matched'] = False
    return context


def get_default_context(environment: Dict) -> Context:
    return reset_context(Context({
        'environment': environment
    }))

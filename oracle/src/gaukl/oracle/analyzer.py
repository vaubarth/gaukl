from pprint import pprint
from typing import List, Dict, Any
from collections import MutableMapping, Iterable, Counter
from copy import deepcopy
from dateutil import parser as date_parser

import yaml


class DictAnalyzer:
    def __init__(self, *dicts: Dict):
        self.results = {}
        self.annotated_orig = {}
        self.dicts_count = len(dicts)
        for to_analyze in dicts:
            self.analyze(to_analyze, 'root')
            self.create_new(self.results, deepcopy(to_analyze))

    @staticmethod
    def is_datetime(v: Any) -> bool:
        # TODO: too broad?
        try:
            date_parser.parse(v)
            return True
        except(ValueError, AttributeError):
            return False

    @staticmethod
    def is_number(v) -> bool:
        try:
            float(v)
            return True
        except(ValueError, TypeError):
            return False

    @staticmethod
    def split_list(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def analyze(self, to_analyze: [Dict, MutableMapping], parent: str) -> None:
        for k, v in to_analyze.items():
            if isinstance(k, str):
                item_str = f"'{k}'"
            else:
                item_str = k
            self.typedef(v, f'{parent}[{item_str}]')

    def annotate(self, parent: str, v: Any, typ: Any, is_list: bool) -> None:
        if parent in self.results:
            self.results[parent]['values'].append(v)
            self.results[parent]['types'].append(typ)
        else:
            self.results[parent] = {'values': [v], 'types': [typ], 'is_list': is_list}

    def create_new(self, analyzed: Dict, orig: dict) -> None:
        root = orig
        for k, v in analyzed.items():
            res = {'type_count': Counter(v['types']), 'value_count': Counter(v['values']), 'values': v['values']}
            if v['is_list']:
                res['values'] = list(self.split_list(v['values'], len(v['values']) // self.dicts_count))
            exec(f'{k} = {res}')
        self.annotated_orig = root

    def typedef(self, v: Any, parent: str, is_list: bool = False) -> None:
        if self.is_number(v):
            self.annotate(parent, v, 'number', is_list)
        elif self.is_datetime(v):
            self.annotate(parent, v, 'datetime', is_list)
        elif isinstance(v, (str, bytes)):
            self.annotate(parent, v, 'string', is_list)
        elif isinstance(v, MutableMapping):
            self.analyze(v, parent)
        elif isinstance(v, Iterable):
            for lk in v:
                self.typedef(lk, parent, True)


if __name__ == '__main__':
    dd = {
        'foo': 'bar',
        'baz': {
            'a': 'Aug 28 1999 12:00AM',
            'c': {
                1: 2
            },
            'd': [1, 2, 3, 4, 5]
        }
    }
    dd2 = {
        'foo': 'bar',
        'baz': {
            'a': 'b',
            'c': {
                1: 'a'
            },
            'd': ['1', 2, 3, 4, 'a']
        }
    }
    dd3 = {
        'foo': 'bar',
        'baz': {
            'a': 'z',
            'c': {
                1: 'a'
            },
            'd': ['1', 2, 3, 4, 'a']
        }
    }

    analyzer = DictAnalyzer(dd, dd2, dd3)

    pprint(analyzer.results)
    print()
    yaml.add_representer(Counter, lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items()))
    y = yaml.dump(analyzer.annotated_orig, default_flow_style=False)
    print(y)

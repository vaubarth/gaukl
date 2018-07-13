import requests
from jinja2 import nodes
from jinja2.ext import Extension
from jinja2.nodes import Const

from gaukl.core.store import kvstore


class GetVarExtension(Extension):
    tags = set(['get_variable'])

    def __init__(self, environment):
        super(GetVarExtension, self).__init__(environment)
        environment.extend(context=None)

    def parse(self, parser):
        node = nodes.ExprStmt(lineno=next(parser.stream).lineno)
        node.node = parser.parse_tuple()
        res = kvstore.select(
            self.environment.context,
            node.node.value)['value']
        return nodes.Output([Const(res)])


class GetGlobalVarExtension(Extension):
    tags = set(['get_global_variable'])

    def __init__(self, environment):
        super(GetGlobalVarExtension, self).__init__(environment)
        environment.extend(context=None)

    def parse(self, parser):
        node = nodes.ExprStmt(lineno=next(parser.stream).lineno)
        node.node = parser.parse_tuple()
        res = requests.get(self.environment.context["environment"]["config"]["internal"]["juggler"]["path"] +
                           f'/api/vars?key={node.node.value}'
                           ).json()['value']
        return nodes.Output([Const(res)])

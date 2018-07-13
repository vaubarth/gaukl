import operator
import re

import dpath

from gaukl.core.context.context import Context
from gaukl.core.tasks.task import task, Roles


@task(shortname='compare', role=Roles.TEST, async=False)
def compare(context: Context, selector: str, comparator: str, compare_to: object) -> Context:
    comps = {
        '!=': operator.ne,
        '==': operator.eq,
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
    }
    assert comps[comparator](dpath.get(context, selector, separator='.'), compare_to)
    return context


@task(shortname='is_numeric', role=Roles.TEST, async=False)
def is_numeric(context: Context, selector: object) -> Context:
    float(dpath.get(context, selector, separator='.'))
    return context


@task(shortname='matches_regex', role=Roles.TEST, async=False)
def matches_regex(context: Context, selector: str, pattern: str) -> Context:
    assert re.fullmatch(pattern, dpath.get(context, selector, separator='.')) is not None
    return context


@task(shortname='starts_with', role=Roles.TEST, async=False)
def starts_with(context: Context, selector: str, start: str) -> Context:
    assert dpath.get(context, selector, separator='.').startswith(start) is True
    return context

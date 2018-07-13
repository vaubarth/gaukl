import copy
from enum import Enum
from functools import wraps

import logging
from typing import Callable, List, Dict

from gaukl.core.context.context import Context
from gaukl.core.helper.files import fqn
from gaukl.core.helper.logs import verbose_log

_tasks = []  # type: List[Callable]


def task(shortname=None, role=None, async=False):
    def task_decorator(func: Callable) -> Callable:
        # Register metadata
        func.async = async
        func.shortname = shortname
        func.role = role

        task_logger = logging.getLogger(fqn(func))

        @wraps(func)
        def func_wrapper(context: Context, **func_kwargs) -> Context:
            # Create a copy of the context
            context_copy = copy.deepcopy(context)
            # Log to db and console
            verbose_log(func, context_copy, func_kwargs)
            return func(context_copy, **func_kwargs)

        # Append to global task registry
        _tasks.append(func_wrapper)
        return func_wrapper

    return task_decorator

class Roles(Enum):
    WORKFLOW = 'workflow'
    GENERAL = 'general'
    MANIPULATION = 'manipulation'
    TEST = 'test'
    TRANSFORMATION = 'transformation'
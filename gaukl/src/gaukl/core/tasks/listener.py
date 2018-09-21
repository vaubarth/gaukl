import copy
from functools import wraps
import logging
from typing import Callable, Any, List

import gevent

from gaukl.core.workflow import execute_workflow, build_workflow
from gaukl.core.context.context import Context, reset_context
from gaukl.core.helper.files import fqn
from gaukl.core.store import eventstore

_listener = []  # type: List[Callable]


def listener(shortname=None):
    def listener_decorator(func: Callable) -> Callable:
        # Register metadata
        func.shortname = shortname

        @wraps(func)
        def func_wrapper(context: Context, **func_kwargs) -> None:
            func(context, **func_kwargs)

        # Append to global task registry
        _listener.append(func_wrapper)
        return func_wrapper

    return listener_decorator


def on_request():
    def on_request_decorator(func: Callable) -> Any:
        # Register metadata
        task_logger = logging.getLogger(fqn(func))

        @wraps(func)
        def func_wrapper(context: Context, *func_args, **func_kwargs) -> Context:
            # Create a copy of the context and reset request/response
            context_copy = reset_context(copy.deepcopy(context))

            # Log to db and console, do it in another greenthread since db access is expensive
            gevent.spawn(eventstore.insert, context_copy, 'request')
            context_copy = func(context_copy, *func_args, **func_kwargs)

            # Execute all tasks in thr given recipe workflow
            workflow = build_workflow(context_copy['environment']['recipe']['workflow'],
                                      context_copy['environment']['tasks'])
            return execute_workflow(context_copy, workflow)

        return func_wrapper

    return on_request_decorator

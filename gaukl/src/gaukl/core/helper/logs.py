import logging
import pprint
from contextlib import suppress

from gaukl.core.helper.files import fqn


def verbose_log(func, context_copy, func_kwargs):
    # Log context and kwargs
    func_logger = logging.getLogger(fqn(func))
    arguments = {'context': context_copy, 'func_kwargs': func_kwargs}
    with suppress(KeyError):
        # Log including linebreaks for easier debugging if it is enabled
        if context_copy['environment']['config']['internal']['logging']['pretty_print']:
            arguments = '\n' + pprint.pformat(arguments)
    func_logger.debug(f'Called {fqn(func)} with:{arguments}')
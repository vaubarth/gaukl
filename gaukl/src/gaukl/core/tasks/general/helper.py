import logging

from gaukl.core.context.context import Context
from gaukl.core.tasks.task import task, Roles


@task(shortname='log', role=Roles.GENERAL, async=False)
def log(context: Context, message: str = None, reason: str = None) -> Context:
    logger = logging.getLogger("log")
    logger.info('{message}: {reason}')
    return context

from gaukl.core.context.context import Context
from gaukl.core.tasks.task import task, Roles


@task(shortname='mytask', role=Roles.WORKFLOW)
def my_task(context: Context) -> Context:
    """Add a custom task.
    Tasks are used in recipes in the "workflow:" part, they manipulate or do something with the context.
    Tasks must at least receive the context as he first argument, but can receive any number of additionally keyword arguments
    Tasks must also always return the context.
    """
    return context


@task(shortname='my_other_task', role=Roles.GENERAL)
def my_other_task(context: Context) -> Context:
    return context

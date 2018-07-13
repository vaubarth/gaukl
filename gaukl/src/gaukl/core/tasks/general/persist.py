import time
from pathlib import Path

import yaml
from collections import OrderedDict

from gaukl.core.context.context import Context
from gaukl.core.tasks.task import task, Roles


@task(shortname='persist', role=Roles.WORKFLOW, async=False)
def persist(context: Context, only_not_matched: bool = True, path: str = None, name: str = None) -> Context:
    if only_not_matched and context.is_matched():
        return context
    sniffed = {
        'request': {
            'header': context.parsed_request_header(),
            'body': context.parsed_request_body()
        },
        'response': {
            'header': context.parsed_response_header() or context.raw_response_header(),
            'body': context.parsed_response_body() or context.raw_response_body()
        }

    }
    yaml.add_representer(OrderedDict, lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items()))

    yaml.dump(sniffed, Path(path).joinpath('{}_{}'.format(time.time(), name)).open('w'), default_flow_style=False)
    return context

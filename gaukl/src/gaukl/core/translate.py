import argparse
import importlib
from collections import OrderedDict

import yaml
from pathlib import Path

from gaukl.core.context.context import get_default_context

shorthands = {
    'xml': 'gaukl.core.tasks.transformers.xml.response_parse',
    'json': 'gaukl.core.tasks.transformers.json.response_parse'
}


def write_yaml(res: OrderedDict, file_path: str) -> str:
    to_dump = {
        'body': res
    }
    yaml.add_representer(OrderedDict, lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items()))
    new_file = f'{file_path}.yaml'

    yaml.dump(to_dump, Path(new_file).open('w'), default_flow_style=False)
    return new_file


def translate_file(file: Path, action: str) -> OrderedDict:
    ctx = get_default_context({})
    with file.open() as f:
        ctx['response']['body']['raw'] = f.read()

    split = action.split('.')
    mod = importlib.import_module('.'.join(split[:len(split) - 1]))

    fun = getattr(mod, split[len(split) - 1:len(split)][0])
    ctx = fun(ctx)

    return ctx['response']['body']['parsed']


def translate(search_path: Path, action: str, dump_path: Path) -> list:
    written_files = []
    path = search_path
    if search_path.is_dir():
        files = [p for p in path.iterdir() if path.is_file()]
    else:
        files = [path]
    for file in files:
        new_file = write_yaml(translate_file(file.resolve(), action), str(dump_path.joinpath(file.name)))
        written_files.append(new_file)
    return written_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path or file to be translated")
    parser.add_argument("out", help="Path to write translated file(s) to")
    parser.add_argument("parser", help="fully qualified name of function to be used for translation")
    args = parser.parse_args()

    written = translate(args.input, shorthands.get(args.parser) or args.parser, args.out)
    print(written)

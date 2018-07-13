from typing import Callable
from pathlib import Path

import yaml


def fqn(func: Callable) -> str:
    return f'{func.__module__}.{func.__name__}'


def load_yaml_path(path: Path) -> dict:
    with path.open() as f:
        return yaml.load(f)

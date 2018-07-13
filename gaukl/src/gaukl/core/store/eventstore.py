import yaml
from tinydb import TinyDB

from gaukl.core.context.context import Context


def purge(context: Context):
    with TinyDB(context['environment']['config']['internal']['eventdb_path']) as db:
        db.purge()


def insert(context: Context, event):
    with TinyDB(context['environment']['config']['internal']['eventdb_path']) as db:
        db.insert({'event': event, 'context': yaml.dump(context)})


def select(context: Context, limit):
    with TinyDB(context['environment']['config']['internal']['eventdb_path']) as db:
        return db.all()


def count(context: Context, event):
    with TinyDB(context['environment']['config']['internal']['eventdb_path']) as db:
        return {'count': len(db.all())}

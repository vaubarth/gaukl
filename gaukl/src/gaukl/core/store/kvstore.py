from tinydb import TinyDB, Query

from gaukl.core.context.context import Context


def purge(context: Context):
    with TinyDB(context['environment']['config']['internal']['vardb_path']) as db:
        db.purge()


def insert(context: Context, key, value):
    with TinyDB(context['environment']['config']['internal']['vardb_path']) as db:
        if not db.search(Query().key == key):
            db.insert({'key': key, 'value': value})


def select(context: Context, key):
    with TinyDB(context['environment']['config']['internal']['vardb_path']) as db:
        return db.search(Query().key == key)[0]

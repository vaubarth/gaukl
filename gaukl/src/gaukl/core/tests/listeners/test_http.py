import unittest
from time import sleep

import requests
from multiprocessing import Process

from gaukl.core.context.context import get_default_context
from gaukl.core.tasks.listeners.http import listener
from gaukl.core.store import eventstore


def fake_task_header(context):
    context['response']['body']['raw'] = 'body'
    context['response']['header']['parsed'] = {'x-test': 'test'}
    return context


def fake_task_status(context):
    context['response']['body']['raw'] = 'body'
    context['response']['header']['parsed'] = {'gaukl_status': '201 Created'}
    return context


class TestHttpListener(unittest.TestCase):
    def insert(self, a, b):
        pass

    def test_no_header(self):
        eventstore.insert = self.insert

        context = get_default_context({})
        context['environment']['recipe'] = {'workflow': []}
        context['environment']['tasks'] = []
        context['environment']['config'] = {'internal': {'db_path': ''}}

        listener_process = Process(group=None, target=listener, args=[context], kwargs={'port': 8080})
        listener_process.start()

        sleep(1)
        r = requests.get('http://localhost:8080')
        listener_process.terminate()
        self.assertEqual('', r.text)

    def test_context_reset(self):
        eventstore.insert = self.insert

        context = get_default_context({})
        context['environment']['recipe'] = {'workflow': []}
        context['environment']['tasks'] = []
        context['environment']['config'] = {'internal': {'db_path': ''}}

        context['response']['body']['raw'] = 'body'
        context['response']['header']['parsed'] = {'x-test': 'test'}

        listener_process = Process(group=None, target=listener, args=[context], kwargs={'port': 8080})
        listener_process.start()

        sleep(1)
        r = requests.get('http://localhost:8080')
        listener_process.terminate()
        self.assertNotIn('x-test', r.headers)
        self.assertEqual('', r.text)

    def test_header(self):
        eventstore.insert = self.insert

        context = get_default_context({})
        fake_task_header.async = False
        context['environment']['recipe'] = {'workflow': ['fake_task']}
        context['environment']['tasks'] = {'fake_task': fake_task_header}
        context['environment']['config'] = {'internal': {'db_path': ''}}

        listener_process = Process(group=None, target=listener, args=[context], kwargs={'port': 8080})
        listener_process.start()

        sleep(1)
        r = requests.get('http://localhost:8080')
        listener_process.terminate()
        self.assertIn('x-test', r.headers)
        self.assertEqual('body', r.text)

    def test_status(self):
        eventstore.insert = self.insert

        context = get_default_context({})
        fake_task_status.async = False
        context['environment']['recipe'] = {'workflow': ['fake_task']}
        context['environment']['tasks'] = {'fake_task': fake_task_status}
        context['environment']['config'] = {'internal': {'db_path': ''}}

        listener_process = Process(group=None, target=listener, args=[context], kwargs={'port': 8080})
        listener_process.start()

        sleep(1)
        r = requests.get('http://localhost:8080')
        listener_process.terminate()
        self.assertEqual('body', r.text)

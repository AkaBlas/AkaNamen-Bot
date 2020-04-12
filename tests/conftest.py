#!/usr/bin/env python
import datetime as dt
import os
import sys
from collections import defaultdict
from queue import Queue
from threading import Thread, Event
from time import sleep

import pytest
from telegram import Bot
from telegram.ext import Dispatcher, JobQueue, Updater

from tests.bots import get_bot

GITHUB_ACTION = os.getenv('GITHUB_ACTION', False)

# On Github Actions fold the output
if GITHUB_ACTION:
    pytest_plugins = ['tests.plugin_github_group']


def pytest_configure(config):
    if sys.version_info >= (3,):
        config.addinivalue_line('filterwarnings', 'ignore::ResourceWarning')


@pytest.fixture(scope='session')
def today():
    return dt.date.today()


@pytest.fixture(scope='session')
def bot_info():
    return get_bot()


@pytest.fixture(scope='session')
def bot(bot_info):
    return make_bot(bot_info)


@pytest.fixture(scope='session')
def chat_id(bot_info):
    return bot_info['chat_id']


@pytest.fixture(scope='session')
def super_group_id(bot_info):
    return bot_info['super_group_id']


def create_dp(bot):
    # Dispatcher is heavy to init (due to many threads and such) so we have a single session
    # scoped one here, but before each test, reset it (dp fixture below)
    dispatcher = Dispatcher(bot, Queue(), job_queue=JobQueue(), workers=2, use_context=True)
    dispatcher.job_queue.set_dispatcher(dispatcher)
    thr = Thread(target=dispatcher.start)
    thr.start()
    sleep(2)
    yield dispatcher
    sleep(1)
    if dispatcher.running:
        dispatcher.stop()
    thr.join()


@pytest.fixture(scope='session')
def _dp(bot):
    for dp in create_dp(bot):
        yield dp


@pytest.fixture(scope='function')
def dp(_dp):
    # Reset the dispatcher first
    while not _dp.update_queue.empty():
        _dp.update_queue.get(False)
    _dp.chat_data = defaultdict(dict)
    _dp.user_data = defaultdict(dict)
    _dp.bot_data = {}
    _dp.persistence = None
    _dp.handlers = {}
    _dp.groups = []
    _dp.error_handlers = []
    _dp.__stop_event = Event()
    _dp.__exception_event = Event()
    _dp.__async_queue = Queue()
    _dp.__async_threads = set()
    _dp.persistence = None
    _dp.use_context = True
    if _dp._Dispatcher__singleton_semaphore.acquire(blocking=0):
        Dispatcher._set_singleton(_dp)
    yield _dp
    Dispatcher._Dispatcher__singleton_semaphore.release()


@pytest.fixture(scope='function')
def updater(bot):
    up = Updater(bot=bot, workers=2)
    yield up
    if up.running:
        up.stop()


def make_bot(bot_info, **kwargs):
    return Bot(bot_info['token'], **kwargs)

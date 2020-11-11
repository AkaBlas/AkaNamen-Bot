#!/usr/bin/env python
import pytest
import datetime as dt
import os
import sys

from collections import defaultdict
from queue import Queue
from threading import Thread, Event
from time import sleep

from telegram import Bot, ParseMode
from telegram.ext import Dispatcher, JobQueue, Updater, Defaults
from geopy import Photon

from tests.bots import get_bot
from tests.orchestra import orchestra
from tests.addresses import get_address_from_cache

GITHUB_ACTION = os.getenv('GITHUB_ACTION', False)

# On Github Actions fold the output
if GITHUB_ACTION:
    pytest_plugins = ['tests.plugin_github_group']

# Make sure that we don't actually geocode data in the tests
orig_geocode = Photon.geocode
orig_reverse = Photon.reverse


def new_geocode(*args, **kwargs):
    pytest.fail('Make sure to mock Photon.geocode with tests.addresses.get_address_from_cache')


def new_reverse(*args, **kwargs):
    pytest.fail('Make sure to mock Photon.reverse with tests.addresses.get_address_from_cache')


Photon.geocode = new_geocode
Photon.reverse = new_reverse


def pytest_configure(config):
    if sys.version_info >= (3,):
        config.addinivalue_line('filterwarnings', 'ignore::ResourceWarning')


@pytest.fixture(scope='session')
def today():
    return dt.date.today()


@pytest.fixture(scope='session')
def bot_info():
    return get_bot()


def make_bot(bot_info, **kwargs):
    return Bot(
        bot_info['token'],
        **kwargs,
        defaults=Defaults(parse_mode=ParseMode.HTML, disable_notification=True),
    )


@pytest.fixture(scope='session')
def bot(bot_info):
    return make_bot(bot_info)


@pytest.fixture(scope='session')
def chat_id(bot_info):
    return int(bot_info['chat_id'])


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


@pytest.fixture(scope='function')
def populated_orchestra(request, monkeypatch, bot, chat_id):
    monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)
    param = request.param if hasattr(request, 'param') else {}
    members = param.get('members', 100)
    skip = param.get('skip', [])
    return orchestra(members, bot, chat_id, skip=skip)

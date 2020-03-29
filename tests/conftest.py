#!/usr/bin/env python
import datetime
import re
from collections import defaultdict
from queue import Queue
from threading import Thread, Event
from time import sleep

import pytest

from telegram import (Bot, Message, User, Chat, MessageEntity, Update)
from telegram.ext import Dispatcher, JobQueue, Updater
from tests.bots import get_bot


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
    _dp.use_context = False
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


CMD_PATTERN = re.compile(r'/[\da-z_]{1,32}(?:@\w{1,32})?')
DATE = datetime.datetime.now()


def make_message(text, **kwargs):
    """
    Testing utility factory to create a fake ``telegram.Message`` with
    reasonable defaults for mimicking a real message.
    :param text: (str) message text
    :return: a (fake) ``telegram.Message``
    """
    return Message(message_id=1,
                   from_user=kwargs.pop('user', User(id=1, first_name='', is_bot=False)),
                   date=kwargs.pop('date', DATE),
                   chat=kwargs.pop('chat', Chat(id=1, type='')),
                   text=text,
                   bot=kwargs.pop('bot', make_bot(get_bot())),
                   **kwargs)


def make_command_message(text, **kwargs):
    """
    Testing utility factory to create a message containing a single telegram
    command.
    Mimics the Telegram API in that it identifies commands within the message
    and tags the returned ``Message`` object with the appropriate ``MessageEntity``
    tag (but it does this only for commands).

    :param text: (str) message text containing (or not) the command
    :return: a (fake) ``telegram.Message`` containing only the command
    """

    match = re.search(CMD_PATTERN, text)
    entities = [
        MessageEntity(
            type=MessageEntity.BOT_COMMAND, offset=match.start(0), length=len(match.group(0)))
    ] if match else []

    return make_message(text, entities=entities, **kwargs)


def make_message_update(message, message_factory=make_message, edited=False, **kwargs):
    """
    Testing utility factory to create an update from a message, as either a
    ``telegram.Message`` or a string. In the latter case ``message_factory``
    is used to convert ``message`` to a ``telegram.Message``.
    :param message: either a ``telegram.Message`` or a string with the message text
    :param message_factory: function to convert the message text into a ``telegram.Message``
    :param edited: whether the message should be stored as ``edited_message`` (vs. ``message``)
    :return: ``telegram.Update`` with the given message
    """
    if not isinstance(message, Message):
        message = message_factory(message, **kwargs)
    update_kwargs = {'message' if not edited else 'edited_message': message}
    return Update(0, **update_kwargs)


def make_command_update(message, edited=False, **kwargs):
    """
    Testing utility factory to create an update from a message that potentially
    contains a command. See ``make_command_message`` for more details.
    :param message: message potentially containing a command
    :param edited: whether the message should be stored as ``edited_message`` (vs. ``message``)
    :return: ``telegram.Update`` with the given message
    """
    return make_message_update(message, make_command_message, edited, **kwargs)

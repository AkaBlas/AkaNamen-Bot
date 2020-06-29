#!/usr/bin/env python
from configparser import ConfigParser

import pytest
import responses
from geopy import Photon
from telegram import Update, Message, User, Chat, CallbackQuery, MessageEntity
from telegram.ext import TypeHandler

from bot import (ORCHESTRA_KEY, PENDING_REGISTRATIONS_KEY, DENIED_USERS_KEY, REGISTRATION_PATTERN,
                 ADMIN_KEY)
from bot.setup import register_dispatcher
from bot.registration import ACCEPT_REGISTRATION, DENY_REGISTRATION
from components import Member, Orchestra
from tests.addresses import get_address_from_cache
from tests.check_file_path import check_file_path


class TestRegistration:
    handler_executed = False

    @pytest.fixture(autouse=True)
    def reset(self, dp, chat_id):
        self.handler_executed = False
        register_dispatcher(dp, chat_id)
        dp.bot_data[ORCHESTRA_KEY] = Orchestra()

        def check_handler_callback(update, context):
            self.handler_executed = True

        check_handler = TypeHandler(Update, check_handler_callback)
        dp.add_handler(check_handler, group=1000)

    def test_check_registration_status_no_effective_user(self, dp):
        update = Update(123, channel_post=Message(123, User(123, 'user', False), None, None))
        dp.process_update(update)
        assert not self.handler_executed

    def test_check_registration_status_orchestra_member(self, dp):
        dp.bot_data[ORCHESTRA_KEY].register_member(Member(123))
        update = Update(123, message=Message(123, User(123, 'user', False), None, None))
        dp.process_update(update)
        assert self.handler_executed

    def test_check_registration_status_pending_registration(self, dp, monkeypatch, chat_id):
        dp.bot_data[ADMIN_KEY] = None
        orig_send_message = dp.bot.send_message
        answer_message = None

        def send_message(*args, **kwargs):
            nonlocal answer_message
            answer_message = orig_send_message(*args, **kwargs)
            return answer_message

        monkeypatch.setattr(dp.bot, 'send_message', send_message)
        dp.bot_data[PENDING_REGISTRATIONS_KEY][chat_id] = None
        update = Update(123,
                        message=Message(chat_id,
                                        User(chat_id, 'user', False),
                                        None,
                                        Chat(chat_id, Chat.PRIVATE),
                                        bot=dp.bot))

        dp.process_update(update)
        assert isinstance(answer_message, Message)
        assert 'Geduld' in answer_message.text
        assert not self.handler_executed

    def test_check_registration_status_denied_user(self, dp):
        dp.bot_data[ADMIN_KEY] = None
        dp.bot_data[DENIED_USERS_KEY].append(123)
        update = Update(123, message=Message(123, User(123, 'user', False), None, None))
        dp.process_update(update)
        assert not self.handler_executed

    def test_check_registration_status_not_registered(self, dp, chat_id, monkeypatch):
        dp.bot_data[ADMIN_KEY] = None
        orig_send_message = dp.bot.send_message
        answer_message = None

        def send_message(*args, **kwargs):
            nonlocal answer_message
            answer_message = orig_send_message(*args, **kwargs)
            return answer_message

        monkeypatch.setattr(dp.bot, 'send_message', send_message)
        update = Update(123,
                        message=Message(chat_id,
                                        User(chat_id, 'user', False),
                                        None,
                                        Chat(chat_id, Chat.PRIVATE),
                                        bot=dp.bot,
                                        text='/start'))

        dp.process_update(update)
        assert answer_message is None
        assert self.handler_executed
        self.handler_executed = False

        update = Update(123,
                        message=Message(chat_id,
                                        User(chat_id, 'user', False),
                                        None,
                                        Chat(chat_id, Chat.PRIVATE),
                                        bot=dp.bot,
                                        text='/not_start'))

        dp.process_update(update)
        assert isinstance(answer_message, Message)
        assert 'Bevor Du los raten kannst' in answer_message.text
        assert not self.handler_executed

    @responses.activate
    def test_request_registration(self, dp, chat_id, monkeypatch):
        monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)

        config = ConfigParser()
        config.read('bot.ini')
        url = config['akadressen']['url']
        with open(check_file_path('tests/data/akadressen.pdf'), 'rb') as akadressen:
            responses.add(responses.GET,
                          url,
                          body=akadressen.read(),
                          stream=True,
                          status=200,
                          adding_headers={'Transfer-Encoding': 'chunked'})

        orig_send_message = dp.bot.send_message
        messages = []

        def send_message(*args, **kwargs):
            nonlocal messages
            messages.append(orig_send_message(*args, **kwargs))
            return messages[-1]

        monkeypatch.setattr(dp.bot, 'send_message', send_message)

        update = Update(123,
                        message=Message(chat_id,
                                        User(chat_id,
                                             is_bot=False,
                                             first_name='John',
                                             last_name='Doe'),
                                        chat=Chat(chat_id, Chat.PRIVATE),
                                        bot=dp.bot,
                                        text='/start',
                                        entities=[MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)],
                                        date=None))

        dp.process_update(update)
        update = Update(123,
                        callback_query=CallbackQuery(1,
                                                     User(chat_id,
                                                          is_bot=False,
                                                          first_name='John',
                                                          last_name='Doe'),
                                                     Chat(chat_id, Chat.PRIVATE),
                                                     message=messages[-1],
                                                     data=REGISTRATION_PATTERN))

        dp.process_update(update)
        assert 'Name: John "Jonny" Doe' in messages[-1].text
        assert dp.bot_data[PENDING_REGISTRATIONS_KEY][chat_id][0].full_name == 'John "Jonny" Doe'

    @responses.activate
    def test_request_registration_no_result(self, dp, chat_id, monkeypatch):
        monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)

        config = ConfigParser()
        config.read('bot.ini')
        url = config['akadressen']['url']
        with open(check_file_path('tests/data/akadressen.pdf'), 'rb') as akadressen:
            responses.add(responses.GET,
                          url,
                          body=akadressen.read(),
                          stream=True,
                          status=200,
                          adding_headers={'Transfer-Encoding': 'chunked'})

        orig_send_message = dp.bot.send_message
        messages = []

        def send_message(*args, **kwargs):
            nonlocal messages
            messages.append(orig_send_message(*args, **kwargs))
            return messages[-1]

        monkeypatch.setattr(dp.bot, 'send_message', send_message)

        update = Update(123,
                        message=Message(chat_id,
                                        User(chat_id, is_bot=False, first_name='XXXXXX'),
                                        chat=Chat(chat_id, Chat.PRIVATE),
                                        bot=dp.bot,
                                        text='/start',
                                        entities=[MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)],
                                        date=None))

        dp.process_update(update)
        update = Update(123,
                        callback_query=CallbackQuery(1,
                                                     User(chat_id,
                                                          is_bot=False,
                                                          first_name='XXXXXX'),
                                                     Chat(chat_id, Chat.PRIVATE),
                                                     message=messages[-1],
                                                     data=REGISTRATION_PATTERN))

        dp.process_update(update)
        assert 'kein passendes Mitglied' in messages[-1].text
        assert dp.bot_data[PENDING_REGISTRATIONS_KEY][chat_id] == []

    def test_accept_registration_request_no_suggestion(self, dp, bot, chat_id, monkeypatch):
        message = bot.send_message(chat_id, 'test_message')
        dp.bot_data[PENDING_REGISTRATIONS_KEY][chat_id] = []

        orig_send_message = bot.send_message
        orig_edit_message = bot.edit_message_text
        reply_message = None

        def send_message(*args, **kwargs):
            nonlocal reply_message
            reply_message = orig_send_message(*args, **kwargs)
            return reply_message

        def edit_message_text(*args, **kwargs):
            nonlocal message
            message = orig_edit_message(*args, **kwargs)
            return message

        monkeypatch.setattr(bot, 'send_message', send_message)
        monkeypatch.setattr(bot, 'edit_message_text', edit_message_text)

        update = Update(123,
                        callback_query=CallbackQuery(1,
                                                     User(chat_id,
                                                          is_bot=False,
                                                          first_name='XXXXXX'),
                                                     Chat(chat_id, Chat.PRIVATE),
                                                     message=message,
                                                     data=ACCEPT_REGISTRATION.format(chat_id, '')))

        dp.process_update(update)

        chat_member = bot.get_chat_member(chat_id, chat_id).user
        member = dp.bot_data[ORCHESTRA_KEY].members[chat_id]
        assert member.first_name == chat_member.first_name
        assert member.last_name == chat_member.last_name
        assert 'mit den folgenden Daten angemeldet' in reply_message.text
        assert 'erfolgreich angemeldet' in message.text
        assert chat_id not in dp.bot_data[PENDING_REGISTRATIONS_KEY]

    def test_accept_registration_request_with_suggestion(self, dp, bot, chat_id, monkeypatch):
        message = bot.send_message(chat_id, 'test_message')
        dp.bot_data[PENDING_REGISTRATIONS_KEY][chat_id] = [
            Member(chat_id, first_name='0', last_name='0'),
            Member(chat_id, first_name='1', last_name='1')
        ]

        orig_send_message = bot.send_message
        orig_edit_message = bot.edit_message_text
        reply_message = None

        def send_message(*args, **kwargs):
            nonlocal reply_message
            reply_message = orig_send_message(*args, **kwargs)
            return reply_message

        def edit_message_text(*args, **kwargs):
            nonlocal message
            message = orig_edit_message(*args, **kwargs)
            return message

        monkeypatch.setattr(bot, 'send_message', send_message)
        monkeypatch.setattr(bot, 'edit_message_text', edit_message_text)

        update = Update(123,
                        callback_query=CallbackQuery(1,
                                                     User(chat_id,
                                                          is_bot=False,
                                                          first_name='XXXXXX'),
                                                     Chat(chat_id, Chat.PRIVATE),
                                                     message=message,
                                                     data=ACCEPT_REGISTRATION.format(chat_id, 1)))

        dp.process_update(update)

        member = dp.bot_data[ORCHESTRA_KEY].members[chat_id]
        assert member.first_name == '1'
        assert member.last_name == '1'
        assert 'mit den folgenden Daten angemeldet' in reply_message.text
        assert 'erfolgreich angemeldet' in message.text
        assert chat_id not in dp.bot_data[PENDING_REGISTRATIONS_KEY]

    def test_deny_registration_request(self, dp, bot, chat_id, monkeypatch):
        message = bot.send_message(chat_id, 'test_message')
        dp.bot_data[PENDING_REGISTRATIONS_KEY][chat_id] = []

        orig_send_message = bot.send_message
        orig_edit_message = bot.edit_message_text
        reply_message = None

        def send_message(*args, **kwargs):
            nonlocal reply_message
            reply_message = orig_send_message(*args, **kwargs)
            return reply_message

        def edit_message_text(*args, **kwargs):
            nonlocal message
            message = orig_edit_message(*args, **kwargs)
            return message

        monkeypatch.setattr(bot, 'send_message', send_message)
        monkeypatch.setattr(bot, 'edit_message_text', edit_message_text)

        update = Update(123,
                        callback_query=CallbackQuery(1,
                                                     User(chat_id,
                                                          is_bot=False,
                                                          first_name='XXXXXX'),
                                                     Chat(chat_id, Chat.PRIVATE),
                                                     message=message,
                                                     data=DENY_REGISTRATION.format(chat_id)))

        dp.process_update(update)

        assert chat_id not in dp.bot_data[ORCHESTRA_KEY].members
        assert 'Anfrage wurde abgelehnt' in reply_message.text
        assert 'wird jetzt ignoriert' in message.text
        assert chat_id in dp.bot_data[DENIED_USERS_KEY]
        assert chat_id not in dp.bot_data[PENDING_REGISTRATIONS_KEY]

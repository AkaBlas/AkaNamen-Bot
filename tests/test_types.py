#!/usr/bin/env python
from utils import MessageType, UpdateType
from telegram import Update, Message, CallbackQuery


class TestMessageType:

    def test_types(self):
        for attr_name in MessageType.__dict__:
            attr = getattr(MessageType, attr_name)
            is_special = attr_name.startswith('__') and attr_name.endswith('__')
            if isinstance(attr, str) and not is_special:
                assert attr == attr.lower()

    def test_all_types(self):
        for attr_name in MessageType.__dict__:
            attr = getattr(MessageType, attr_name)
            is_special = attr_name.startswith('__') and attr_name.endswith('__')
            if isinstance(attr, str) and not is_special:
                assert attr in MessageType.ALL_TYPES

    def test_relevant_type(self):
        for type_ in MessageType.ALL_TYPES:
            message = Message(1, None, None, None)
            setattr(message, type_, True)
            assert MessageType.relevant_type(message) == type_

            update = Update(1, message=message)
            assert MessageType.relevant_type(update) == type_

        message = Message(1, None, None, None, dice=True)
        update = Update(1, message=message)
        assert MessageType.relevant_type(message) is None
        assert MessageType.relevant_type(update) is None

        update = Update(1,
                        callback_query=CallbackQuery(2,
                                                     None,
                                                     None,
                                                     message=Message(1,
                                                                     None,
                                                                     None,
                                                                     None,
                                                                     text='test')))
        assert update.effective_message is not None
        assert MessageType.relevant_type(update) is None


class TestUpdateType:

    def test_types(self):
        for attr_name in UpdateType.__dict__:
            attr = getattr(UpdateType, attr_name)
            is_special = attr_name.startswith('__') and attr_name.endswith('__')
            if isinstance(attr, str) and not is_special:
                assert attr == attr.lower()

    def test_all_types(self):
        for attr_name in UpdateType.__dict__:
            attr = getattr(UpdateType, attr_name)
            is_special = attr_name.startswith('__') and attr_name.endswith('__')
            if isinstance(attr, str) and not is_special:
                assert attr in UpdateType.ALL_TYPES

    def test_relevant_type(self):
        for type_ in UpdateType.ALL_TYPES:
            update = Update(1)
            setattr(update, type_, True)
            assert UpdateType.relevant_type(update) == type_

        update = Update(1, shipping_query=True)
        assert UpdateType.relevant_type(update) is None

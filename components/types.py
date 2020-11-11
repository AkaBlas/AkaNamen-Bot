#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the classes MessageType and UpdateType."""
from typing import Union, Optional
from telegram.utils.helpers import effective_message_type
from telegram import Update, Message


class MessageType:
    """
    This object represents message types relevant for the AkaNamen Bot.
    """

    TEXT: str = 'text'
    """:obj:`str`: Text messages"""
    PHOTO: str = 'photo'
    """:obj:`str`: Foto messages"""
    LOCATION: str = 'location'
    """:obj:`str`: Location messages"""
    ALL_TYPES = [TEXT, PHOTO, LOCATION]
    """List[:obj:`str`]: All relevant types"""

    @classmethod
    def relevant_type(cls, entity: Union[Update, Message]) -> Optional[str]:
        """
        Extracts the type of the message, if it is relevant for the AkaNamen Bot in terms of
        :attr:`All_TYPES`. If it's not relevant, the output will be :obj:`None`.

        Note:
            In contrast to :meth:`telegram.utils.helpers.effective_message_type` , only updates
            with ``update.message`` are considered.

        Args:
            entity: A :class:`telegram.Update` or :class:`telegram.Message`
        """
        if isinstance(entity, Update) and not entity.message:
            return None
        type_ = effective_message_type(entity)
        if type_ in cls.ALL_TYPES:
            return type_
        return None


class UpdateType:
    """
    This object represents update types relevant for the AkaNamen Bot.
    """

    MESSAGE: str = 'message'
    """:obj:`str`: Message updates"""
    INLINE_QUERY: str = 'inline_query'
    """:obj:`str`: Inline query updates"""
    CHOSEN_INLINE_RESULT: str = 'chosen_inline_result'
    """:obj:`str`: Chosen inline result updates"""
    CALLBACK_QUERY: str = 'callback_query'
    """:obj:`str`: Callback query updates"""
    POLL: str = 'poll'
    """:obj:`str`: Poll updates"""
    POLL_ANSWER: str = 'poll_answer'
    """:obj:`str`: Poll answer updates"""
    ALL_TYPES = [MESSAGE, INLINE_QUERY, CHOSEN_INLINE_RESULT, CALLBACK_QUERY, POLL, POLL_ANSWER]
    """List[:obj:`str`]: All relevant types"""

    @classmethod
    def relevant_type(cls, update: Update) -> Optional[str]:
        """
        Extracts the type of the update, if it is relevant for the AkaNamen Bot in terms of
        :attr:`All_TYPES`. If it's not relevant, the output will be :obj:`None`.

        Args:
            update: A :class:`telegram.Update`
        """
        for type_ in cls.ALL_TYPES:
            if getattr(update, type_, None):
                return type_
        return None

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the GameHandler class."""
from game import Question

from abc import ABC
from collections import defaultdict
from threading import Lock

from typing import Dict

from telegram.ext import Handler, CallbackContext
from telegram import Update


class GameHandler(ABC, Handler):
    """
    A :class:`telegram.ext.Handler` acting as base class for game handlers for the specific games
    of the AkaNamen Bot. Subclasses must implement

    * :meth:`foo`
    * :meth:`bar`

    POLLS MUST BE SEND AS NON ANONYMUS IN ORDER TO RECEIVE POLL ANSWERS
    BIRTDAYS MUST BE ENTERED AS DD.MM.
    FOR ISTRUMENT FREE TEXT, SHOW KEYBOARD WITH AVAILABLE OPTIONS
    """

    def __init__(self) -> None:
        Handler.__init__(self, callback=self.callback)

        self._awaited_update_type: Dict[int, str] = defaultdict(str)
        self._awaited_update_type_lock = Lock()

        self._awaited_message_type: Dict[int, str] = defaultdict(str)
        self._awaited_message_type_lock = Lock()

        self._current_question: Dict[int, Question] = {}
        self._current_question_lock = Lock()

    @staticmethod
    def callback(update: Update, context: CallbackContext):
        pass

    @property
    def awaited_update_type(self) -> Dict[int, str]:
        """
        For each chat ID ``chat_id``, ``awaited_update_type[chat_id]`` is one of
        :attr:`utils.UpdateType.ALL_TYPES` indicating the kind of response from the chat, the game
        awaits.
        """
        with self._awaited_update_type_lock:
            return self._awaited_update_type

    @property
    def awaited_message_type(self) -> Dict[int, str]:
        """
        For each chat ID ``chat_id``, ``awaited_message_type[chat_id]`` is one of
        :attr:`utils.MessageType.ALL_TYPES` indicating the kind of message from the chat, the game
        awaits. Only relevant, of ``awaited_update_type[chat_id] == UpdateType.MESSAGE``.
        """
        with self._awaited_message_type_lock:
            return self._awaited_message_type

    @property
    def current_question(self) -> Dict[int, Question]:
        """
        For each chat ID ``chat_id``, ``current_question[chat_id]`` is a :class:`game.Question``
        instance representing the question currently asked in the chat for this game.
        """
        with self._current_question_lock:
            return self._current_question

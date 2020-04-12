#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the GameContext class."""
from components import Question, Orchestra
from components.constants import GAME_IN_PROGRESS_KEY, ORCHESTRA_KEY

from telegram.ext import CallbackContext

from collections import defaultdict
from typing import Optional, Dict


class GameContext(CallbackContext):
    """
    A custom :class:`telegram.ext.CallbackContext` class that has some attributes handy for the use
    in :class:`components.GameHandler`.

    Attributes:
        games_chat_id: The chat id the game this context is part of, takes place in. Useful, if the
            update is a :class:`telegram.PollAnswer`.
        question: The current question of the game.
        answer_is_correct: Whether the answer to the question was correct.

    Args:
        context: A :class:`telegram.ext.CallbackContext` instance.
    """

    def __init__(self, context: CallbackContext) -> None:
        # Copy contexts attributes
        self.update(context.__dict__)

        # New attribute
        self.games_chat_id: Optional[int] = None
        self.question: Optional[Question] = None
        self.answer_is_correct: Optional[bool] = None

    @property
    def games_in_progress(self) -> Dict[int, bool]:
        """
        Convenience property at access ``context.bot_data[GAME_IN_PROGRESS_KEY]``.
        """
        return self.bot_data.get(GAME_IN_PROGRESS_KEY, defaultdict(lambda: False))

    @property
    def orchestra(self) -> Optional[Orchestra]:
        """
        Convenience property at access ``context.bot_data[ORCHESTRA_KEY]``.
        """
        return self.bot_data.get(ORCHESTRA_KEY, None)

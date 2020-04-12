#!/usr/bin/env python
from components import GameContext
from components.constants import ORCHESTRA_KEY, GAME_IN_PROGRESS_KEY
from telegram.ext import CallbackContext


class TestGameContext:

    def test_init(self, dp):
        context = CallbackContext(dp)
        gc = GameContext(context)
        assert gc is not context
        assert gc.dispatcher is context.dispatcher
        assert gc.games_chat_id is None
        assert gc.question is None
        assert gc.answer_is_correct is None
        assert gc.games_in_progress == {}
        assert gc.orchestra is None

    def test_properties(self, dp):
        context = CallbackContext(dp)
        gc = GameContext(context)
        context.bot_data[ORCHESTRA_KEY] = 1
        context.bot_data[GAME_IN_PROGRESS_KEY] = {2: 3}

        assert gc.orchestra == 1
        assert gc.games_in_progress == {2: 3}

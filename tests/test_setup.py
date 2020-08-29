#!/usr/bin/env python
from bot.setup import BOT_COMMANDS, register_dispatcher


class TestSetup:

    def test_set_commands(self, dp, chat_id):
        dp.bot.set_my_commands([])
        assert dp.bot.get_my_commands() == []
        register_dispatcher(dp, chat_id)
        assert dp.bot.get_my_commands() == BOT_COMMANDS

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for setting up to bot at start up."""
from typing import List, Union

from telegram import BotCommand, Update
from telegram.ext import Dispatcher, TypeHandler, CommandHandler, CallbackQueryHandler
from bot import (ORCHESTRA_KEY, PENDING_REGISTRATIONS_KEY, DENIED_USERS_KEY, ADMIN_KEY,
                 REGISTRATION_PATTERN)
import bot.registration as registration
from components import Orchestra

BOT_COMMANDS: List[BotCommand] = [
    BotCommand('start', 'Startet den Bot.'),
]
"""List[:class:`telegram.BotCommand`]: A list of commands of the bot."""


def register_dispatcher(disptacher: Dispatcher, admin: Union[int, str]) -> None:
    """
    Adds handlers. Convenience method to avoid doing that all in the main script.
    Also sets the bot commands and makes sure ``dispatcher.bot_data`` is set up correctly.

    Args:
        disptacher: The :class:`telegram.ext.Dispatcher`.
        admin: The admins chat id.
    """
    # Handlers
    disptacher.add_handler(TypeHandler(Update, registration.check_registration_status), group=-1)
    disptacher.add_handler(CommandHandler('start', registration.start))
    disptacher.add_handler(
        CallbackQueryHandler(registration.request_registration, pattern=REGISTRATION_PATTERN))
    disptacher.add_handler(registration.ACCEPT_REGISTRATION_HANDLER)
    disptacher.add_handler(registration.DENY_REGISTRATION_HANDLER)

    # Set commands
    disptacher.bot.set_my_commands(BOT_COMMANDS)

    # Set up bot_dat
    bot_data = disptacher.bot_data
    if not bot_data.get(ORCHESTRA_KEY):
        bot_data[ORCHESTRA_KEY] = Orchestra()
    if not bot_data.get(PENDING_REGISTRATIONS_KEY):
        bot_data[PENDING_REGISTRATIONS_KEY] = dict()
    if not bot_data.get(DENIED_USERS_KEY):
        bot_data[DENIED_USERS_KEY] = list()
    bot_data[ADMIN_KEY] = int(admin)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for the admin."""
from telegram import Update
from telegram.ext import CallbackContext

from bot import ORCHESTRA_KEY
from components import Orchestra


def rebuild_orchestra(update: Update, context: CallbackContext) -> None:
    """
    Builds a new orchestra by registering all members from the one in ``context.bot_data`` to a
    new instance of :class:`components.Orchestra`. Puts the new orchestra in ``bot_data``.
    Useful, if there have been changes to the attribute manager setup.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    members = context.bot_data[ORCHESTRA_KEY].members.values()
    orchestra = Orchestra()

    for member in members:
        orchestra.register_member(member.copy())

    context.bot_data[ORCHESTRA_KEY] = orchestra
    update.message.reply_text('Orchester neu besetzt.')

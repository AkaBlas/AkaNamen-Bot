#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for checking if users blocked the bot."""
import datetime

from telegram import ChatAction
from telegram.error import Unauthorized
from telegram.ext import CallbackContext, Dispatcher

from bot import ORCHESTRA_KEY, ADMIN_KEY


def check_users(context: CallbackContext) -> None:
    """
    Checks for each member of the orchestra, if the bot can still access the user. If there are
    users, who blocked the bot, they are deleted from the orchestra and the admin is informed.

    Args:
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    orchestra = context.bot_data[ORCHESTRA_KEY]

    blocked_users = []
    for uid in orchestra.members:
        try:
            context.bot.send_chat_action(chat_id=uid, action=ChatAction.TYPING)
        except Unauthorized:
            blocked_users.append(uid)

    if blocked_users:
        blocked_users_text = []
        for uid in blocked_users:
            member = orchestra.members[uid]
            blocked_users_text.append(f'Name:{member.full_name or "-"}, ID: {member.user_id}')
            orchestra.kick_member(member)

        insert_text = '\n'.join(blocked_users_text)
        text = (
            'Seit der letzten Überprüfung haben die folgenden AkaBlasen den Bot blockiert:\n\n'
            f'{insert_text}\n\nSie wurden aus dem digitalen Orchester gelöscht.'
        )
        context.bot.send_message(chat_id=context.bot_data[ADMIN_KEY], text=text)


def schedule_daily_job(dispatcher: Dispatcher) -> None:
    """
    Schedules a job running daily at 2AM which runs :meth:`check_users`.

    Args:
        dispatcher: The :class:`telegram.ext.Dispatcher`.
    """
    dispatcher.job_queue.run_daily(check_users, datetime.time(2, 0))

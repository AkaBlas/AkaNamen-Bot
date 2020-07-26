#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for banning users."""
from telegram import (Update, ChatAction, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.error import Unauthorized
from telegram.ext import CallbackContext, ConversationHandler, \
    CommandHandler, MessageHandler, Filters

from bot import ORCHESTRA_KEY, BANNING_KEY, DENIED_USERS_KEY, ADMIN_KEY

SELECTING_USER = 'SELECTING_USER'
"""
:obj:`str`: State of the conversation in which the user to ban is selected.
"""
CONFIRMATION = 'CONFIRMATION'
"""
:obj:`str`: State of the conversation in which the cancellation is to be confirmed.
"""
CONFIRMATION_TEXT = 'Hinfort! Garstiges Gesindel!'
"""
:obj:`str`: The text used to confirm the ban.
"""
BANNING_PATTERN = r'.*ID:(\d*)'
"""
obj:`str`: Pattern to extract the ID to be banned in the :attr:`CONFIRMATION` state.
``context.matches.group(1)`` will be the id (as string).
"""


def select_user(update: Update, context: CallbackContext) -> str:
    """
    Asks the admin which user is to be banned.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    context.bot.send_chat_action(chat_id=update.effective_user.id, action=ChatAction.TYPING)

    orchestra = context.bot_data[ORCHESTRA_KEY]

    buttons = []
    for uid, member in orchestra.members.items():
        if uid != context.bot_data[ADMIN_KEY]:
            user = context.bot.get_chat_member(uid, uid).user
            if user.username:
                button_text = f'{member.full_name} ({user.full_name}, @{user.username}), ID:{uid}'
            else:
                button_text = f'{member.full_name} ({user.full_name}), ID:{uid}'
            buttons.append(button_text)

    if not buttons:
        update.effective_message.reply_text(
            text='Es gibt keine Mitglieder, die gebannt werden könnten.')
        return ConversationHandler.END

    text = 'Wer hat sich denn daneben benommen?'
    reply_markup = ReplyKeyboardMarkup.from_column(buttons)

    update.effective_message.reply_text(text=text, reply_markup=reply_markup)

    return SELECTING_USER


def ask_for_confirmation(update: Update, context: CallbackContext) -> str:
    """
    Asks the admin for confirmation.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    text = 'Ganz sicher? Der Nutzer wird dann dauerhaft geblockt. Ent-blocken ist zur Zeit noch ' \
           'nicht implementiert! Wenn ja, schick mir eine Nachricht mit dem Text' \
           f'\n\n<code>{CONFIRMATION_TEXT}</code>\n\nZum Abbrechen schick mir irgendwas.'

    update.effective_message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    context.user_data[BANNING_KEY] = int(context.matches[0].group(1))

    return CONFIRMATION


def confirm(update: Update, context: CallbackContext) -> int:
    """
    Deletes the member, bans it permanently and informs both the admin and the member.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    context.bot.send_chat_action(chat_id=update.effective_user.id, action=ChatAction.TYPING)

    uid = context.user_data[BANNING_KEY]

    orchestra = context.bot_data[ORCHESTRA_KEY]
    orchestra.kick_member(orchestra.members[uid])
    context.bot_data[DENIED_USERS_KEY].append(uid)

    update.effective_message.reply_text('Aye, aye. Ist erledigt.')

    text = 'Du wurdest vom Administrator blockiert. Ich werde nicht weiter auf Dich reagieren.'
    try:
        context.bot.send_message(chat_id=uid, text=text)
    except Unauthorized:
        pass

    return ConversationHandler.END


def cancel_banning(update: Update, context: CallbackContext) -> int:
    """
    Cancels the banning.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    text = 'Vorgang abgebrochen. Nutzer wird nicht blockiert.'
    update.effective_message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def build_banning_handler(admin: int) -> ConversationHandler:
    """
    Returns a handler used to ban members, which is accessible only for the admin.

    Args:
        admin: The admins ID
    """
    # yapf: disable
    return ConversationHandler(
        entry_points=[CommandHandler('ban', select_user)],
        states={
            SELECTING_USER: [MessageHandler(Filters.regex(BANNING_PATTERN) & Filters.user(admin),
                                            ask_for_confirmation)],
            CONFIRMATION: [
                MessageHandler(Filters.text(CONFIRMATION_TEXT), confirm),
                MessageHandler(~Filters.command, cancel_banning)
            ]
        },
        fallbacks=[])
    # yapf: enable

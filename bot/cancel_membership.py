#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for canceling the membership."""
from telegram import (Update, InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import CallbackContext, CallbackQueryHandler, ConversationHandler, \
    CommandHandler, MessageHandler, Filters

from bot import ORCHESTRA_KEY, CANCELLATION_MESSAGE_KEY, CONVERSATION_KEY

CONFIRMATION_TEXT = 'Oooh, Så svinge vi på seidelen igen ... Skål!'
"""
:obj:`str`: The text used to confirm the cancellation.
"""
CONFIRMATION = 'CONFIRMATION'
"""
:obj:`str`: State of the conversation in which the cancellation is to be confirmed.
"""
CONVERSATION_VALUE = 'cancelling_membership'
"""
:obj:`str`: The value of ``context.user_data[CONVERSATION_KEY]`` if the user is in a membership
cancellation conversation.
"""
CONVERSATION_INTERRUPT_TEXT = 'Hey! Entscheid Dich erst einmal, ob Du noch angemeldet bleiben ' \
                              'möchtest, bevor Du etwas anderes versuchst. 🙄 '
"""
:obj:`str`: Message to send, if the user tries to interrupt this conversation.
"""


def ask_for_confirmation(update: Update, context: CallbackContext) -> str:
    """
    Requests the user to confirm the cancellation request and informs them on what a cancellation
    will mean for them.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    context.user_data[CONVERSATION_KEY] = CONVERSATION_VALUE
    text = 'Bist Du Dir <i>ganz</i> sicher, dass Du das möchtest? 🥺 Wenn Du Dich abmeldest, ' \
           'kannst Du den AkaNamen-Bot nicht mehr nutzen und andere AkaBlasen können nicht mehr ' \
           'Deinen Namen lernen.\n\n<b>Bitte beachte:</b> Wenn Du Dich abmeldest, werden alle ' \
           'Deine Daten vom AkaNamen-Bot gelöscht.Ob/wann sie von den Telegram-Servern gelöscht ' \
           'werden, kann der AkaNamen-Bot nicht beeinflussen.\n\nWenn Du Dich <i>wirklich</i> ' \
           'abmelden möchtest, sende mir eine Nachricht mit dem Text ' \
           f'\n\n<code>{CONFIRMATION_TEXT}</code>\n\n Wenn Du doch lieber bleiben möchtest, ' \
           'nutze den Knopf unten.'
    reply_markup = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton(text='Nein, nein, das war ein Versehen! Abbruch! 😱',
                             callback_data='cancel_cancellation'))
    msg = update.effective_message.reply_text(text, reply_markup=reply_markup)
    context.user_data[CANCELLATION_MESSAGE_KEY] = msg

    return CONFIRMATION


def confirm(update: Update, context: CallbackContext) -> int:
    """
    Deletes the member and confirms the cancellation.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    text = 'Schade, dass Du gehst. Natürlich kannst Du jederzeit zurückkommen! Sende dafür ' \
           'einfach den /start Befehl. 😎 '

    update.effective_message.reply_text(text)

    orchestra = context.bot_data[ORCHESTRA_KEY]
    orchestra.kick_member(orchestra.members[update.effective_user.id])

    context.user_data[CONVERSATION_KEY] = False
    return ConversationHandler.END


def cancel_cancellation(update: Update, context: CallbackContext) -> int:
    """
    Cancels the cancellation.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    text = 'Sehr schön 😊 Da bin ich beruhigt.'

    if update.message:
        msg = context.user_data[CANCELLATION_MESSAGE_KEY]
        msg.edit_reply_markup()
        update.effective_message.reply_text(text)
    else:
        update.effective_message.edit_text(text)

    context.user_data[CONVERSATION_KEY] = False
    return ConversationHandler.END


CANCEL_MEMBERSHIP_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('abmelden', ask_for_confirmation)],
    states={
        CONFIRMATION: [
            MessageHandler(Filters.text(CONFIRMATION_TEXT) & ~Filters.command, confirm),
            MessageHandler(~Filters.command, cancel_cancellation),
            CallbackQueryHandler(cancel_cancellation)
        ]
    },
    fallbacks=[])
""":class:`telegram.ext.ConversationHandler`: Handler used to allow users to cancel their
membership. """

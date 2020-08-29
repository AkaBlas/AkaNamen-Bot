#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for the inline mode."""
from typing import Union

from telegram import (Update, InlineQueryResultArticle, InputTextMessageContent,
                      InlineKeyboardMarkup, InlineKeyboardButton, ChatAction)
from telegram.constants import MAX_INLINE_QUERY_RESULTS
from telegram.ext import CallbackContext, CallbackQueryHandler

from bot import ORCHESTRA_KEY, INLINE_HELP

REQUEST_CONTACT = 'contact_request {}'
""":obj:`str`: Callback data for requesting the vCard of a member.
Use as ``REQUEST_CONTACT.format(user_id)``."""
REQUEST_CONTACT_PATTERN = r'contact_request (\d*)'
""":obj:`str`: Callback data  pattern for requesting the vCard of a member.
``context.match.group(1)`` will be users id."""


def search_users(update: Update, context: CallbackContext) -> None:
    """
    Searches the orchestras members for a match of the inline query and answers the query.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    inline_query = update.inline_query
    query = inline_query.query

    if inline_query.offset:
        offset = int(inline_query.offset)
    else:
        offset = 0
    next_offset: Union[str, int] = ''

    if not query:
        results = []
    else:
        orchestra = context.bot_data[ORCHESTRA_KEY]
        user_id = update.effective_user.id
        members = [
            m for uid, m in orchestra.members.items() if m.allow_contact_sharing and uid != user_id
        ]
        sorted_members = sorted(members, key=lambda m: m.compare_full_name_to(query), reverse=True)

        # Telegram only likes up to 50 results
        if len(sorted_members) > (offset + 1) * MAX_INLINE_QUERY_RESULTS:
            next_offset = offset + 1
            sorted_members = sorted_members[offset * MAX_INLINE_QUERY_RESULTS:offset
                                            * MAX_INLINE_QUERY_RESULTS + MAX_INLINE_QUERY_RESULTS]
        else:
            sorted_members = sorted_members[offset * MAX_INLINE_QUERY_RESULTS:]

        results = [
            InlineQueryResultArticle(id=m.user_id,
                                     title=m.full_name,
                                     input_message_content=InputTextMessageContent(m.to_str()),
                                     reply_markup=InlineKeyboardMarkup.from_button(
                                         InlineKeyboardButton(text='vCard-Datei anfordern 📇',
                                                              callback_data=REQUEST_CONTACT.format(
                                                                  m.user_id))))
            for m in sorted_members
        ]

    inline_query.answer(results=results,
                        next_offset=next_offset,
                        switch_pm_text='Hilfe',
                        switch_pm_parameter=INLINE_HELP)


def send_vcard(update: Update, context: CallbackContext) -> None:
    """
    Sends the vCard of a Member as requested by the keyboard attached to an inline query result.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    context.bot.send_chat_action(update.effective_user.id, action=ChatAction.UPLOAD_DOCUMENT)

    uid = int(context.match.group(1))
    orchestra = context.bot_data[ORCHESTRA_KEY]
    member = orchestra.members[uid]
    vcard = member.vcard(context.bot)

    update.callback_query.answer()
    update.callback_query.edit_message_reply_markup(reply_markup=None)
    context.bot.send_document(chat_id=update.effective_user.id,
                              document=vcard,
                              filename=member.vcard_filename,
                              caption=member.full_name)
    vcard.close()


SEND_VCARD_HANDLER = CallbackQueryHandler(send_vcard, pattern=REQUEST_CONTACT_PATTERN)
""":class:`telegram.ext.CallbackQueryHandler`: Handler used to send vCards on request."""

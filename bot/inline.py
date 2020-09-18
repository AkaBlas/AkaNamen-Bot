#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for the inline mode."""
from typing import Union

from telegram import (Update, InlineQueryResultArticle, InputTextMessageContent,
                      InlineKeyboardMarkup, InlineKeyboardButton, ChatAction)
from telegram.ext import CallbackContext, CallbackQueryHandler

from bot import ORCHESTRA_KEY, INLINE_HELP, ADMIN_KEY

REQUEST_CONTACT = 'contact_request {}'
""":obj:`str`: Callback data for requesting the vCard of a member.
Use as ``REQUEST_CONTACT.format(user_id)``."""
REQUEST_CONTACT_PATTERN = r'contact_request (\d*)'
""":obj:`str`: Callback data  pattern for requesting the vCard of a member.
``context.match.group(1)`` will be users id."""
MEMBERS_PER_PAGE = 10
""":obj:`int`: Number of members per page in inline mode."""


def search_users(update: Update, context: CallbackContext) -> None:
    """
    Searches the orchestras members for a match of the inline query and answers the query. If the
    query is empty, returns all members in alphabetical order.

    Results are paginated with at most :attr:`MEMBERS_PER_PAGE` members per page.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    inline_query = update.inline_query
    query = inline_query.query
    orchestra = context.bot_data[ORCHESTRA_KEY]
    admin_id = context.bot_data[ADMIN_KEY]
    user_id = update.effective_user.id

    if inline_query.offset:
        offset = int(inline_query.offset)
    else:
        offset = 0
    next_offset: Union[str, int] = ''

    members = [
        m for uid, m in orchestra.members.items()
        if (m.allow_contact_sharing and uid != user_id) or user_id == admin_id
    ]

    if not query:
        sorted_members = sorted(members, key=lambda m: m.full_name)
    else:
        sorted_members = sorted(members, key=lambda m: m.compare_full_name_to(query), reverse=True)

    # Telegram only likes up to 50 results
    if len(sorted_members) > (offset + 1) * MEMBERS_PER_PAGE:
        next_offset = offset + 1
        sorted_members = sorted_members[offset * MEMBERS_PER_PAGE:offset * MEMBERS_PER_PAGE
                                        + MEMBERS_PER_PAGE]
    else:
        sorted_members = sorted_members[offset * MEMBERS_PER_PAGE:]

    results = [
        InlineQueryResultArticle(id=m.user_id,
                                 title=m.full_name,
                                 input_message_content=InputTextMessageContent(m.to_str()),
                                 reply_markup=InlineKeyboardMarkup.from_button(
                                     InlineKeyboardButton(text='vCard-Datei anfordern 📇',
                                                          callback_data=REQUEST_CONTACT.format(
                                                              m.user_id)))) for m in sorted_members
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
    admin_id = context.bot_data[ADMIN_KEY]

    uid = int(context.match.group(1))
    orchestra = context.bot_data[ORCHESTRA_KEY]
    member = orchestra.members[uid]
    vcard = member.vcard(context.bot, admin=admin_id == update.effective_user.id)

    update.callback_query.answer()
    update.callback_query.edit_message_reply_markup(reply_markup=None)
    context.bot.send_document(chat_id=update.effective_user.id,
                              document=vcard,
                              filename=member.vcard_filename,
                              caption=member.full_name)
    vcard.close()


SEND_VCARD_HANDLER = CallbackQueryHandler(send_vcard, pattern=REQUEST_CONTACT_PATTERN)
""":class:`telegram.ext.CallbackQueryHandler`: Handler used to send vCards on request."""

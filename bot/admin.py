#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for the admin."""
from telegram import Update
from telegram.ext import CallbackContext

from bot import ORCHESTRA_KEY
from components import Orchestra, Member


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

    for m in members:
        new_member = Member(
            m.user_id,
            phone_number=m.phone_number,
            first_name=m.first_name,
            last_name=m.last_name,
            nickname=m.nickname,
            gender=m.gender,
            date_of_birth=m.date_of_birth,
            instruments=m.instruments,
            address=None,
            photo_file_id=m.photo_file_id,
            allow_contact_sharing=m.allow_contact_sharing,
        )
        new_member.user_score = m.user_score
        new_member.user_score.member = new_member
        new_member._raw_address = m._raw_address
        new_member._address = m._address
        new_member._longitude = m._longitude
        new_member._latitude = m._latitude
        orchestra.register_member(new_member)

    context.bot_data[ORCHESTRA_KEY] = orchestra
    update.message.reply_text('Orchester neu besetzt.')

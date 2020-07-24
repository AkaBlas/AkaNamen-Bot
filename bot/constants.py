#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains several constants for the bot."""

# Bot data keys
ORCHESTRA_KEY = 'orchestra'
""":obj:`str`: Each ``context.bot_data[ORCHESTRA_KEY]`` is expected to be an
:class:`components.Orchestra`."""
PENDING_REGISTRATIONS_KEY = 'pending_registrations'
"""
:obj:`str`: Each ``context.bot_data[PENDING_REGISTRATIONS_KEY]`` is expected to be a dictionary of
type Dict[:obj:`int`, List[:class:`components.Member`]], where each entry represents a user
registration request, which needs to be processed by the admin.
"""
DENIED_USERS_KEY = 'denied_users_key'
"""
:obj:`str`: Each ``context.bot_data[DENIED_USERS_KEY]`` is expected to be a list of user
ids, which were denied registration.
"""
ADMIN_KEY = 'admin_key'
"""
:obj:`str`: Each ``context.bot_data[ADMIN_KEY]`` is expected to be the admins chat id.
"""

# User data keys
EDITING_MESSAGE_KEY = 'editing_message_key'
"""
:obj:`str`: Each ``context.user_data[EDITING_MESSAGE_KEY]`` is expected to be the last
:class:`telegram.Message` with an :class:`telegram.InlineKeyboardMarkup` sent in the process of
editing the members data.
"""

# Callback Data
REGISTRATION_PATTERN = 'requesting_registration'
"""
:obj:`str`: :class:`telegram.CallbackQuery` s with this as ``callback_data`` will trigger a
registration request.
"""

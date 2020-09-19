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
EDITING_USER_KEY = 'editing_user_key'
"""
:obj:`str`: Each ``context.user_data[EDITING_USER_KEY]`` is expected to be the id of a user to be
edited. Only relevant for the admin.
"""
GAME_MESSAGE_KEY = 'game_message_key'
"""
:obj:`str`: Each ``context.user_data[GAME_MESSAGE_KEY]`` is expected to be the last
:class:`telegram.Message` with an :class:`telegram.InlineKeyboardMarkup` sent in the process of
setting up a game.
"""
CANCELLATION_MESSAGE_KEY = 'cancellation_message_key'
"""
:obj:`str`: Each ``context.user_data[CANCELLATION_MESSAGE_KEY]`` is expected to be the last
:class:`telegram.Message` with an :class:`telegram.InlineKeyboardMarkup` sent in the process of
cancelling the members membership.
"""
BANNING_KEY = 'banning_key'
"""
:obj:`str`: Each ``context.user_data[BANNING_KEY]`` is expected to be the last user id of a user
to be banned from the bot.
"""
GAME_KEY = 'game_key'
"""
:obj:`str`: Each ``context.user_data[GAME_KEY]`` is expected to contain information to be used
by :class:`bot.GameHandler`.
"""

# Callback Data
REGISTRATION_PATTERN = 'requesting_registration'
"""
:obj:`str`: :class:`telegram.CallbackQuery` s with this as ``callback_data`` will trigger a
registration request.
"""

# Deep Linking
INLINE_HELP = 'inline_help'
"""
:obj:`str`: If start message with this as deep linking parameter is received, a help message about
the inline mode should be displayed.
"""

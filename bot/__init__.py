#!/usr/bin/env python
"""The Bot module."""

from .constants import (
    ORCHESTRA_KEY,
    PENDING_REGISTRATIONS_KEY,
    DENIED_USERS_KEY,
    REGISTRATION_PATTERN,
    ADMIN_KEY,
    EDITING_MESSAGE_KEY,
    INLINE_HELP,
    CANCELLATION_MESSAGE_KEY,
    BANNING_KEY,
    GAME_KEY,
    GAME_MESSAGE_KEY,
    EDITING_USER_KEY,
    CONVERSATION_KEY,
)

from .keyboards import (
    build_instruments_keyboard,
    parse_instruments_keyboard,
    build_questions_hints_keyboard,
    parse_questions_hints_keyboard,
    REGISTRATION_KEYBOARD,
    DOCS_KEYBOARD,
    DONE,
    SELECTED,
    BACK,
    CHANNEL_KEYBOARD,
    ALL,
)
from .setup import setup

__all__ = [
    # Keyboards
    'build_instruments_keyboard',
    'parse_instruments_keyboard',
    'build_questions_hints_keyboard',
    'parse_questions_hints_keyboard',
    'REGISTRATION_KEYBOARD',
    'DOCS_KEYBOARD',
    'DONE',
    'SELECTED',
    'BACK',
    'CHANNEL_KEYBOARD',
    'ALL',
    # Setup
    'setup',
    # Constants
    'ORCHESTRA_KEY',
    'PENDING_REGISTRATIONS_KEY',
    'DENIED_USERS_KEY',
    'REGISTRATION_PATTERN',
    'ADMIN_KEY',
    'EDITING_MESSAGE_KEY',
    'EDITING_USER_KEY',
    'GAME_MESSAGE_KEY',
    'INLINE_HELP',
    'CANCELLATION_MESSAGE_KEY',
    'BANNING_KEY',
    'GAME_KEY',
    'CONVERSATION_KEY',
]

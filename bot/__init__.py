#!/usr/bin/env python
"""The Bot module."""

from .constants import (
    ORCHESTRA_KEY,
    PENDING_REGISTRATIONS_KEY,
    DENIED_USERS_KEY,
    REGISTRATION_PATTERN,
    ADMIN_KEY,
    EDITING_MESSAGE_KEY,
)
from .keyboards import (build_instruments_keyboard, parse_instruments_keyboard,
                        REGISTRATION_KEYBOARD, DOCS_KEYBOARD, DONE, SELECTED, BACK,
                        CHANNEL_KEYBOARD)
from .setup import register_dispatcher

__all__ = [
    # Keyboards
    'build_instruments_keyboard',
    'parse_instruments_keyboard',
    'REGISTRATION_KEYBOARD',
    'DOCS_KEYBOARD',
    'DONE',
    'SELECTED',
    'BACK',
    'CHANNEL_KEYBOARD',
    # Setup
    'register_dispatcher',
    # Constants
    'ORCHESTRA_KEY',
    'PENDING_REGISTRATIONS_KEY',
    'DENIED_USERS_KEY',
    'REGISTRATION_PATTERN',
    'ADMIN_KEY',
    'EDITING_MESSAGE_KEY'
]

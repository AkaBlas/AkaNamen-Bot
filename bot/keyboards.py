#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for generating often needed keyboards."""
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from components import (Instrument, WoodwindInstrument, BrassInstrument, HighBrassInstrument,
                        LowBrassInstrument, PercussionInstrument, Flute, Clarinet, Oboe, Bassoon,
                        Saxophone, SopranoSaxophone, AltoSaxophone, TenorSaxophone,
                        BaritoneSaxophone, Euphonium, BaritoneHorn, Baritone, Trombone, Tuba,
                        Trumpet, Flugelhorn, Horn, Drums, Guitar, BassGuitar, Conductor, Orchestra)
from bot import REGISTRATION_PATTERN
from typing import Dict, Optional, List

SELECTED = '✔️'
""":obj:`str`: Emoji to use to mark selected options."""
DESELECTED = '❌'
""":obj:`str`: Emoji to use to mark deselected options."""
NEXT_TEXT = 'Weiter ➡️'
"""":obj:`str`: Text to use for buttons leading to the next menu."""
NEXT_DATA = 'NEXT_BUTTON'
"""":obj:`str`: Callback data to use for buttons leading to the next menu."""
REGISTRATION_KEYBOARD = InlineKeyboardMarkup.from_button(
    InlineKeyboardButton(text='Anmeldungs-Anfrage senden ✉️', callback_data=REGISTRATION_PATTERN))
""":class:`telegram.InlineKeyboardMarkup`: Keyboard that triggers the registration process."""
DOCS_KEYBOARD = InlineKeyboardMarkup.from_button(
    InlineKeyboardButton(text='Benutzerhandbuch 📖',
                         url='https://bibo-joshi.github.io/AkaNamen-Bot/'))
""":class:`telegram.InlineKeyboardMarkup`: Keyboard leading to the docs."""
CHANNEL_KEYBOARD = InlineKeyboardMarkup.from_button(
    InlineKeyboardButton(text='Info-Kanal 📣', url='https://t.me/AkaNamenInfo'))
""":class:`telegram.InlineKeyboardMarkup`: Keyboard leading to the info channel."""

# yapf: disable
INSTRUMENT_KEYBOARD: List[List[Instrument]] = [
    [WoodwindInstrument()],
    [Flute(), Clarinet()],
    [Oboe(), Bassoon()],
    [Saxophone()],
    [SopranoSaxophone(), AltoSaxophone()],
    [TenorSaxophone(), BaritoneSaxophone()],
    [BrassInstrument()],
    [HighBrassInstrument()],
    [Trumpet(), Flugelhorn()],
    [Horn()],
    [LowBrassInstrument()],
    [Euphonium(), Baritone()],
    [BaritoneHorn(), Trombone()],
    [Tuba()],
    [Guitar()],
    [BassGuitar()],
    [PercussionInstrument()],
    [Drums()],
    [Conductor()]
]

QUESTION_HINT_KEYBOARD: List[List[str]] = [
    ['first_names', 'last_names'],
    ['full_names', 'nicknames'],
    ['ages', 'birthdays'],
    ['instruments'],
    ['addresses', 'photo_file_ids']
]

# yapf: enable


def build_instruments_keyboard(
        current_selection: Optional[Dict[Instrument, bool]] = None) -> InlineKeyboardMarkup:
    """
    Builds a :class:`telegram.InlineKeyboardMarkup` listing all instruments that are up for
    selection. The callback data for each button will equal its text.
    Also appends a button with the text :attr:`NEXT_TEXT` and data :attr:`NEXT_DATA` at the very
    end of the keyboard.

    Args:
        current_selection: Optional. If passed, gives the current selection and the keyboard will
            reflect that selection state. If not present, all instruments will be deselected.
            A corresponding dictionary is returned e.g. by :meth:`parse_instruments_keyboard`.

    Returns:
        InlineKeyboardMarkup
    """
    current_selection = current_selection or dict()

    buttons = []
    for row in INSTRUMENT_KEYBOARD:
        button_row = []
        for instrument in row:
            text = (f'{instrument} '
                    f'{SELECTED if current_selection.get(instrument) else DESELECTED}')
            button = InlineKeyboardButton(text=text, callback_data=text)
            button_row.append(button)
        buttons.append(button_row)
    buttons.append([InlineKeyboardButton(text=NEXT_TEXT, callback_data=NEXT_DATA)])
    return InlineKeyboardMarkup(buttons)


def parse_instruments_keyboard(keyboard: InlineKeyboardMarkup) -> Dict[Instrument, bool]:
    """
    Parses the given keyboard and returns ad dictionary, indicating for every instrument, whether
    it has been selected or not.

    Args:
        keyboard: The :class:`telegram.InlineKeyboardMarkup` from an update. Buttons must have the
            structure as provided by :meth:`build_instruments_keyboard`.
    """
    current_selection = dict()
    for row in keyboard.inline_keyboard[:-1]:
        for button in row:
            instrument, selection = button.text.split(' ')
            current_selection[Instrument.from_string(instrument)] = selection == SELECTED

    return current_selection


def build_questions_hints_keyboard(
        orchestra: Orchestra,
        question: bool = False,
        hint: bool = False,
        current_selection: Optional[Dict[str, bool]] = None) -> InlineKeyboardMarkup:
    """
    Builds a :class:`telegram.InlineKeyboardMarkup` listing all questions that are up for
    selection for the given orchestra. The callback data for each button will equal its text.
    Also appends a button with the text :attr:`NEXT_TEXT` and data :attr:`NEXT_DATA` at the very
    end of the keyboard.

    Args:
        orchestra: The orchestra to build the keyboard for.
        question: Optional. Set to :obj:`True`, if the keyboard is build for question selection.
        hint: Optional. Set to :obj:`True`, if the keyboard is build for hint selection.
        current_selection: Optional. If passed, gives the current selection and the keyboard will
            reflect that selection state. If not present, all options will be deselected.
            A corresponding dictionary is returned e.g. by :meth:`parse_questions_hints_keyboard`.

    Note:
        Exactly one on :attr:`hint` and :attr:`question` must be :obj:`True`.

    Returns:
        InlineKeyboardMarkup

    Raises:
        RuntimeError: If the orchestra currently has no questionable attributes.
    """
    if question == hint:
        raise ValueError('Exactly one on hint and question must be True.')

    current_selection = current_selection or dict()

    questionable = orchestra.questionable
    if not questionable:
        raise RuntimeError('Orchestra currently has no questionable attributes.')
    hints = [q[0] for q in questionable]
    questions = [q[1] for q in questionable]

    buttons = []
    for row in QUESTION_HINT_KEYBOARD:
        button_row = []
        for option in row:
            if (hint and option not in hints) or (question and option not in questions):
                continue

            text = (f'{Orchestra.DICTS_TO_HR[option]} '
                    f'{SELECTED if current_selection.get(option) else DESELECTED}')
            callback_data = f'{option} {SELECTED if current_selection.get(option) else DESELECTED}'
            button = InlineKeyboardButton(text=text, callback_data=callback_data)
            button_row.append(button)
        if row:
            buttons.append(button_row)
    buttons.append([InlineKeyboardButton(text=NEXT_TEXT, callback_data=NEXT_DATA)])
    return InlineKeyboardMarkup(buttons)


def parse_questions_hints_keyboard(keyboard: InlineKeyboardMarkup) -> Dict[str, bool]:
    """
    Parses the given keyboard and returns ad dictionary, indicating for every option, whether
    it has been selected or not.

    Args:
        keyboard: The :class:`telegram.InlineKeyboardMarkup` from an update. Buttons must have the
            structure as provided by :meth:`build_questions_hints_keyboard`.
    """
    current_selection = dict()
    for row in keyboard.inline_keyboard[:-1]:
        for button in row:
            option, selection = button.callback_data.split(' ')
            current_selection[option] = selection == SELECTED

    return current_selection

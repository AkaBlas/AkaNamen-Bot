#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for generating often needed keyboards."""

from typing import Dict, Optional, List, Iterable
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from components import (
    Instrument,
    PercussionInstrument,
    Flute,
    Clarinet,
    Oboe,
    Bassoon,
    SopranoSaxophone,
    AltoSaxophone,
    TenorSaxophone,
    BaritoneSaxophone,
    Euphonium,
    BaritoneHorn,
    Baritone,
    Trombone,
    Tuba,
    Trumpet,
    Flugelhorn,
    Horn,
    Drums,
    Guitar,
    BassGuitar,
    Conductor,
    Orchestra,
    Member,
)
from bot import REGISTRATION_PATTERN

SELECTED = '✔️'
""":obj:`str`: Emoji to use to mark selected options."""
DESELECTED = '❌'
""":obj:`str`: Emoji to use to mark deselected options."""
REGISTRATION_KEYBOARD = InlineKeyboardMarkup.from_button(
    InlineKeyboardButton(text='Anmeldungs-Anfrage senden ✉️', callback_data=REGISTRATION_PATTERN)
)
""":class:`telegram.InlineKeyboardMarkup`: Keyboard that triggers the registration process."""
DOCS_KEYBOARD = InlineKeyboardMarkup.from_button(
    InlineKeyboardButton(
        text='Benutzerhandbuch 📖', url='https://bibo-joshi.github.io/AkaNamen-Bot/'
    )
)
""":class:`telegram.InlineKeyboardMarkup`: Keyboard leading to the docs."""
CHANNEL_KEYBOARD = InlineKeyboardMarkup.from_column(
    [
        InlineKeyboardButton(text='Info-Kanal 📣', url='https://t.me/AkaNamenInfo'),
        InlineKeyboardButton(
            text='Benutzerhandbuch 📖', url='https://bibo-joshi.github.io/AkaNamen-Bot/'
        ),
    ]
)
""":class:`telegram.InlineKeyboardMarkup`: Keyboard leading to the info channel and the docs."""
BACK = 'Zurück'
""":obj:`str`: Text indicating a 'back' action. Use as text or callback data."""
DONE = 'Fertig'
""":obj:`str`: Text indicating a 'done' action. Use as text or callback data."""
ALL = 'Alles'
""":obj:`str`: Text indicating to select all. Use as text or callback data."""

INSTRUMENT_KEYBOARD: List[List[Instrument]] = [
    [Flute(), Clarinet()],
    [Oboe(), Bassoon()],
    [SopranoSaxophone(), AltoSaxophone()],
    [TenorSaxophone(), BaritoneSaxophone()],
    [Trumpet(), Flugelhorn()],
    [Horn()],
    [Euphonium(), Baritone()],
    [BaritoneHorn(), Trombone()],
    [Tuba()],
    [Guitar(), BassGuitar()],
    [PercussionInstrument(), Drums()],
    [Conductor()],
]

QUESTION_HINT_KEYBOARD: List[List[str]] = [
    ['first_name', 'last_name'],
    ['full_name', 'nickname'],
    ['age', 'birthday'],
    ['instruments', 'joined'],
    ['address', 'photo_file_id'],
    ['functions'],
]


def build_instruments_keyboard(
    current_selection: Optional[Dict[Instrument, bool]] = None
) -> InlineKeyboardMarkup:
    """
    Builds a :class:`telegram.InlineKeyboardMarkup` listing all instruments that are up for
    selection. The callback data for each button will equal its text.
    Also appends a button with the text :attr:`DONE` and data :attr:`DONE` at the very
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
            text = f'{instrument} {SELECTED if current_selection.get(instrument) else DESELECTED}'
            button = InlineKeyboardButton(text=text, callback_data=text)
            button_row.append(button)
        buttons.append(button_row)
    buttons.append([InlineKeyboardButton(text=DONE, callback_data=DONE)])
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
            key = Instrument.from_string(instrument, allowed=Member.ALLOWED_INSTRUMENTS)
            if key is not None:
                current_selection[key] = selection == SELECTED

    return current_selection


def build_questions_hints_keyboard(
    orchestra: Orchestra,
    question: bool = False,
    hint: bool = False,
    current_selection: Optional[Dict[str, bool]] = None,
    multiple_choice: bool = True,
    allowed_hints: List[str] = None,
    exclude_members: Iterable[Member] = None,
) -> InlineKeyboardMarkup:
    """
    Builds a :class:`telegram.InlineKeyboardMarkup` listing all questions that are up for
    selection for the given orchestra. The callback data for each button will equal its text.
    Also appends a button with the text :attr:`DONE` and data :attr:`DONE` at the very
    end of the keyboard.

    Args:
        orchestra: The orchestra to build the keyboard for.
        question: Optional. Set to :obj:`True`, if the keyboard is build for question selection.
        hint: Optional. Set to :obj:`True`, if the keyboard is build for hint selection.
        current_selection: Optional. If passed, gives the current selection and the keyboard will
            reflect that selection state. If not present, all options will be deselected.
            A corresponding dictionary is returned e.g. by :meth:`parse_questions_hints_keyboard`.
        multiple_choice: Optional. Whether the questions are supposed to be multiple choice or free
            text. Defaults to :obj:`True`.
        allowed_hints: Optional. Only relevant if :obj:`question` is :obj:`True`. If passed, in
            this case only question attributes which are questionable for at least one of the
            allowed hints will be listed in the keyboard.
        exclude_members: Optional. Members to exclude from serving as hint.

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

    questionable = orchestra.questionable(
        multiple_choice=multiple_choice, exclude_members=exclude_members
    )
    if not questionable:
        raise RuntimeError('Orchestra currently has no questionable attributes.')
    hints = [q[0].description for q in questionable]

    if question and allowed_hints:
        questions = [q[1].description for q in questionable if q[0] in allowed_hints]
    else:
        questions = [q[1].description for q in questionable]

    buttons = []
    any_selected = False
    for row in QUESTION_HINT_KEYBOARD:
        button_row = []
        for option in row:
            if (hint and option not in hints) or (question and option not in questions):
                continue

            text = (
                f'{Orchestra.TO_HR[option]} '
                f'{SELECTED if current_selection.get(option) else DESELECTED}'
            )
            callback_data = f'{option} {SELECTED if current_selection.get(option) else DESELECTED}'
            button = InlineKeyboardButton(text=text, callback_data=callback_data)
            button_row.append(button)

            if current_selection.get(option):
                any_selected = True
        if row:
            buttons.append(button_row)
    if any_selected:
        buttons.append(
            [
                InlineKeyboardButton(text=ALL, callback_data=ALL),
                InlineKeyboardButton(text=DONE, callback_data=DONE),
            ]
        )
    else:
        buttons.append([InlineKeyboardButton(text=ALL, callback_data=DONE)])
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

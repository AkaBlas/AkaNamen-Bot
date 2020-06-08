#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for generating often needed keyboards."""
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from components import (Instrument, WoodwindInstrument, BrassInstrument, HighBrassInstrument,
                        LowBrassInstrument, PercussionInstrument, Flute, Clarinet, Oboe, Bassoon,
                        Saxophone, SopranoSaxophone, AltoSaxophone, TenorSaxophone,
                        BaritoneSaxophone, Euphonium, BaritoneHorn, Baritone, Trombone, Tuba,
                        Trumpet, Flugelhorn, Horn, Drums, Guitar, BassGuitar)

from typing import Dict, Optional, List

SELECTED = '✔️'
""":obj:`str`: Emoji to use to mark selected options."""
DESELECTED = '❌'
""":obj:`str`: Emoji to use to mark deselected options."""
NEXT_TEXT = 'Weiter ➡️'
"""":obj:`str`: Text to use for buttons leading to the next menu."""
NEXT_DATA = 'NEXT_BUTTON'
"""":obj:`str`: Callback data to use for buttons leading to the next menu."""

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
]


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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for showing the highscore."""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler

from bot import ORCHESTRA_KEY
from components import Orchestra

OVERALL_SCORE = 'overall highscore'
""":obj:`str`: Callback data for the overall score."""
TODAYS_SCORE = 'todays highscore'
""":obj:`str`: Callback data for todays score."""
WEEKS_SCORE = 'weeks highscore'
""":obj:`str`: Callback data for the weekly score."""
MONTHS_SCORE = 'months highscore'
""":obj:`str`: Callback data for the monthly score."""
YEARS_SCORE = 'years highscore'
""":obj:`str`: Callback data for the yearly score."""
CURRENT = 'current highscore'
""":obj:`str` Callback data for the current view."""

HEADINGS = {
    OVERALL_SCORE: 'Highscore:',
    TODAYS_SCORE: 'Highscore von heute:',
    WEEKS_SCORE: 'Highscore der aktuellen Woche:',
    MONTHS_SCORE: 'Highscore des aktuellen Monats:',
    YEARS_SCORE: 'Highscore des aktuellen Jahres:',
}
"""Dict[str, str]: Mapping giving for each callback data a corresponding heading for the message.
"""

BUTTON_TEXTS = {
    OVERALL_SCORE: 'Gesamter Highscore',
    TODAYS_SCORE: 'Heute',
    WEEKS_SCORE: 'Woche',
    MONTHS_SCORE: 'Monats',
    YEARS_SCORE: 'Jahr',
}
"""Dict[str, str]: Mapping giving for each callback data a corresponding text for the keyboard.
"""


def build_keyboard(view: str = OVERALL_SCORE) -> InlineKeyboardMarkup:
    """
    Builds the keyboard for the highscore message.

    Args:
        view: One of attr:`OVERALL_SCORE`, attr:`TODAYS_SCORE`: 'Highscore von heute:',
            attr:`WEEKS_SCORE`, attr:`MONTHS_SCORE` and attr:`YEARS_SCORE`. The corresponding
            button will have :attr:`CURRENT` as data. Defaults to :attr:`OVERALL_SCORE`.
    """
    data = {k: k if k != view else CURRENT for k in BUTTON_TEXTS.keys()}
    # yapf: disable
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_TEXTS[OVERALL_SCORE], callback_data=data[OVERALL_SCORE])],
        [
            InlineKeyboardButton(BUTTON_TEXTS[TODAYS_SCORE], callback_data=data[TODAYS_SCORE]),
            InlineKeyboardButton(BUTTON_TEXTS[WEEKS_SCORE], callback_data=data[WEEKS_SCORE])
        ],
        [
            InlineKeyboardButton(BUTTON_TEXTS[MONTHS_SCORE], callback_data=data[MONTHS_SCORE]),
            InlineKeyboardButton(BUTTON_TEXTS[YEARS_SCORE], callback_data=data[YEARS_SCORE])
        ]])
    # yapf: enable


def build_text(orchestra: Orchestra, interval: str) -> str:
    """
    Builds the highscore text for an orchestra for the given interval.

    Args:
        orchestra: The orchestra to get the score from.
        interval: The requested interval.
    """
    method = getattr(orchestra, "{}_score_text".format(interval))
    return f'<b>{HEADINGS["{} highscore".format(interval)]}</b>\n\n{method(length=10, html=True)}'


def show_highscore(update: Update, context: CallbackContext) -> None:
    """
    Shows the current highscore with an option to switch between daily, weekly, monthly, yearly and
    overall score.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    orchestra = context.bot_data[ORCHESTRA_KEY]

    if update.message:
        update.message.reply_text(text=build_text(orchestra, 'overall'),
                                  reply_markup=build_keyboard())
    else:
        data = update.callback_query.data
        if data != CURRENT:
            update.callback_query.answer()
            update.effective_message.edit_text(text=build_text(orchestra,
                                                               context.matches[0].group(1)),
                                               reply_markup=build_keyboard(data))
        else:
            update.callback_query.answer(text='Wird bereits angezeigt.', show_alert=True)


HIGHSCORE_HANDLER = CallbackQueryHandler(show_highscore, pattern=r'(\w*) highscore')
""":class:`telegram.ext.CallbackQueryHandler`: Handler used to switch between the highscores."""

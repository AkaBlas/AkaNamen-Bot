#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for handling simple commands."""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from bot import ORCHESTRA_KEY, CHANNEL_KEYBOARD


def show_data(update: Update, context: CallbackContext) -> None:
    """
    Shows the users currently saved data.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    orchestra = context.bot_data[ORCHESTRA_KEY]
    member = orchestra.members[update.effective_user.id]

    text = (f'Aktuell habe ich folgendes über Dich gespeichert:\n\n{member.to_str()}\n\n'
            'Um diese Daten zu bearbeiten, nutze den Befehl /daten_bearbeiten.')
    update.message.reply_text(text=text)


def help_message(update: Update, context: CallbackContext) -> None:
    """
    Shows a simple help message.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    text = ('Okay, lass mich versuchen, Dir zu helfen. Folgende Infos sind vielleicht '
            'nützlich:\n\n• Eine Übersicht der verfügbaren Befehle siehst Du, wenn Du unten '
            'rechts auf das »<code>/</code>« Symbol klickst.\n\n• Eine ausführliche Erklärung '
            'meiner Funktionen findest Du im Benutzerhandbuch (s. unten)\n\n• Dort findest Du auch'
            ' viele Antworten z.B. bezüglich Verwendung der Daten.\n\n• Neuigkeiten zum'
            ' AkaNamen-Bot werden über den Channel (s. unten) bekanntgegeben. Tritt gerne bei!\n\n'
            '• Im Zweifel lieber noch ein bisschen mehr Gurkenwasser an den Labskaus geben.\n\n• '
            'Wenn der Schnee gelb ist, solltest Du ihn lieber nicht essen.\n\n• Ein bisschen Hello'
            ' Dolly hat noch nie geschadet!')
    update.message.reply_text(text=text, reply_markup=CHANNEL_KEYBOARD)


def start_inline(update: Update, context: CallbackContext) -> None:
    """
    Helps the user find the inline mode.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    text = ('Über den AkaNamen-Bot kannst Du Kontaktdaten von anderen AkaBlas abrufen, '
            'sofern diese das erlauben. Das geht so:\n\n1. Drücke auf den Knopf unten. In deinem '
            'Textfeld erscheint dann »<code>@AkaNamenBot ...</code>«.\n2. Gib den '
            'Namen/Spitznamen des AkaBlasen ein, den Du suchst. Dir wird eine Liste von '
            'Vorschlägen gezeigt.\n3. Klicke auf den gewünschten AkaBlasen. Im Chat erscheinen '
            'dann die Kontaktdaten.\n\n<i>PS:</i> Damit Du '
            'auf diese Art von anderen AkaBlasen gefunden werden kannst, musst Du unter '
            '/daten_bearbeiten ➜ Datennutzung zustimmen. ')
    update.message.reply_text(text=text,
                              reply_markup=InlineKeyboardMarkup.from_button(
                                  InlineKeyboardButton(text='Klick mich! 🙂',
                                                       switch_inline_query_current_chat='')))

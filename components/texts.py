#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains functions for generating often needed texts."""
import random
from components import Question
from typing import Optional, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from components import Member  # noqa: F401

MULTIPLE_CHOICE_QUESTIONS = {
    Question.FIRST_NAME: {
        Question.ADDRESS: 'Wo wohnt {hint}?',
        Question.BIRTHDAY: 'An welchem Tag hat {hint} Geburtstag?',
        Question.AGE: 'Wie alt ist {hint}?',
        Question.INSTRUMENT: 'Welches dieser Instrumente spielt {hint} (ggf. unter anderem)?',
        Question.LAST_NAME: 'Wie lautet der Nachname von {hint}?',
        Question.NICKNAME: 'Wie lautet der Spitzname von {hint}?',
        Question.FULL_NAME: 'Wie lautet der volle Name von {hint}?',
        Question.PHOTO: 'Welches Bild zeigt {hint}?',
    },
    Question.LAST_NAME: {
        Question.ADDRESS: 'Wo wohnt {hint}?',
        Question.BIRTHDAY: 'An welchem Tag hat {hint} Geburtstag?',
        Question.AGE: 'Wie alt ist {hint}?',
        Question.INSTRUMENT: 'Welches dieser Instrumente spielt {hint} (ggf. unter anderem)?',
        Question.FIRST_NAME: 'Wie lautet der Vorname von {hint}?',
        Question.NICKNAME: 'Wie lautet der Spitzname von {hint}?',
        Question.FULL_NAME: 'Wie lautet der volle Name von {hint}?',
        Question.PHOTO: 'Welches Bild zeigt {hint}?',
    },
    Question.NICKNAME: {
        Question.ADDRESS: 'Wo wohnt {hint}?',
        Question.BIRTHDAY: 'An welchem Tag hat {hint} Geburtstag?',
        Question.AGE: 'Wie alt ist {hint}?',
        Question.INSTRUMENT: 'Welches dieser Instrumente spielt {hint} (ggf. unter anderem)?',
        Question.FIRST_NAME: 'Wie lautet der Vorname von {hint}?',
        Question.LAST_NAME: 'Wie lautet der Nachname von {hint}?',
        Question.FULL_NAME: 'Wie lautet der volle Name von {hint}?',
        Question.PHOTO: 'Welches Bild zeigt {hint}?',
    },
    Question.FULL_NAME: {
        Question.FIRST_NAME: 'Wie lautet der Vorname von {hint}?',
        Question.LAST_NAME: 'Wie lautet der Nachname von {hint}?',
        Question.NICKNAME: 'Wie lautet der Spitzname von {hint}?',
        Question.ADDRESS: 'Wo wohnt {hint}?',
        Question.BIRTHDAY: 'An welchem Tag hat {hint} Geburtstag?',
        Question.AGE: 'Wie alt ist {hint}?',
        Question.INSTRUMENT: 'Welches dieser Instrumente spielt {hint} (ggf. unter anderem)?',
        Question.PHOTO: 'Welches Bild zeigt {hint}?',
    },
    Question.BIRTHDAY: {
        Question.FIRST_NAME: 'Wer hat am {hint} Geburtstag?',
        Question.LAST_NAME: 'Wer hat am {hint} Geburtstag?',
        Question.NICKNAME: 'Wer hat am {hint} Geburtstag?',
        Question.FULL_NAME: 'Wer hat am {hint} Geburtstag?',
        Question.AGE: 'Wie alt ist das Mitglied von AkaBlas, das am {hint} Geburtstag hat?',
        Question.INSTRUMENT: ('Welches Instrument wird von einem Mitglied von AkaBlas gespielt, '
                              'das am {hint} Geburtstag hat?'),
        Question.ADDRESS: 'Wo wohnt ein Mitglied von AkaBlas, das am {hint} Geburtstag hat?',
        Question.PHOTO: 'Welches Bild zeigt das AkaBlas-Mitglied, das am {hint} Geburtstag hat?',
    },
    Question.AGE: {
        Question.FIRST_NAME: 'Wer ist {hint} Jahre alt?',
        Question.LAST_NAME: 'Wer ist {hint} Jahre alt?',
        Question.NICKNAME: 'Wer ist {hint} Jahre alt?',
        Question.FULL_NAME: 'Wer ist {hint} Jahre alt?',
        Question.BIRTHDAY: ('Wann hat das Mitglied von AkaBlas Geburtstag, das jetzt {hint} Jahre '
                            'alt ist?'),
        Question.INSTRUMENT: ('Welches Instrument wird von einem Mitglied von AkaBlas gespielt, '
                              'das jetzt {hint} Jahre alt ist?'),
        Question.ADDRESS: 'Wo wohnt ein Mitglied von AkaBlas, das jetzt {hint} Jahre alt ist?',
        Question.PHOTO: 'Welches Bild zeigt das AkaBlas-Mitglied, das {hint} Jahre alt ist?',
    },
    Question.INSTRUMENT: {
        Question.FIRST_NAME:
            'Wer spielt (ggf. unter anderem) {hint}?',
        Question.LAST_NAME:
            'Wer spielt (ggf. unter anderem) {hint}?',
        Question.NICKNAME:
            'Wer spielt (ggf. unter anderem) {hint}?',
        Question.FULL_NAME:
            'Wer spielt (ggf. unter anderem) {hint}?',
        Question.BIRTHDAY: ('Wann hat das Mitglied von AkaBlas Geburtstag, das (ggf. unter '
                            'unter anderem) {hint} spielt?'),
        Question.AGE: ('Wie alt is ein Mitglied von AkaBlas, das (ggf. unter anderem) '
                       '{hint} spielt?'),
        Question.ADDRESS: ('Wo wohnt ein Mitglied von AkaBlas, das (ggf. unter anderem) {hint} '
                           'spielt?'),
        Question.PHOTO: ('Welches Bild zeigt das Akablas-Mitglied, das (ggf. unter anderem) '
                         '{hint} spielt?'),
    },
    Question.ADDRESS: {
        Question.FIRST_NAME:
            'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}?',
        Question.LAST_NAME:
            'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}?',
        Question.NICKNAME:
            'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}?',
        Question.FULL_NAME:
            'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}?',
        Question.BIRTHDAY: ('Wann hat das Mitglied von AkaBlas Geburtstag, das bei dieser Adresse '
                            'wohnt: {hint}?'),
        Question.AGE: ('Wie alt ist das Mitglied von AkaBlas, das bei dieser Adresse wohnt: '
                       '{hint}?'),
        Question.INSTRUMENT: ('Welches Instrument wird von einem Mitglied von AkaBlas gespielt, '
                              'das bei dieser Adresse wohnt: {hint}?'),
        Question.PHOTO:
            'Welches Bild zeigt das AkaBlas-Mitglied, dass Du bei dieser Adresse triffst: {hint}?',
    },
    Question.PHOTO: {
        Question.ADDRESS: 'Wo wohnt dieses AkaBlas-Mitglied?',
        Question.BIRTHDAY: 'An welchem Tag hat dieses AkaBlas-Mitglied Geburtstag?',
        Question.AGE: 'Wie alt ist dieses AkaBlas-Mitglied?',
        Question.INSTRUMENT: ('Welches dieser Instrumente spielt dieses AkaBlas-Mitglied '
                              '(ggf. unter anderem)?'),
        Question.FIRST_NAME: 'Wie lautet der Vorname dieses AkaBlas-Mitglieds?',
        Question.LAST_NAME: 'Wie lautet der Nachname dieses AkaBlas-Mitglieds?',
        Question.NICKNAME: 'Wie lautet der Spitzname dieses AkaBlas-Mitglieds?',
        Question.FULL_NAME: 'Wie lautet der volle Name dieses AkaBlas-Mitglieds?',
    }
}

FREE_TEXT_QUESTIONS = {
    Question.FIRST_NAME: {
        Question.ADDRESS: 'Wo wohnt {hint}?',
        Question.BIRTHDAY: ('An welchem Tag hat {hint} Geburtstag? Bitte gib das Datum im Format '
                            '"TT.MM." ein.'),
        Question.AGE: 'Wie alt ist {hint}?',
        Question.INSTRUMENT: 'Welches Instrument spielt {hint} (ggf. unter anderem)?',
        Question.LAST_NAME: 'Wie lautet der Nachname von {hint}?',
        Question.NICKNAME: 'Wie lautet der Spitzname von {hint}?',
        Question.FULL_NAME: 'Wie lautet der volle Name von {hint}?',
    },
    Question.LAST_NAME: {
        Question.ADDRESS: 'Wo wohnt {hint}?',
        Question.BIRTHDAY: ('An welchem Tag hat {hint} Geburtstag? Bitte gib das Datum im Format '
                            '"TT.MM." ein.'),
        Question.AGE: 'Wie alt ist {hint}?',
        Question.INSTRUMENT: 'Welches Instrument spielt {hint} (ggf. unter anderem)?',
        Question.FIRST_NAME: 'Wie lautet der Vorname von {hint}?',
        Question.NICKNAME: 'Wie lautet der Spitzname von {hint}?',
        Question.FULL_NAME: 'Wie lautet der volle Name von {hint}?',
    },
    Question.NICKNAME: {
        Question.ADDRESS: 'Wo wohnt {hint}?',
        Question.BIRTHDAY: ('An welchem Tag hat {hint} Geburtstag? Bitte gib das Datum im Format '
                            '"TT.MM." ein.'),
        Question.AGE: 'Wie alt ist {hint}?',
        Question.INSTRUMENT: 'Welches Instrument spielt {hint} (ggf. unter anderem)?',
        Question.FIRST_NAME: 'Wie lautet der Vorname von {hint}?',
        Question.LAST_NAME: 'Wie lautet der Nachname von {hint}?',
        Question.FULL_NAME: 'Wie lautet der volle Name von {hint}?',
    },
    Question.FULL_NAME: {
        Question.FIRST_NAME: 'Wie lautet der Vorname von {hint}?',
        Question.LAST_NAME: 'Wie lautet der Nachname von {hint}?',
        Question.NICKNAME: 'Wie lautet der Spitzname von {hint}?',
        Question.ADDRESS: 'Wo wohnt {hint}?',
        Question.BIRTHDAY: ('An welchem Tag hat {hint} Geburtstag? Bitte gib das Datum im Format '
                            '"TT.MM." ein.'),
        Question.AGE: 'Wie alt ist {hint}?',
        Question.INSTRUMENT: 'Welches Instrument spielt {hint} (ggf. unter anderem)?',
    },
    Question.BIRTHDAY: {
        Question.FIRST_NAME: 'Wer hat am {hint} Geburtstag? (Vorname)',
        Question.LAST_NAME: 'Wer hat am {hint} Geburtstag? (Nachname)',
        Question.NICKNAME: 'Wer hat am {hint} Geburtstag? (Spitzname)',
        Question.FULL_NAME: 'Wer hat am {hint} Geburtstag? (Ganzer Name)',
        Question.AGE: 'Wie alt ist das Mitglied von AkaBlas, das am {hint} Geburtstag hat?',
        Question.INSTRUMENT: ('Welches Instrument wird von einem Mitglied von AkaBlas gespielt, '
                              'das am {hint} Geburtstag hat?'),
        Question.ADDRESS: 'Wo wohnt ein Mitglied von AkaBlas, das am {hint} Geburtstag hat?'
    },
    Question.AGE: {
        Question.FIRST_NAME: 'Wer ist {hint} Jahre alt? (Vorname)',
        Question.LAST_NAME: 'Wer ist {hint} Jahre alt? (Nachname)',
        Question.NICKNAME: 'Wer ist {hint} Jahre alt? (Spitzname)',
        Question.FULL_NAME: 'Wer ist {hint} Jahre alt? (Ganzer Name)',
        Question.BIRTHDAY: ('Wann hat das Mitglied von AkaBlas Geburtstag, das jetzt {hint} Jahre '
                            'alt ist? Bitte gib das Datum im Format "TT.MM." ein.'),
        Question.INSTRUMENT: ('Welches Instrument wird von einem Mitglied von AkaBlas gespielt, '
                              'das jetzt {hint} Jahre alt ist?'),
        Question.ADDRESS: 'Wo wohnt ein Mitglied von AkaBlas, das jetzt {hint} Jahre alt ist?'
    },
    Question.INSTRUMENT: {
        Question.FIRST_NAME:
            'Wer spielt (ggf. unter anderem) {hint}? (Vorname)',
        Question.LAST_NAME:
            'Wer spielt (ggf. unter anderem) {hint}? (Nachname)',
        Question.NICKNAME:
            'Wer spielt (ggf. unter anderem) {hint}? (Spitzname)',
        Question.FULL_NAME:
            'Wer spielt (ggf. unter anderem) {hint}? (Ganzer Name)',
        Question.BIRTHDAY: ('Wann hat das Mitglied von AkaBlas Geburtstag, das (ggf. unter '
                            'unter anderem) {hint} spielt?  Bitte gib das Datum im Format '
                            '"TT.MM." ein.'),
        Question.AGE: ('Wie alt ist das Mitglied von AkaBlas, das (ggf. unter anderem) '
                       '{hint} spielt?'),
        Question.ADDRESS: ('Wo wohnt ein Mitglied von AkaBlas, das (ggf. unter anderem) {hint} '
                           'spielt?')
    },
    Question.ADDRESS: {
        Question.FIRST_NAME:
            'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}? (Vorname)',
        Question.LAST_NAME:
            'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}? (Nachname)',
        Question.NICKNAME:
            'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}? (Spitzname)',
        Question.FULL_NAME:
            'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}? (Ganzer Name)',
        Question.BIRTHDAY: ('Wann hat das Mitglied von AkaBlas Geburtstag, das bei dieser Adresse '
                            'wohnt: {hint}? Bitte gib das Datum im Format "TT.MM." ein.'),
        Question.AGE: ('Wie alt ist das Mitglied von AkaBlas, das bei dieser Adresse wohnt: '
                       '{hint}?'),
        Question.INSTRUMENT: ('Welches Instrument wird von einem Mitglied von AkaBlas gespielt, '
                              'das bei dieser Adresse wohnt: {hint}?')
    },
    Question.PHOTO: {
        Question.ADDRESS: 'Wo wohnt dieses AkaBlas-Mitglied?',
        Question.BIRTHDAY:
            ('An welchem Tag hat dieses AkaBlas-Mitglied Geburtstag?  Bitte gib das '
             'Datum im Format "TT.MM." ein.'),
        Question.AGE: 'Wie alt ist dieses AkaBlas-Mitglied?',
        Question.INSTRUMENT: ('Welches Instrument spielt dieses AkaBlas-Mitglied '
                              '(ggf. unter anderem)?'),
        Question.FIRST_NAME: 'Wie lautet der Vorname dieses AkaBlas-Mitglieds?',
        Question.LAST_NAME: 'Wie lautet der Nachname dieses AkaBlas-Mitglieds?',
        Question.NICKNAME: 'Wie lautet der Spitzname dieses AkaBlas-Mitglieds?',
        Question.FULL_NAME: 'Wie lautet der volle Name dieses AkaBlas-Mitglieds?',
    }
}


def question_text(member: 'Member',
                  question_attribute: str,
                  hint_attribute: str,
                  multiple_choice: Optional[bool] = True,
                  hint_value: Any = None) -> str:
    """
    Gives the question text for the question specified by the parameters.

    Args:
        member: The orchestra member with the correct answer.
        question_attribute: The attribute that is asked for. One of
            :attr:`components.Question.SUPPORTED_ATTRIBUTES`.
        hint_attribute: The attribute to give as a hint.
        multiple_choice: Whether this is a multiple choice question. Defaults to :obj:`True`.
        hint_value: Optional. A specific value to use as hint. Useful if the hint attribute is a
            list.
    """

    if question_attribute not in Question.SUPPORTED_ATTRIBUTES:
        raise ValueError('Unsupported question_attribute!')
    if hint_attribute not in Question.SUPPORTED_ATTRIBUTES:
        raise ValueError('Unsupported hint_attribute!')

    if question_attribute == Question.PHOTO and not multiple_choice:
        raise ValueError('Photos are only supported as multiple choice questions.')

    if not hint_value:
        hint = member[hint_attribute]
        if isinstance(hint, list):
            hint = str(random.choice(hint))
        hint_value = hint

    if multiple_choice:
        q = MULTIPLE_CHOICE_QUESTIONS[hint_attribute][question_attribute]
    else:
        q = FREE_TEXT_QUESTIONS[hint_attribute][question_attribute]

    return q.format(hint=hint_value)


PHOTO_OPTIONS = ['Oben links', 'Oben rechts', 'Unten links', 'Unten rechts']
"""
List[:obj:`str`]: Poll options to present when the question attribute is
:attr:`components.Question.PHOTO`.
"""

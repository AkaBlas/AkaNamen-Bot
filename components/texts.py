#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains functions for generating often needed texts."""
import random
from typing import Optional, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from components import Member  # noqa: F401

from components import Question  # pylint: disable=C0413

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
        Question.JOINED: 'Seit welchem Jahr ist {hint} bei AkaBlas?',
        Question.FUNCTIONS: 'Welches Amt hat {hint} (ggf. unter anderem) inne?',
    },
    Question.LAST_NAME: {
        Question.ADDRESS: 'Wo wohnt ein Mitglied von AkaBlas mit Nachnamen {hint}?',
        Question.BIRTHDAY: 'An welchem Tag hat ein Mitglied von AkaBlas mit Nachnamen {hint} '
        'Geburtstag?',
        Question.AGE: 'Wie alt ist ein Mitglied von AkaBlas mit Nachnamen {hint}?',
        Question.INSTRUMENT: 'Welches dieser Instrumente spielt ein Mitglied von AkaBlas mit '
        'Nachnamen {hint} (ggf. unter anderem)?',
        Question.FIRST_NAME: 'Wie lautet der Vorname eines Mitglieds von AkaBlas mit '
        'Nachnamen {hint}?',
        Question.NICKNAME: 'Wie lautet der Spitzname eines Mitglieds von AkaBlas mit Nachnamen {'
        'hint}?',
        Question.FULL_NAME: 'Wie lautet der volle Name eines Mitglieds von AkaBlas mit Nachnamen '
        '{hint}?',
        Question.PHOTO: 'Welches Bild zeigt ein Mitglied von AkaBlas mit Nachnamen {hint}?',
        Question.JOINED: 'Seit welchem Jahr ist ein Mitglied von AkaBlas mit Nachnamen {hint} '
        'bei AkaBlas?',
        Question.FUNCTIONS: 'Welches Amt hat ein Mitglied von AkaBlas mit Nachnamen {hint} (ggf. '
        'unter anderem) inne?',
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
        Question.JOINED: 'Seit welchem Jahr ist {hint} bei AkaBlas?',
        Question.FUNCTIONS: 'Welches Amt hat {hint} (ggf. unter anderem) inne?',
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
        Question.JOINED: 'Seit welchem Jahr ist {hint} bei AkaBlas?',
        Question.FUNCTIONS: 'Welches Amt hat {hint} (ggf. unter anderem) inne?',
    },
    Question.BIRTHDAY: {
        Question.FIRST_NAME: 'Wer hat am {hint} Geburtstag?',
        Question.LAST_NAME: 'Wer hat am {hint} Geburtstag?',
        Question.NICKNAME: 'Wer hat am {hint} Geburtstag?',
        Question.FULL_NAME: 'Wer hat am {hint} Geburtstag?',
        Question.AGE: 'Wie alt ist das Mitglied von AkaBlas, das am {hint} Geburtstag hat?',
        Question.INSTRUMENT: (
            'Welches Instrument wird von einem Mitglied von AkaBlas gespielt, '
            'das am {hint} Geburtstag hat?'
        ),
        Question.ADDRESS: 'Wo wohnt ein Mitglied von AkaBlas, das am {hint} Geburtstag hat?',
        Question.PHOTO: 'Welches Bild zeigt das AkaBlas-Mitglied, das am {hint} Geburtstag hat?',
        Question.JOINED: 'Seit welchem Jahr ist ein AkaBlas-Mitglied bei AkaBlas, das am {hint} '
        'Geburtstag hat?',
        Question.FUNCTIONS: 'Welches Amt hat ein Mitglied ven AkaBlas (ggf. unter anderem) inne, '
        'das am {hint} Geburtstag hat?',
    },
    Question.AGE: {
        Question.FIRST_NAME: 'Wer ist {hint} Jahre alt?',
        Question.LAST_NAME: 'Wer ist {hint} Jahre alt?',
        Question.NICKNAME: 'Wer ist {hint} Jahre alt?',
        Question.FULL_NAME: 'Wer ist {hint} Jahre alt?',
        Question.BIRTHDAY: (
            'Wann hat das Mitglied von AkaBlas Geburtstag, das jetzt {hint} Jahre alt ist?'
        ),
        Question.INSTRUMENT: (
            'Welches Instrument wird von einem Mitglied von AkaBlas gespielt, '
            'das jetzt {hint} Jahre alt ist?'
        ),
        Question.ADDRESS: 'Wo wohnt ein Mitglied von AkaBlas, das jetzt {hint} Jahre alt ist?',
        Question.PHOTO: 'Welches Bild zeigt das AkaBlas-Mitglied, das {hint} Jahre alt ist?',
        Question.JOINED: 'Seit welchem Jahr ist ein AkaBlas-Mitglied bei AkaBlas, das {hint} '
        'Jahre alt ist?',
        Question.FUNCTIONS: 'Welches Amt hat ein Mitglied ven AkaBlas (ggf. unter anderem) inne, '
        'das {hint} Jahre alt hat?',
    },
    Question.INSTRUMENT: {
        Question.FIRST_NAME: 'Wer spielt (ggf. unter anderem) {hint}?',
        Question.LAST_NAME: 'Wer spielt (ggf. unter anderem) {hint}?',
        Question.NICKNAME: 'Wer spielt (ggf. unter anderem) {hint}?',
        Question.FULL_NAME: 'Wer spielt (ggf. unter anderem) {hint}?',
        Question.BIRTHDAY: (
            'Wann hat das Mitglied von AkaBlas Geburtstag, das (ggf. unter '
            'unter anderem) {hint} spielt?'
        ),
        Question.AGE: (
            'Wie alt is ein Mitglied von AkaBlas, das (ggf. unter anderem) {hint} spielt?'
        ),
        Question.ADDRESS: (
            'Wo wohnt ein Mitglied von AkaBlas, das (ggf. unter anderem) {hint} spielt?'
        ),
        Question.PHOTO: (
            'Welches Bild zeigt das Akablas-Mitglied, das (ggf. unter anderem) {hint} spielt?'
        ),
        Question.JOINED: 'Seit welchem Jahr ist ein AkaBlas-Mitglied bei AkaBlas, das '
        '(ggf. unter anderem) {hint} spielt?',
        Question.FUNCTIONS: 'Welches Amt hat ein Mitglied ven AkaBlas (ggf. unter anderem) inne, '
        'das (ggf. unter anderem) {hint} spielt?',
    },
    Question.ADDRESS: {
        Question.FIRST_NAME: 'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}?',
        Question.LAST_NAME: 'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}?',
        Question.NICKNAME: 'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}?',
        Question.FULL_NAME: 'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}?',
        Question.BIRTHDAY: (
            'Wann hat das Mitglied von AkaBlas Geburtstag, das bei dieser Adresse '
            'wohnt: {hint}?'
        ),
        Question.AGE: (
            'Wie alt ist das Mitglied von AkaBlas, das bei dieser Adresse wohnt: {hint}?'
        ),
        Question.INSTRUMENT: (
            'Welches Instrument wird von einem Mitglied von AkaBlas gespielt, '
            'das bei dieser Adresse wohnt: {hint}?'
        ),
        Question.PHOTO: 'Welches Bild zeigt das AkaBlas-Mitglied, dass Du bei dieser Adresse '
        'triffst: {hint}?',
        Question.JOINED: 'Seit welchem Jahr ist ein AkaBlas-Mitglied bei AkaBlas, das Du bei '
        'dieser Adresse triffst: {hint}?',
        Question.FUNCTIONS: 'Welches Amt hat ein Mitglied ven AkaBlas (ggf. unter anderem) inne, '
        'das Du bei dieser Adresse triffst: {hint}?',
    },
    Question.PHOTO: {
        Question.ADDRESS: 'Wo wohnt dieses AkaBlas-Mitglied?',
        Question.BIRTHDAY: 'An welchem Tag hat dieses AkaBlas-Mitglied Geburtstag?',
        Question.AGE: 'Wie alt ist dieses AkaBlas-Mitglied?',
        Question.INSTRUMENT: (
            'Welches dieser Instrumente spielt dieses AkaBlas-Mitglied (ggf. unter anderem)?'
        ),
        Question.FIRST_NAME: 'Wie lautet der Vorname dieses AkaBlas-Mitglieds?',
        Question.LAST_NAME: 'Wie lautet der Nachname dieses AkaBlas-Mitglieds?',
        Question.NICKNAME: 'Wie lautet der Spitzname dieses AkaBlas-Mitglieds?',
        Question.FULL_NAME: 'Wie lautet der volle Name dieses AkaBlas-Mitglieds?',
        Question.JOINED: 'Seit welchem Jahr ist dieses AkaBlas-Mitglied bei AkaBlas?',
        Question.FUNCTIONS: 'Welches Amt dieses Mitglied ven AkaBlas (ggf. unter anderem) inne?',
    },
    Question.JOINED: {
        Question.ADDRESS: 'Wo wohnt ein AkaBlas-Mitglied, das seit {hint} bei AkaBlas ist?',
        Question.BIRTHDAY: 'An welchem Tag hat ein AkaBlas-Mitglied Geburtstag, das seit {hint} '
        'bei AkaBlas ist?',
        Question.AGE: 'Wie alt ist ein AkaBlas-Mitglied, das seit {hint} bei AkaBlas ist?',
        Question.INSTRUMENT: (
            'Welches dieser Instrumente spielt ein AkaBlas-Mitglied (ggf. unter anderem), '
            'das seit {hint} bei AkaBlas ist? '
        ),
        Question.FIRST_NAME: 'Wie lautet der Vorname eines AkaBlas-Mitglieds, das seit {hint} '
        'bei AkaBlas ist?',
        Question.LAST_NAME: 'Wie lautet der Nachname eines AkaBlas-Mitglieds, das seit {hint} '
        'bei AkaBlas ist?',
        Question.NICKNAME: 'Wie lautet der Spitzname eines AkaBlas-Mitglieds, das seit {hint} '
        'bei AkaBlas ist?',
        Question.FULL_NAME: 'Wie lautet der volle Name eines AkaBlas-Mitglieds, das seit {hint} '
        'bei AkaBlas ist?',
        Question.PHOTO: 'Welches Bild zeigt das AkaBlas-Mitglied, '
        'das seit {hint} bei AkaBlas ist?',
        Question.FUNCTIONS: 'Welches Amt hat ein Mitglied ven AkaBlas (ggf. unter anderem) inne, '
        'das seit {hint} bei AkaBlas ist?',
    },
    Question.FUNCTIONS: {
        Question.ADDRESS: 'Wo wohnt ein AkaBlas-Mitglied, das (ggf. unter anderem) {hint} ist?',
        Question.BIRTHDAY: 'An welchem Tag hat ein AkaBlas-Mitglied Geburtstag, das (ggf. unter '
        'anderem) {hint} ist?',
        Question.AGE: 'Wie alt ist ein AkaBlas-Mitglied, das (ggf. unter anderem) {hint} ist?',
        Question.INSTRUMENT: (
            'Welches dieser Instrumente spielt ein AkaBlas-Mitglied (ggf. unter anderem), '
            'das (ggf. unter anderem) {hint} ist? '
        ),
        Question.FIRST_NAME: 'Wie lautet der Vorname eines AkaBlas-Mitglieds, das (ggf. unter '
        'anderem) {hint} ist? ',
        Question.LAST_NAME: 'Wie lautet der Nachname eines AkaBlas-Mitglieds, das (ggf. unter '
        'anderem) {hint} ist? ',
        Question.NICKNAME: 'Wie lautet der Spitzname eines AkaBlas-Mitglieds, das (ggf. unter '
        'anderem) {hint} ist? ',
        Question.FULL_NAME: 'Wie lautet der volle Name eines AkaBlas-Mitglieds, das (ggf. unter '
        'anderem) {hint} ist? ',
        Question.PHOTO: 'Welches Bild zeigt das AkaBlas-Mitglied, '
        'das (gg. unter anderem) {hint} ist?',
        Question.JOINED: 'Seit wann ist ein Mitglied von AkaBlas bei AkaBlas, das (ggf. unter '
        'anderem) {hint} ist?',
    },
}

FREE_TEXT_QUESTIONS = {
    Question.FIRST_NAME: {
        Question.ADDRESS: 'Wo wohnt {hint}?',
        Question.BIRTHDAY: (
            'An welchem Tag hat {hint} Geburtstag? Bitte gib das Datum im Format "TT.MM." ein.'
        ),
        Question.AGE: 'Wie alt ist {hint}?',
        Question.INSTRUMENT: 'Welches Instrument spielt {hint} (ggf. unter anderem)?',
        Question.LAST_NAME: 'Wie lautet der Nachname von {hint}?',
        Question.NICKNAME: 'Wie lautet der Spitzname von {hint}?',
        Question.FULL_NAME: 'Wie lautet der volle Name von {hint}?',
        Question.JOINED: 'Seit welchem Jahr ist {hint} bei AkaBlas? Bitte gib das Jahr im Format '
        '"JJJJ" ein.',
        Question.FUNCTIONS: 'Welches Amt hat {hint} (ggf. unter anderem) inne?',
    },
    Question.LAST_NAME: {
        Question.ADDRESS: 'Wo wohnt das Mitglied von AkaBlas mit Nachnamen {hint}?',
        Question.BIRTHDAY: (
            'An welchem Tag hat das Mitglied von AkaBlas mit Nachnamen {hint} '
            'Geburtstag? Bitte gib das Datum im Format "TT.MM." ein.'
        ),
        Question.AGE: 'Wie alt ist das Mitglied von AkaBlas mit Nachnamen {hint}?',
        Question.INSTRUMENT: 'Welches Instrument spielt das Mitglied von AkaBlas mit Nachnamen {'
        'hint} (ggf. unter anderem)?',
        Question.FIRST_NAME: 'Wie lautet der Vorname des Mitglieds von AkaBlas mit Nachnamen {'
        'hint}?',
        Question.NICKNAME: 'Wie lautet der Spitzname des Mitglieds von AkaBlas mit Nachnamen {'
        'hint}?',
        Question.FULL_NAME: 'Wie lautet der volle Name des Mitglieds von AkaBlas mit Nachnamen {'
        'hint}?',
        Question.JOINED: 'Seit welchem Jahr ist {hint} bei AkaBlas? Bitte gib das Jahr im Format '
        '"JJJJ" ein.',
        Question.FUNCTIONS: 'Welches Amt hat {hint} (ggf. unter anderem) inne?',
    },
    Question.NICKNAME: {
        Question.ADDRESS: 'Wo wohnt {hint}?',
        Question.BIRTHDAY: (
            'An welchem Tag hat {hint} Geburtstag? Bitte gib das Datum im Format "TT.MM." ein.'
        ),
        Question.AGE: 'Wie alt ist {hint}?',
        Question.INSTRUMENT: 'Welches Instrument spielt {hint} (ggf. unter anderem)?',
        Question.FIRST_NAME: 'Wie lautet der Vorname von {hint}?',
        Question.LAST_NAME: 'Wie lautet der Nachname von {hint}?',
        Question.FULL_NAME: 'Wie lautet der volle Name von {hint}?',
        Question.JOINED: 'Seit welchem Jahr ist {hint} bei AkaBlas? Bitte gib das Jahr im Format '
        '"JJJJ" ein.',
        Question.FUNCTIONS: 'Welches Amt hat {hint} (ggf. unter anderem) inne?',
    },
    Question.FULL_NAME: {
        Question.FIRST_NAME: 'Wie lautet der Vorname von {hint}?',
        Question.LAST_NAME: 'Wie lautet der Nachname von {hint}?',
        Question.NICKNAME: 'Wie lautet der Spitzname von {hint}?',
        Question.ADDRESS: 'Wo wohnt {hint}?',
        Question.BIRTHDAY: (
            'An welchem Tag hat {hint} Geburtstag? Bitte gib das Datum im Format "TT.MM." ein.'
        ),
        Question.AGE: 'Wie alt ist {hint}?',
        Question.INSTRUMENT: 'Welches Instrument spielt {hint} (ggf. unter anderem)?',
        Question.JOINED: 'Seit welchem Jahr ist {hint} bei AkaBlas? Bitte gib das Jahr im Format '
        '"JJJJ" ein.',
        Question.FUNCTIONS: 'Welches Amt hat {hint} (ggf. unter anderem) inne?',
    },
    Question.BIRTHDAY: {
        Question.FIRST_NAME: 'Wer hat am {hint} Geburtstag? (Vorname)',
        Question.LAST_NAME: 'Wer hat am {hint} Geburtstag? (Nachname)',
        Question.NICKNAME: 'Wer hat am {hint} Geburtstag? (Spitzname)',
        Question.FULL_NAME: 'Wer hat am {hint} Geburtstag? (Ganzer Name)',
        Question.AGE: 'Wie alt ist das Mitglied von AkaBlas, das am {hint} Geburtstag hat?',
        Question.INSTRUMENT: (
            'Welches Instrument wird von einem Mitglied von AkaBlas gespielt, '
            'das am {hint} Geburtstag hat?'
        ),
        Question.ADDRESS: 'Wo wohnt ein Mitglied von AkaBlas, das am {hint} Geburtstag hat?',
        Question.JOINED: 'Seit welchem Jahr ist ein AkaBlas-Mitglied bei AkaBlas, das am {hint} '
        'Geburtstag hat? Bitte gib das Jahr im Format "JJJJ" ein.',
        Question.FUNCTIONS: 'Welches Amt hat ein Mitglied ven AkaBlas (ggf. unter anderem) inne, '
        'das am {hint} Geburtstag hat?',
    },
    Question.AGE: {
        Question.FIRST_NAME: 'Wer ist {hint} Jahre alt? (Vorname)',
        Question.LAST_NAME: 'Wer ist {hint} Jahre alt? (Nachname)',
        Question.NICKNAME: 'Wer ist {hint} Jahre alt? (Spitzname)',
        Question.FULL_NAME: 'Wer ist {hint} Jahre alt? (Ganzer Name)',
        Question.BIRTHDAY: (
            'Wann hat das Mitglied von AkaBlas Geburtstag, das jetzt {hint} Jahre '
            'alt ist? Bitte gib das Datum im Format "TT.MM." ein.'
        ),
        Question.INSTRUMENT: (
            'Welches Instrument wird von einem Mitglied von AkaBlas gespielt, '
            'das jetzt {hint} Jahre alt ist?'
        ),
        Question.ADDRESS: 'Wo wohnt ein Mitglied von AkaBlas, das jetzt {hint} Jahre alt ist?',
        Question.JOINED: 'Seit welchem Jahr ist ein AkaBlas-Mitglied bei AkaBlas, das {hint} '
        'Jahre alt ist? Bitte gib das Jahr im Format "JJJJ" ein.',
        Question.FUNCTIONS: 'Welches Amt hat ein Mitglied ven AkaBlas (ggf. unter anderem) inne, '
        'das {hint} Jahre alt hat?',
    },
    Question.INSTRUMENT: {
        Question.FIRST_NAME: 'Wer spielt (ggf. unter anderem) {hint}? (Vorname)',
        Question.LAST_NAME: 'Wer spielt (ggf. unter anderem) {hint}? (Nachname)',
        Question.NICKNAME: 'Wer spielt (ggf. unter anderem) {hint}? (Spitzname)',
        Question.FULL_NAME: 'Wer spielt (ggf. unter anderem) {hint}? (Ganzer Name)',
        Question.BIRTHDAY: (
            'Wann hat das Mitglied von AkaBlas Geburtstag, das (ggf. unter '
            'unter anderem) {hint} spielt?  Bitte gib das Datum im Format '
            '"TT.MM." ein.'
        ),
        Question.AGE: (
            'Wie alt ist das Mitglied von AkaBlas, das (ggf. unter anderem) {hint} spielt?'
        ),
        Question.ADDRESS: (
            'Wo wohnt ein Mitglied von AkaBlas, das (ggf. unter anderem) {hint} spielt?'
        ),
        Question.JOINED: 'Seit welchem Jahr ist ein AkaBlas-Mitglied bei AkaBlas, das '
        '(ggf. unter anderem) {hint} spielt? Bitte gib das Jahr im Format "JJJJ" ein.',
        Question.FUNCTIONS: 'Welches Amt hat ein Mitglied ven AkaBlas (ggf. unter anderem) inne, '
        'das (ggf. unter anderem) {hint} spielt?',
    },
    Question.ADDRESS: {
        Question.FIRST_NAME: 'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {'
        'hint}? (Vorname)',
        Question.LAST_NAME: 'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}? '
        '(Nachname)',
        Question.NICKNAME: 'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}? '
        '(Spitzname)',
        Question.FULL_NAME: 'Welches Mitglied von AkaBlas triffst Du bei dieser Adresse: {hint}? '
        '(Ganzer Name)',
        Question.BIRTHDAY: (
            'Wann hat das Mitglied von AkaBlas Geburtstag, das bei dieser Adresse '
            'wohnt: {hint}? Bitte gib das Datum im Format "TT.MM." ein.'
        ),
        Question.AGE: (
            'Wie alt ist das Mitglied von AkaBlas, das bei dieser Adresse wohnt: {hint}?'
        ),
        Question.INSTRUMENT: (
            'Welches Instrument wird von einem Mitglied von AkaBlas gespielt, '
            'das bei dieser Adresse wohnt: {hint}?'
        ),
        Question.JOINED: 'Seit welchem Jahr ist ein AkaBlas-Mitglied bei AkaBlas, das Du bei '
        'dieser Adresse triffst: {hint}? Bitte gib das Jahr im Format "JJJJ" ein.',
        Question.FUNCTIONS: 'Welches Amt hat ein Mitglied ven AkaBlas (ggf. unter anderem) inne, '
        'das Du bei dieser Adresse triffst: {hint}?',
    },
    Question.PHOTO: {
        Question.ADDRESS: 'Wo wohnt dieses AkaBlas-Mitglied?',
        Question.BIRTHDAY: (
            'An welchem Tag hat dieses AkaBlas-Mitglied Geburtstag? Bitte gib das '
            'Datum im Format "TT.MM." ein.'
        ),
        Question.AGE: 'Wie alt ist dieses AkaBlas-Mitglied?',
        Question.INSTRUMENT: (
            'Welches Instrument spielt dieses AkaBlas-Mitglied (ggf. unter anderem)?'
        ),
        Question.FIRST_NAME: 'Wie lautet der Vorname dieses AkaBlas-Mitglieds?',
        Question.LAST_NAME: 'Wie lautet der Nachname dieses AkaBlas-Mitglieds?',
        Question.NICKNAME: 'Wie lautet der Spitzname dieses AkaBlas-Mitglieds?',
        Question.FULL_NAME: 'Wie lautet der volle Name dieses AkaBlas-Mitglieds?',
        Question.JOINED: 'Seit welchem Jahr ist dieses AkaBlas-Mitglied bei AkaBlas? Bitte gib '
        'das Jahr im Format "JJJJ" ein.',
        Question.FUNCTIONS: 'Welches Amt dieses Mitglied ven AkaBlas (ggf. unter anderem) inne?',
    },
    Question.JOINED: {
        Question.ADDRESS: 'Wo wohnt ein AkaBlas-Mitglied, das seit {hint} bei AkaBlas ist?',
        Question.BIRTHDAY: 'An welchem Tag hat ein AkaBlas-Mitglied Geburtstag, das seit {hint} '
        'bei AkaBlas ist? Bitte gib das Datum im Format "TT.MM." ein.',
        Question.AGE: 'Wie alt ist ein AkaBlas-Mitglied, das seit {hint} bei AkaBlas ist?',
        Question.INSTRUMENT: (
            'Welches Instrument spielt ein AkaBlas-Mitglied (ggf. unter anderem), '
            'das seit {hint} bei AkaBlas ist? '
        ),
        Question.FIRST_NAME: 'Wie lautet der Vorname eines AkaBlas-Mitglieds, das seit {hint} '
        'bei AkaBlas ist?',
        Question.LAST_NAME: 'Wie lautet der Nachname eines AkaBlas-Mitglieds, das seit {hint} '
        'bei AkaBlas ist?',
        Question.NICKNAME: 'Wie lautet der Spitzname eines AkaBlas-Mitglieds, das seit {hint} '
        'bei AkaBlas ist?',
        Question.FULL_NAME: 'Wie lautet der volle Name eines AkaBlas-Mitglieds, das seit {hint} '
        'bei AkaBlas ist?',
        Question.PHOTO: 'Welches Bild zeigt das AkaBlas-Mitglied, das seit {hint} bei AkaBlas '
        'ist? Bitte gib das Jahr im Format "JJJJ" ein.',
        Question.FUNCTIONS: 'Welches Amt hat ein Mitglied ven AkaBlas (ggf. unter anderem) inne, '
        'das seit {hint} bei AkaBlas ist?',
    },
    Question.FUNCTIONS: {
        Question.ADDRESS: 'Wo wohnt ein AkaBlas-Mitglied, das seit {hint} bei AkaBlas ist?',
        Question.BIRTHDAY: 'An welchem Tag hat ein AkaBlas-Mitglied Geburtstag, das seit {hint} '
        'bei AkaBlas ist? Bitte gib das Datum im Format "TT.MM." ein.',
        Question.AGE: 'Wie alt ist ein AkaBlas-Mitglied, das seit {hint} bei AkaBlas ist?',
        Question.INSTRUMENT: (
            'Welches Instrument spielt ein AkaBlas-Mitglied (ggf. unter anderem), '
            'das seit {hint} bei AkaBlas ist? '
        ),
        Question.FIRST_NAME: 'Wie lautet der Vorname eines AkaBlas-Mitglieds, das seit {hint} '
        'bei AkaBlas ist?',
        Question.LAST_NAME: 'Wie lautet der Nachname eines AkaBlas-Mitglieds, das seit {hint} '
        'bei AkaBlas ist?',
        Question.NICKNAME: 'Wie lautet der Spitzname eines AkaBlas-Mitglieds, das seit {hint} '
        'bei AkaBlas ist?',
        Question.FULL_NAME: 'Wie lautet der volle Name eines AkaBlas-Mitglieds, das seit {hint} '
        'bei AkaBlas ist?',
        Question.PHOTO: 'Welches Bild zeigt das AkaBlas-Mitglied, das seit {hint} bei AkaBlas '
        'ist? Bitte gib das Jahr im Format "JJJJ" ein.',
        Question.JOINED: 'Seit wann ist ein Mitglied von AkaBlas bei AkaBlas, das (ggf. unter '
        'anderem) {hint} ist? Bitte gib das Jahr im Format "JJJJ" ein.',
    },
}


def question_text(
    member: 'Member',
    question_attribute: str,
    hint_attribute: str,
    multiple_choice: Optional[bool] = True,
    hint_value: Any = None,
) -> str:
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
        question = MULTIPLE_CHOICE_QUESTIONS[hint_attribute][question_attribute]
    else:
        question = FREE_TEXT_QUESTIONS[hint_attribute][question_attribute]

    return question.format(hint=hint_value)


PHOTO_OPTIONS = ['Oben links', 'Oben rechts', 'Unten links', 'Unten rechts']
"""
List[:obj:`str`]: Poll options to present when the question attribute is
:attr:`components.Question.PHOTO`.
"""

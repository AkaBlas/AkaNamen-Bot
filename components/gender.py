#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Gender class."""
from emoji import emojize


class Gender:  # pylint: disable=R0903
    """
    This object represents the available genders. The genders are string objects containing emojis,
    making symbolic representation in text easy.
    """

    FEMALE: str = emojize(':woman:', use_aliases=True)
    """:obj:`str`: Female"""
    MALE: str = emojize(':man:', use_aliases=True)
    """:obj:`str`: Male"""

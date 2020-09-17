#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains helper functions and casses."""
import locale
import threading
from contextlib import contextmanager
from typing import Generator

LOCALE_LOCK = threading.Lock()


@contextmanager
def setlocale(name: str) -> Generator:
    """
    Wrapper to set locale. Use like::

        with setlocale('de_DE.UTF-8'):
            return string.strptime('%B %Y')
    """
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)


COORDINATES_PATTERN = r'(\d*\.\d*), *(\d*\.\d*)'
"""
:obj:`str`: Regex pattern for coordinates tuples.
"""

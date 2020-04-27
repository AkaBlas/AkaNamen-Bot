#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the PicklableBase class."""
from threading import Lock
from typing import Dict, Any


class PicklableBase:
    """
    A base class for objects using locks for thread safety. All locks must have names ending on
    ``_lock``.
    """

    def __getstate__(self) -> Dict[str, Any]:
        """
        Get's called, when object is being pickled. Sets all variables ending on ``_lock`` to
        :obj:`None`.

        Returns: The dictionary describing the current state of the object.
        """
        state = self.__dict__.copy()
        for key in [k for k in state if k.endswith('_lock')]:
            state[key] = None
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Get's called, when object is being un-pickled. Sets all variables ending on ``_lock`` to
        a new :class:`threading.Lock` instance.

        Args:
            state: The pickled state of the object as produced by :meth:`__getstate__`.
        """
        for key in [k for k in state if k.endswith('_lock')]:
            state[key] = Lock()
        self.__dict__.update(state)

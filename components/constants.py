#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains several constants."""

ORCHESTRA_KEY = 'orchestra'
""":obj:`str`: Each ``context.bot_data[ORCHESTRA_KEY]`` is expected to be an
:class:`components.Orchestra`."""
GAME_IN_PROGRESS_KEY = 'game_in_progress'
"""
:obj:`str`: Each ``context.bot_data[GAME_IN_PROGRESS_KEY]`` is expected to be a dictionary of
type Dict[:obj:`int`, :obj:`bool`], such that ``context.bot_data[GAME_IN_PROGRESS_KEY][chat_id]``
indicates, whether there is a game being played in the corresponding chat.
"""

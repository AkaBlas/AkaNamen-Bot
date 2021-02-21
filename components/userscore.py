#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the UserScore class."""

import datetime as dt
from threading import Lock
from typing import Dict
from collections import defaultdict

from components import PicklableBase
from components import Score


class UserScore(PicklableBase):
    """
    The high score of a single user. Keeps track of their game stats. :class:`components.UserScore`
    instances are subscriptable: For each date ``day``, ``score[day]`` is a
    :class:`components.Score` instance with the number of answers and correct answers given by the
    user on that day. To add values, :meth:`add_to_score` should be the preferred method.
    """

    def __init__(self) -> None:
        self._high_score_lock = Lock()
        self._high_score: Dict[dt.date, Score] = defaultdict(Score)

    @staticmethod
    def _default_factory() -> Score:
        # needed for backwards compatibility only. Can be dropped in future versions
        return Score()  # pragma: no cover

    def __getitem__(self, date: dt.date) -> Score:
        with self._high_score_lock:
            return self._high_score[date]

    def add_to_score(self, answers: int, correct: int, date: dt.date = None) -> None:
        """
        Adds the given answers to the score of the given date.

        Args:
            answers: Number of given answers.
            correct: Number of correct answers.
            date: Date of the score. Defaults to today.

        Raises:
            ValueError: If more correct answers than answers are given.
        """
        if correct > answers:
            raise ValueError('There can\'t be more correct answers than overall answers!')

        if date is None:
            date = dt.date.today()

        score = self[date]
        score.answers += answers
        score.correct += correct

    @property
    def todays_score(self) -> Score:
        """
        Gives the score, that the user achieved today.
        """
        return self[dt.date.today()]

    def _cumulative_score(self, start: dt.date = None) -> Score:
        c_score = Score()

        with self._high_score_lock:
            for date, score in self._high_score.items():
                if start is None or date >= start:
                    c_score.answers += score.answers
                    c_score.correct += score.correct
        return c_score

    @property
    def weeks_score(self) -> Score:
        """
        The overall score, that the user achieved during the current week.
        """
        today = dt.date.today()
        return self._cumulative_score(start=today - dt.timedelta(days=today.weekday()))

    @property
    def months_score(self) -> Score:
        """
        The overall score, that the user achieved during the current month.
        """
        today = dt.date.today()
        return self._cumulative_score(start=today - dt.timedelta(days=today.day - 1))

    @property
    def years_score(self) -> Score:
        """
        The overall score, that the user achieved during the current year.
        """
        return self._cumulative_score(start=dt.date(dt.date.today().year, 1, 1))

    @property
    def overall_score(self) -> Score:
        """
        The overall score of the user.
        """
        return self._cumulative_score()

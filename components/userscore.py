#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the UserScore class."""
from components import PicklableBase
from components import Score

import datetime as dt

from threading import Lock
from typing import Optional, Dict, TYPE_CHECKING
from collections import defaultdict

# We don't like circular imports
if TYPE_CHECKING:
    from components import Member


class UserScore(PicklableBase):
    """
    The high score of a single user. Keeps track of their game stats. :class:`components.UserScore`
    instances are subscriptable: For each date ``day``, ``score[day]`` is a
    :class:`components.Score` instance with the number of answers and correct answers given by the
    user on that day. To add values, :meth:`add_to_score` should be the preferred method.

    Attributes:
        member (:class:`components.Member`): The member, this high score is associated with.

    Args:
        member: The member, this high score is associated with.
    """

    def __init__(self, member: 'Member') -> None:
        self.member = member

        self._high_score_lock = Lock()
        self._high_score: Dict[dt.date, Score] = defaultdict(self._default_factory)

    def _default_factory(self):
        return Score(member=self.member)

    def __getitem__(self, date: dt.date) -> Score:
        with self._high_score_lock:
            return self._high_score[date]

    def add_to_score(self, answers: int, correct: int, date: dt.date = dt.date.today()) -> None:
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

        score = self[date]
        score.answers += answers
        score.correct += correct

    @property
    def todays_score(self) -> Score:
        """
        Gives the score, that the user achieved today.
        """
        return self[dt.date.today()]

    def _cumulative_score(self, start: Optional[dt.date] = None) -> Score:
        c_score = Score(member=self.member)

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

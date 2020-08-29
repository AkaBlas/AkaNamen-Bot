#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Score class."""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from components import Member  # noqa: F401


class Score:
    """
    A single score count. Scores are comparable, i.e. ``score_1 == score_2`` if and only if the
    :attr:`answers` and :attr:`correct` attributes are equal. Moreover, scores can be evaluated as
    boolean, where ``bool(score) == True`` if :attr:`answers` is greater than zero. Finally, scores
    are ordered: ``score_1 < score_2``, if ``score_1`` has a smaller :attr:`ratio` than `score_2`,
    or, if the ratios coincide, has fewer recorded answers.

    Args:
        answers: The number of answers that were given. Defaults to zero.
        correct: The number of answers that were correct. Defaults to zero.
        member: The member this score is associated with.
    """

    def __init__(self, answers: int = 0, correct: int = 0, member: 'Member' = None) -> None:
        self._answers = 0
        self._correct = 0
        self.answers = answers
        self.correct = correct
        self.member = member

    @property
    def answers(self) -> int:
        """
        The number of answers that were given.
        """
        return self._answers

    @answers.setter
    def answers(self, value: int) -> None:
        if value < 0:
            raise ValueError('answers can\'t be smaller than zero.')
        if value < self.correct:
            raise ValueError('Fewer answers than correct answers.')
        self._answers = value

    @property
    def correct(self) -> int:
        """
        The number of answers that were correct.
        """
        return self._correct

    @correct.setter
    def correct(self, value: int) -> None:
        if value < 0:
            raise ValueError('correct can\'t be smaller than zero.')
        if value > self.answers:
            raise ValueError('Fewer answers than correct answers.')
        self._correct = value

    @property
    def ratio(self) -> float:
        """
        The ratio of given and correct answers in percentage with two decimal places.
        """
        if self.answers == 0:
            return 0
        return round((self.correct / self.answers) * 100, 2)

    def __bool__(self) -> bool:
        return self.answers > 0

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Score):
            return self.answers == other.answers and self.correct == other.correct
        return False

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Score):
            if self.ratio == other.ratio:
                return self.answers < other.answers
            return self.ratio < other.ratio
        return False

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Score):
            return other < self
        return False

    def __le__(self, other: object) -> bool:
        if isinstance(other, Score):
            return self < other or not self > other
        return False

    def __ge__(self, other: object) -> bool:
        if isinstance(other, Score):
            return other <= self
        return False

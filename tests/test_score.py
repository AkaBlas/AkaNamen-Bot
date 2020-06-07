#!/usr/bin/env python
import pytest
from components import Member, Score


class TestScore:

    def test_init(self):
        score = Score()
        assert score.answers == 0
        assert score.correct == 0

        score = Score(answers=2, correct=1, member=Member(123))
        assert score.answers == 2
        assert score.correct == 1
        assert score.member == Member(123)

    def test_properties(self):
        score = Score()
        with pytest.raises(ValueError, match='smaller than zero'):
            score.answers = -1
        with pytest.raises(ValueError, match='smaller than zero'):
            score.correct = -1

        score.answers = 10
        score.correct = 5
        assert score.answers == 10
        assert score.correct == 5

        with pytest.raises(ValueError, match='Fewer'):
            score.answers = 4
        with pytest.raises(ValueError, match='Fewer'):
            score.correct = 11

    def test_ratio(self):
        score = Score()
        assert score.ratio == 0
        score = Score(7, 5)
        assert score.ratio == 71.43

    def test_bool(self):
        score = Score(0, 0)
        assert not score
        score.answers += 1
        assert score

    def test_comparison(self):
        score_1 = Score(4, 2)
        score_2 = Score(8, 4)
        member = Member(123)

        assert score_1 <= score_2
        assert score_2 >= score_1
        assert score_1 < score_2
        assert score_2 > score_1
        assert score_1 != score_2

        score_1 = Score(3, 1)
        score_2 = Score(4, 1)

        assert score_1 >= score_2
        assert score_2 <= score_1
        assert score_1 > score_2
        assert score_2 < score_1
        assert score_1 != score_2

        assert score_1 >= score_1
        assert score_1 <= score_1
        assert not score_1 > score_1
        assert not score_1 < score_1
        assert score_1 == score_1

        assert not (score_1 < member)
        assert not (score_1 <= member)
        assert not (score_1 > member)
        assert not (score_1 >= member)

    def test_equality(self):
        a = Score(7, 5)
        b = Score(7, 5)
        c = Score(6, 5)
        d = Score(7, 6)
        e = Score()
        f = Member(123)

        assert a == b
        assert a != c
        assert a != d
        assert a != e
        assert a != f

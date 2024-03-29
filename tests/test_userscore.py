#!/usr/bin/env python
import pytest
import datetime as dt
from components import Score, UserScore


@pytest.fixture(scope='function')
def us():
    return UserScore()


class TestUserScore:
    def test_subscriptable(self, us, today):
        score = us[today]
        assert isinstance(score, Score)

        score.answers = 7
        score.correct = 5

        assert us[today].correct == 5
        assert us[today].answers == 7

    def test_add_to_score(self, us, today):
        with pytest.raises(ValueError, match='more correct answers'):
            us.add_to_score(5, 10)

        score = us[today]
        us.add_to_score(answers=5, correct=3)

        assert score.answers == 5
        assert score.correct == 3
        assert not us[today + dt.timedelta(days=1)]

    def test_add_to_score_tomorrow(self, us, monkeypatch):
        today = dt.date.today()
        tomorrow = today + dt.timedelta(days=1)

        class MyDate:
            def today(*args, **kwargs):  # pylint: disable=E0211
                return tomorrow

        monkeypatch.setattr(dt, 'date', MyDate)

        score = us[tomorrow]
        us.add_to_score(answers=5, correct=3)

        assert score.answers == 5
        assert score.correct == 3
        assert not us[today]
        assert not us[tomorrow + dt.timedelta(days=1)]

    def test_todays_score(self, us, today):
        us.add_to_score(answers=5, correct=3, date=today)
        score = us.todays_score

        assert score.answers == 5
        assert score.correct == 3

    def test_weeks_score(self, us, today):
        us.add_to_score(answers=4, correct=3, date=today - dt.timedelta(days=10))
        assert not us.weeks_score

        us.add_to_score(answers=8, correct=4, date=today - dt.timedelta(days=today.weekday()))
        assert us.weeks_score
        assert us.weeks_score.answers == 8
        assert us.weeks_score.correct == 4

    def test_months_score(self, us, today):
        us.add_to_score(answers=5, correct=3, date=today - dt.timedelta(weeks=6))
        assert not us.months_score

        us.add_to_score(answers=8, correct=4, date=today - dt.timedelta(days=today.day - 1))
        assert us.months_score
        assert us.months_score.answers == 8
        assert us.months_score.correct == 4

    def test_years_score(self, us, today):
        us.add_to_score(answers=5, correct=3, date=today - dt.timedelta(weeks=53))
        assert not us.years_score

        us.add_to_score(answers=8, correct=4, date=dt.date(today.year, 1, 1))
        assert us.years_score
        assert us.years_score.answers == 8
        assert us.years_score.correct == 4

    def test_overall_score(self, us, today):
        us.add_to_score(answers=5, correct=3, date=today - dt.timedelta(weeks=53))
        assert us.overall_score
        assert us.overall_score.answers == 5
        assert us.overall_score.correct == 3

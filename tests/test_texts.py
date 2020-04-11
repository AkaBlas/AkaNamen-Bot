#!/usr/bin/env python
import pytest
import datetime as dt
from components import Member, Gender, instruments, Question, question_text


class TestTexsts:
    member = Member(1,
                    first_name='first',
                    last_name='last',
                    nickname='nickname',
                    gender=Gender.DIVERSE,
                    date_of_birth=dt.date(dt.date.today().year - 21, 12, 31),
                    instruments=instruments.AltoSaxophone(),
                    address='Universitätsplatz 2, 38106 Braunschweig')

    def test_all(self):
        for q in Question.SUPPORTED_ATTRIBUTES:
            for h in Question.SUPPORTED_ATTRIBUTES:
                if h != q:
                    for m in [True, False]:
                        text = question_text(self.member, q, h, m)
                        assert isinstance(text, str)
                        assert text != ''
                        assert '{' not in text
                        assert '}' not in text

    def test_errors(self):
        with pytest.raises(ValueError, match='Unsupported'):
            question_text(self.member, 'abc', Question.FULL_NAME)
        with pytest.raises(ValueError, match='Unsupported'):
            question_text(self.member, Question.FULL_NAME, 'abc')

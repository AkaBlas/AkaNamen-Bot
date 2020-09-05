#!/usr/bin/env python
import pytest
import datetime as dt
from geopy import Photon
from components import Member, Gender, instruments, Question, question_text

from tests.addresses import get_address_from_cache


@pytest.fixture
def member(monkeypatch):
    monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)
    return Member(1,
                  first_name='first',
                  last_name='last',
                  nickname='nickname',
                  photo_file_id='file_id',
                  gender=Gender.MALE,
                  date_of_birth=dt.date(dt.date.today().year - 21, 12, 31),
                  instruments=instruments.AltoSaxophone(),
                  address='Universitätsplatz 2, 38106 Braunschweig')


class TestTexts:

    def test_all_but_photo(self, member):
        for q in [a for a in Question.SUPPORTED_ATTRIBUTES if a != Question.PHOTO]:
            for h in Question.SUPPORTED_ATTRIBUTES:
                if h != q:
                    for m in [True, False]:
                        text = question_text(member, q, h, m)
                        assert isinstance(text, str)
                        assert text != ''
                        assert '{' not in text
                        assert '}' not in text

        for q in [k for k in Question.SUPPORTED_ATTRIBUTES if k != Question.PHOTO]:
            for h in [k for k in Question.SUPPORTED_ATTRIBUTES if k != Question.PHOTO]:
                if h not in q and q not in h:
                    for m in [True, False]:
                        text = question_text(member, q, h, m)
                        assert isinstance(text, str)
                        assert text != ''
                        assert '{' not in text
                        assert '}' not in text

    def test_photo(self, member):
        q = Question.PHOTO
        for h in [a for a in Question.SUPPORTED_ATTRIBUTES if a != q]:
            with pytest.raises(ValueError, match='Photos are'):
                question_text(member, q, h, False)

            text = question_text(member, q, h, True)
            assert text != ''
            assert '{' not in text
            assert '}' not in text

        q = 'photo_file_id'
        for h in [k for k in Question.SUPPORTED_ATTRIBUTES if k != Question.PHOTO]:
            with pytest.raises(ValueError, match='Photos are'):
                question_text(member, q, h, False)

            text = question_text(member, q, h, True)
            assert text != ''
            assert '{' not in text
            assert '}' not in text

    def test_errors(self):
        with pytest.raises(ValueError, match='Unsupported'):
            question_text(member, 'abc', Question.FULL_NAME)
        with pytest.raises(ValueError, match='Unsupported'):
            question_text(member, Question.FULL_NAME, 'abc')

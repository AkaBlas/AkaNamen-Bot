#!/usr/bin/env python
import pytest
import datetime as dt
from components import Member, Gender, instruments, Question, question_text, Orchestra


class TestTexts:
    member = Member(1,
                    first_name='first',
                    last_name='last',
                    nickname='nickname',
                    gender=Gender.MALE,
                    date_of_birth=dt.date(dt.date.today().year - 21, 12, 31),
                    instruments=instruments.AltoSaxophone(),
                    address='Universitätsplatz 2, 38106 Braunschweig')

    def test_all_but_photo(self):
        for q in [a for a in Question.SUPPORTED_ATTRIBUTES if a != Question.PHOTO]:
            for h in Question.SUPPORTED_ATTRIBUTES:
                if h != q:
                    for m in [True, False]:
                        text = question_text(self.member, q, h, m)
                        assert isinstance(text, str)
                        assert text != ''
                        assert '{' not in text
                        assert '}' not in text

        for q in [
                k for k, v in Orchestra.DICTS_TO_ATTRS.items()
                if k != 'photo_file_ids' and v in Question.SUPPORTED_ATTRIBUTES
        ]:
            for h in [
                    k for k, v in Orchestra.DICTS_TO_ATTRS.items()
                    if v in Question.SUPPORTED_ATTRIBUTES
            ]:
                if h not in q and q not in h:
                    for m in [True, False]:
                        text = question_text(self.member, q, h, m)
                        assert isinstance(text, str)
                        assert text != ''
                        assert '{' not in text
                        assert '}' not in text

    def test_photo(self):
        q = Question.PHOTO
        for h in [a for a in Question.SUPPORTED_ATTRIBUTES if a != q]:
            with pytest.raises(ValueError, match='Photos are'):
                question_text(self.member, q, h, False)

            text = question_text(self.member, q, h, True)
            assert text != ''
            assert '{' not in text
            assert '}' not in text

        q = 'photo_file_ids'
        for h in [
                k for k, v in Orchestra.DICTS_TO_ATTRS.items()
                if k != q and v in Question.SUPPORTED_ATTRIBUTES
        ]:
            with pytest.raises(ValueError, match='Photos are'):
                question_text(self.member, q, h, False)

            text = question_text(self.member, q, h, True)
            assert text != ''
            assert '{' not in text
            assert '}' not in text

    def test_errors(self):
        with pytest.raises(ValueError, match='Unsupported'):
            question_text(self.member, 'abc', Question.FULL_NAME)
        with pytest.raises(ValueError, match='Unsupported'):
            question_text(self.member, Question.FULL_NAME, 'abc')

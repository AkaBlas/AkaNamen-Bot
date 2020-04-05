#!/usr/bin/env python
from akablas import Gender


class TestGender:

    def test_genders(self):
        assert isinstance(Gender.MALE, str)
        assert isinstance(Gender.FEMALE, str)
        assert isinstance(Gender.DIVERSE, str)

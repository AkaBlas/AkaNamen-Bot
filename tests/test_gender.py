#!/usr/bin/env python
from akablas import Gender


def test_instruments():
    assert isinstance(Gender.MALE, str)
    assert isinstance(Gender.FEMALE, str)
    assert isinstance(Gender.DIVERSE, str)

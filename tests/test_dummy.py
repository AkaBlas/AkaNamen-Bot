#!/usr/bin/env python
import akablas
import bot


def test_akablas():
    assert 'dummy' == akablas.dummy('dummy')
    assert 'dummy' != akablas.dummy(1)


def test_bot():
    assert 'dummy' == bot.dummy('dummy')
    assert 'dummy' != bot.dummy(1)

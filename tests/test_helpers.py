#!/usr/bin/env python
import datetime as dt
import locale
from components.helpers import setlocale


class TestHelpers:

    def test_set_locale(self):
        date = dt.date(2020, 3, 13)
        current_locale = locale.getlocale()

        with setlocale('de_DE.UTF-8'):
            assert date.strftime('%B') == 'März'
            assert date.strftime('%A') == 'Freitag'

        assert locale.getlocale() == current_locale

        with setlocale('en_US.UTF-8'):
            assert date.strftime('%B') == 'March'
            assert date.strftime('%A') == 'Friday'

        assert locale.getlocale() == current_locale

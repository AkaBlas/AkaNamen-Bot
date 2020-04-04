#!/usr/bin/env python
import pickle

from threading import Lock
from utils import PicklableBase
from tempfile import NamedTemporaryFile


class TestPicklableBase:

    def test_pickle(self):
        base = PicklableBase()
        base._one_lock = Lock()
        base._two_lock = Lock()

        with NamedTemporaryFile() as file:
            pickle.dump(base, file)
            file.flush()
            b = pickle.load(open(file.name, 'rb'))

            assert isinstance(b._one_lock, type(Lock()))
            assert isinstance(b._two_lock, type(Lock()))

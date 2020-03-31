#!/usr/bin/env python
import os

import pytest


def call_pre_commit_hook(hook_id):
    __tracebackhide__ = True
    return os.system(' '.join(['pre-commit', 'run', '--all-files', hook_id]))  # pragma: no cover


@pytest.mark.nocoverage
@pytest.mark.parametrize('hook_id', argvalues=('yapf', 'flake8', 'pylint', 'mypy'))
@pytest.mark.skipif(not os.getenv('TEST_PRE_COMMIT', False), reason='TEST_PRE_COMMIT not enabled')
def test_pre_commit_hook(hook_id):
    assert call_pre_commit_hook(hook_id) == 0  # pragma: no cover

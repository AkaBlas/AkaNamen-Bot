#!/usr/bin/env python
import pytest
import datetime as dt

from components import Gender, Member, instruments, Orchestra, Score, Questioner
from collections import defaultdict


@pytest.fixture(scope='function')
def empty_member():
    return Member(user_id=123456)


@pytest.fixture(scope='function')
def empty_orchestra():
    return Orchestra()


class TestQuestioner:

    @pytest.mark.parametrize('populated_orchestra', [{}], indirect=True)
    def test_init(self, bot, populated_orchestra, empty_member):
        orchestra = populated_orchestra
        orchestra.register_member(empty_member)
        questioner = Questioner(user_id=empty_member.user_id,
                                orchestra=orchestra,
                                hint_attributes=[],
                                question_attributes=[],
                                number_of_questions=42,
                                bot=bot,
                                multiple_choice=True)

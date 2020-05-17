#!/usr/bin/env python
import pytest

from telegram import Update, PollAnswer, User
from components import Member, Orchestra, Questioner


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

        assert questioner.member == empty_member
        assert questioner.orchestra is orchestra
        assert questioner.bot is bot
        assert questioner.multiple_choice is True
        assert questioner.score.answers == 0
        assert not questioner.current_question
        assert not questioner.check_update(Update(123))
        assert not questioner.check_update(
            Update(123, poll_answer=PollAnswer(123, User(123, '', False), [1])))
        assert not questioner.used_members

    @pytest.mark.parametrize('populated_orchestra', [{'skip': ['last_name']}], indirect=True)
    def test_init_errors(self, bot, populated_orchestra, empty_orchestra, empty_member):
        orchestra = populated_orchestra
        orchestra.register_member(empty_member)
        with pytest.raises(ValueError, match='Number of questions'):
            Questioner(user_id=empty_member.user_id,
                       orchestra=orchestra,
                       hint_attributes=[],
                       question_attributes=[],
                       number_of_questions=-1,
                       bot=bot)

        with pytest.raises(ValueError, match='Allowing the same'):
            Questioner(user_id=empty_member.user_id,
                       orchestra=orchestra,
                       hint_attributes=['age'],
                       question_attributes=['age'],
                       number_of_questions=42,
                       bot=bot)

        with pytest.raises(ValueError, match='Unsupported hint'):
            Questioner(user_id=empty_member.user_id,
                       orchestra=orchestra,
                       hint_attributes=['foo'],
                       question_attributes=[],
                       number_of_questions=42,
                       bot=bot)

        with pytest.raises(ValueError, match='Unsupported question'):
            Questioner(user_id=empty_member.user_id,
                       orchestra=orchestra,
                       hint_attributes=[],
                       question_attributes=['bar'],
                       number_of_questions=42,
                       bot=bot)

        with pytest.raises(ValueError, match='Attribute last_name'):
            Questioner(user_id=empty_member.user_id,
                       orchestra=orchestra,
                       hint_attributes=['last_name'],
                       question_attributes=[],
                       number_of_questions=42,
                       bot=bot)

        with pytest.raises(ValueError, match='Attribute last_name'):
            Questioner(user_id=empty_member.user_id,
                       orchestra=orchestra,
                       hint_attributes=[],
                       question_attributes=['last_name'],
                       number_of_questions=42,
                       bot=bot)

        empty_orchestra.register_member(empty_member)
        with pytest.raises(ValueError, match='hint_attributes and question_attributes'):
            Questioner(user_id=empty_member.user_id,
                       orchestra=empty_orchestra,
                       hint_attributes=[],
                       question_attributes=[],
                       number_of_questions=42,
                       bot=bot)

    @pytest.mark.parametrize('populated_orchestra', [{}], indirect=True)
    def test_ask_question(self, bot, chat_id, populated_orchestra, empty_member, monkeypatch):
        orig_send_poll = bot.send_poll

        poll_message = None

        def send_poll(*args, **kwargs):
            kwargs['chat_id'] = chat_id
            nonlocal poll_message
            poll_message = orig_send_poll(*args, **kwargs)
            return poll_message

        orchestra = populated_orchestra
        orchestra.register_member(empty_member)
        questioner = Questioner(user_id=empty_member.user_id,
                                orchestra=orchestra,
                                hint_attributes=['instruments'],
                                question_attributes=['first_names'],
                                number_of_questions=42,
                                bot=bot,
                                multiple_choice=True)

        monkeypatch.setattr(questioner.bot, 'send_poll', send_poll)
        questioner.ask_question()

        assert questioner.current_question
        assert questioner.current_question.poll is poll_message.poll
        assert not questioner.used_members

        update = Update(123,
                        poll_answer=PollAnswer(poll_message.poll.id, User(chat_id, 'foo', False),
                                               [(poll_message.poll.correct_option_id + 1) % 4]))

        assert not questioner.check_update(update)

        update = Update(123,
                        poll_answer=PollAnswer(poll_message.poll.id,
                                               User(empty_member.user_id, 'foo', False),
                                               [poll_message.poll.correct_option_id]))

        assert questioner.check_update(update)
        questioner.handle_update(update)
        assert questioner.score.answers == 1
        assert questioner.score.correct == 1
        assert len(questioner.used_members) == 1
        assert len(questioner.used_members[list(questioner.used_members.keys())[0]]) == 1

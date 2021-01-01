#!/usr/bin/env python
import random
import pytest

from telegram import Update, PollAnswer, User, Message, Chat, Location, Poll, PollOption
from components import Member, Orchestra, Questioner, Question


@pytest.fixture(scope='function')
def empty_member(chat_id):
    return Member(user_id=int(chat_id))


@pytest.fixture(scope='function')
def empty_orchestra():
    return Orchestra()


def fake_poll():
    return Message(
        message_id=123,
        from_user=None,
        chat=None,
        date=None,
        poll=Poll(
            random.randint(100, 500),
            'question',
            None,
            0,
            False,
            False,
            Poll.QUIZ,
            False,
            random.randint(0, 3),
        ),
    )


class TestQuestioner:
    @pytest.mark.parametrize('populated_orchestra', [{}], indirect=True)
    def test_init(self, bot, populated_orchestra, empty_member):
        orchestra = populated_orchestra
        orchestra.register_member(empty_member)
        questioner = Questioner(
            user_id=empty_member.user_id,
            orchestra=orchestra,
            hint_attributes=[],
            question_attributes=[],
            number_of_questions=42,
            bot=bot,
            multiple_choice=True,
        )

        assert questioner.member == empty_member
        assert questioner.orchestra is orchestra
        assert questioner.bot is bot
        assert questioner.multiple_choice is True
        assert questioner.score.answers == 0
        assert not questioner.current_question
        assert not questioner.check_update(Update(123))
        assert not questioner.check_update(
            Update(123, poll_answer=PollAnswer(123, User(123, '', False), [1]))
        )

    @pytest.mark.parametrize('populated_orchestra', [{'skip': ['last_name']}], indirect=True)
    def test_init_errors(self, bot, populated_orchestra, empty_orchestra, empty_member):
        orchestra = populated_orchestra
        orchestra.register_member(empty_member)
        with pytest.raises(ValueError, match='Number of questions'):
            Questioner(
                user_id=empty_member.user_id,
                orchestra=orchestra,
                hint_attributes=[],
                question_attributes=[],
                number_of_questions=-1,
                bot=bot,
            )

        with pytest.raises(ValueError, match='Allowing the same'):
            Questioner(
                user_id=empty_member.user_id,
                orchestra=orchestra,
                hint_attributes=['age'],
                question_attributes=['age'],
                number_of_questions=42,
                bot=bot,
            )

        with pytest.raises(ValueError, match='Unsupported hint'):
            Questioner(
                user_id=empty_member.user_id,
                orchestra=orchestra,
                hint_attributes=['foo'],
                question_attributes=[],
                number_of_questions=42,
                bot=bot,
            )

        with pytest.raises(ValueError, match='Unsupported question'):
            Questioner(
                user_id=empty_member.user_id,
                orchestra=orchestra,
                hint_attributes=[],
                question_attributes=['bar'],
                number_of_questions=42,
                bot=bot,
            )

        with pytest.raises(ValueError, match='Attribute last_name'):
            Questioner(
                user_id=empty_member.user_id,
                orchestra=orchestra,
                hint_attributes=['last_name'],
                question_attributes=[],
                number_of_questions=42,
                bot=bot,
            )

        with pytest.raises(ValueError, match='Attribute last_name'):
            Questioner(
                user_id=empty_member.user_id,
                orchestra=orchestra,
                hint_attributes=[],
                question_attributes=['last_name'],
                number_of_questions=42,
                bot=bot,
            )

        empty_orchestra.register_member(empty_member)
        with pytest.raises(ValueError, match='No valid hint-question combination available.'):
            Questioner(
                user_id=empty_member.user_id,
                orchestra=empty_orchestra,
                hint_attributes=[],
                question_attributes=[],
                number_of_questions=42,
                bot=bot,
            )

    @pytest.mark.parametrize('populated_orchestra', [{}], indirect=True)
    def test_questionable(self, populated_orchestra, bot, chat_id, empty_member):
        orchestra = populated_orchestra
        orchestra.register_member(empty_member)
        questioner = Questioner(
            user_id=int(chat_id),
            orchestra=populated_orchestra,
            hint_attributes=['first_name'],
            question_attributes=['instruments'],
            number_of_questions=42,
            bot=bot,
            multiple_choice=True,
        )
        assert len(populated_orchestra.questionable()) > 1
        assert questioner.questionable() == [('first_name', 'instruments')]

    @pytest.mark.parametrize('runs', range(50))
    @pytest.mark.parametrize('populated_orchestra', [{}], indirect=True)
    def test_ask_question_multiple_choice(
        self, bot, chat_id, populated_orchestra, empty_member, monkeypatch, runs
    ):
        poll_message = None

        def send_poll(*args, **kwargs):
            nonlocal poll_message
            poll_message = fake_poll()
            return poll_message

        def send_pass(*args, **kwargs):
            pass

        orchestra = populated_orchestra
        orchestra.register_member(empty_member)
        questioner = Questioner(
            user_id=int(chat_id),
            orchestra=orchestra,
            hint_attributes=[],
            question_attributes=[],
            number_of_questions=42,
            bot=bot,
            multiple_choice=True,
        )

        monkeypatch.setattr(questioner.bot, 'send_poll', send_poll)
        monkeypatch.setattr(questioner.bot, 'send_photo', send_pass)
        monkeypatch.setattr(questioner.bot, 'send_media_group', send_pass)
        questioner.ask_question()
        assert questioner.number_of_questions_asked == 1

        assert questioner.current_question
        assert questioner.current_question.poll is poll_message.poll

        update = Update(
            123,
            poll_answer=PollAnswer(
                poll_message.poll.id,
                User(123, 'foo', False),
                [(poll_message.poll.correct_option_id + 1) % 4],
            ),
        )

        assert not questioner.check_update(update)

        update = Update(
            123,
            poll_answer=PollAnswer(
                '4654654',
                User(chat_id, 'foo', False),
                [(poll_message.poll.correct_option_id + 1) % 4],
            ),
        )

        assert not questioner.check_update(update)

        update = Update(
            123,
            poll_answer=PollAnswer(
                poll_message.poll.id,
                User(chat_id, 'foo', False),
                [(poll_message.poll.correct_option_id + 1) % 4],
            ),
        )

        assert questioner.check_update(update)
        questioner.handle_update(update)
        assert questioner.score.answers == 1
        assert questioner.score.correct == 0

        update = Update(
            123,
            poll_answer=PollAnswer(
                poll_message.poll.id,
                User(chat_id, 'foo', False),
                [poll_message.poll.correct_option_id],
            ),
        )

        assert questioner.check_update(update)
        questioner.handle_update(update)
        assert questioner.score.answers == 2
        assert questioner.score.correct == 1

    @pytest.mark.parametrize('runs', range(50))
    @pytest.mark.parametrize('populated_orchestra', [{'members': 10}], indirect=True)
    def test_ask_question_free_text(
        self, bot, chat_id, populated_orchestra, empty_member, monkeypatch, runs
    ):

        poll_message = None
        answer_message_text = ''

        def send_poll(*args, **kwargs):
            nonlocal poll_message
            poll_message = fake_poll()
            return poll_message

        def send_message(*args, **kwargs):
            nonlocal answer_message_text
            answer_message_text = kwargs['text']
            return answer_message_text

        def send_pass(*args, **kwargs):
            pass

        orchestra = populated_orchestra
        orchestra.register_member(empty_member)
        questioner = Questioner(
            user_id=int(chat_id),
            orchestra=orchestra,
            hint_attributes=[],
            question_attributes=[],
            number_of_questions=42,
            bot=bot,
            multiple_choice=False,
        )

        monkeypatch.setattr(questioner.bot, 'send_poll', send_poll)
        monkeypatch.setattr(questioner.bot, 'send_message', send_message)
        monkeypatch.setattr(questioner.bot, 'send_photo', send_pass)
        monkeypatch.setattr(questioner.bot, 'send_media_group', send_pass)
        try:
            questioner.ask_question()
        except RuntimeError as e:
            if 'currently not hintable' in str(e):
                pytest.xfail('This test may be flaky depending on the orchestra constellation')
        assert questioner.number_of_questions_asked == 1

        assert questioner.current_question
        if questioner.current_question.multiple_choice:
            assert questioner.current_question.attribute == Question.PHOTO
            assert questioner.current_question.poll is poll_message.poll
        else:
            assert not questioner.current_question.poll

        if questioner.current_question.multiple_choice:
            update = Update(
                123,
                poll_answer=PollAnswer(
                    poll_message.poll.id,
                    User(123, 'foo', False),
                    [(poll_message.poll.correct_option_id + 1) % 4],
                ),
            )
        else:
            update = Update(
                123,
                message=Message(
                    message_id=123,
                    from_user=User(123, 'foo', False),
                    chat=Chat(123, Chat.PRIVATE),
                    date=None,
                    text='some very false answer',
                    bot=bot,
                ),
            )

        assert not questioner.check_update(update)

        if questioner.current_question.multiple_choice:
            update = Update(
                123,
                poll_answer=PollAnswer(
                    poll_message.poll.id,
                    User(chat_id, 'foo', False),
                    [(poll_message.poll.correct_option_id + 1) % 4],
                ),
            )
        else:
            update = Update(
                123,
                message=Message(
                    message_id=123,
                    from_user=User(chat_id, 'foo', False),
                    date=None,
                    chat=Chat(chat_id, Chat.PRIVATE),
                    text='some very false answer',
                    bot=bot,
                ),
            )

        assert questioner.check_update(update)
        questioner.handle_update(update)
        assert questioner.score.answers == 1
        assert questioner.score.correct == 0
        if not questioner.current_question.multiple_choice:
            assert 'nicht korrekt' in answer_message_text

        if questioner.current_question.multiple_choice:
            update = Update(
                123,
                poll_answer=PollAnswer(
                    poll_message.poll.id,
                    User(chat_id, 'foo', False),
                    [poll_message.poll.correct_option_id],
                ),
            )
        else:
            if isinstance(questioner.current_question.correct_answer, list):
                text = str(random.choice(questioner.current_question.correct_answer))
            else:
                text = questioner.current_question.correct_answer

            update = Update(
                123,
                message=Message(
                    message_id=123,
                    from_user=User(chat_id, 'foo', False),
                    date=None,
                    chat=Chat(chat_id, Chat.PRIVATE),
                    text=text,
                    bot=bot,
                ),
            )

        assert questioner.check_update(update)
        questioner.handle_update(update)
        assert questioner.score.answers == 2
        assert questioner.score.correct == 1
        if not questioner.current_question.multiple_choice:
            assert 'richtig!' in answer_message_text

    @pytest.mark.parametrize('runs', range(3))
    @pytest.mark.parametrize('populated_orchestra', [{}], indirect=True)
    def test_ask_question_location(
        self, bot, chat_id, populated_orchestra, empty_member, monkeypatch, runs
    ):
        answer_message_text = ''

        def send_message(*args, **kwargs):
            nonlocal answer_message_text
            answer_message_text = kwargs['text']
            return answer_message_text

        def send_pass(*args, **kwargs):
            pass

        orchestra = populated_orchestra
        orchestra.register_member(empty_member)
        questioner = Questioner(
            user_id=int(chat_id),
            orchestra=orchestra,
            hint_attributes=[],
            question_attributes=['address'],
            number_of_questions=42,
            bot=bot,
            multiple_choice=False,
        )

        monkeypatch.setattr(questioner.bot, 'send_message', send_message)
        monkeypatch.setattr(questioner.bot, 'send_photo', send_pass)
        monkeypatch.setattr(questioner.bot, 'send_media_group', send_pass)
        try:
            questioner.ask_question()
        except RuntimeError as e:
            if 'currently not hintable' in str(e):
                pytest.xfail('This test may be flaky depending on the orchestra constellation')
        assert questioner.number_of_questions_asked == 1

        assert questioner.current_question
        assert not questioner.current_question.poll

        update = Update(
            123,
            message=Message(
                message_id=123,
                from_user=User(123, 'foo', False),
                date=None,
                chat=Chat(123, Chat.PRIVATE),
                location=Location(27.988191, 86.924518),
                bot=bot,
            ),
        )

        assert not questioner.check_update(update)

        update = Update(
            123,
            message=Message(
                message_id=123,
                from_user=User(chat_id, 'foo', False),
                date=None,
                chat=Chat(chat_id, Chat.PRIVATE),
                location=Location(27.988191, 86.924518),
                bot=bot,
            ),
        )

        assert questioner.check_update(update)
        questioner.handle_update(update)
        assert questioner.score.answers == 1
        assert questioner.score.correct == 0
        if not questioner.current_question.multiple_choice:
            assert 'nicht korrekt' in answer_message_text

        longitude = questioner.current_question.member.longitude
        latitude = questioner.current_question.member.latitude
        update = Update(
            123,
            message=Message(
                message_id=123,
                from_user=User(chat_id, 'foo', False),
                date=None,
                chat=Chat(chat_id, Chat.PRIVATE),
                location=Location(longitude, latitude),
                bot=bot,
            ),
        )

        assert questioner.check_update(update)
        questioner.handle_update(update)
        assert questioner.score.answers == 2
        assert questioner.score.correct == 1
        if not questioner.current_question.multiple_choice:
            assert 'richtig!' in answer_message_text

    def test_truncate_long_answers(self, bot, chat_id, empty_orchestra, monkeypatch, empty_member):
        poll_message = None

        def send_poll(*args, **kwargs):
            nonlocal poll_message
            poll_message = fake_poll()
            poll_message.poll.options = [PollOption(o, 0) for o in kwargs['options']]
            return poll_message

        monkeypatch.setattr(bot, 'send_poll', send_poll)

        for i in range(10):
            empty_orchestra.register_member(Member(i, nickname=str(i), last_name=150 * str(i)))
        empty_orchestra.register_member(empty_member)

        questioner = Questioner(
            user_id=int(chat_id),
            orchestra=empty_orchestra,
            hint_attributes=['nickname'],
            question_attributes=['last_name'],
            number_of_questions=42,
            bot=bot,
            multiple_choice=True,
        )

        questioner.ask_question()
        assert questioner.number_of_questions_asked == 1
        for option in poll_message.poll.options:
            assert option.text[-4:] == ' ...'

    @pytest.mark.parametrize('populated_orchestra', [{}], indirect=True)
    def test_no_current_question(self, bot, chat_id, populated_orchestra, empty_member):
        populated_orchestra.register_member(empty_member)
        questioner = Questioner(
            user_id=int(chat_id),
            orchestra=populated_orchestra,
            hint_attributes=[],
            question_attributes=[],
            number_of_questions=42,
            bot=bot,
        )
        update = Update(123, poll_answer=PollAnswer(chat_id, User(chat_id, '', False), [1]))

        assert not questioner.check_update(update)
        with pytest.raises(RuntimeError, match='current question'):
            questioner.handle_update(update)

    def test_no_more_questions_to_ask(self, bot, chat_id, empty_orchestra, empty_member):
        empty_orchestra.register_member(empty_member)
        for i in range(4):
            empty_orchestra.register_member(Member(i, nickname=str(i), last_name=str(i)))

        questioner = Questioner(
            user_id=int(chat_id),
            orchestra=empty_orchestra,
            hint_attributes=['nickname'],
            question_attributes=['last_name'],
            number_of_questions=42,
            bot=bot,
        )
        questioner.number_of_questions_asked = 42
        with pytest.raises(RuntimeError, match='No more questions to ask!'):
            questioner.ask_question()

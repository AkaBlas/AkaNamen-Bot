#!/usr/bin/env python
import pytest
import datetime as dt

from copy import copy
from time import sleep

from components import GameHandler, Question, Member, Gender, instruments, GameConfigurationUpdate
from components.gamehandler import TriggerFirstQuestionUpdate, AnswerHandler
from components.constants import GAME_IN_PROGRESS_KEY
from telegram import Update, Poll, PollAnswer, Message, User, Chat, MessageEntity
from telegram.ext import CallbackContext, Job


class ConcreteGameHandler(GameHandler):

    def entry_callback(self, update: Update, context: CallbackContext) -> None:
        pass


@pytest.fixture(scope='function')
def game_handler():
    return ConcreteGameHandler(start_command='start',
                               exit_command='exit',
                               config_handlers=[],
                               question_timeout=1.11)


@pytest.fixture(scope='function')
def callback_context(dp):
    return CallbackContext(dp)


class TestGameHandler:

    class TestTriggerFirstQuestionUpdate:

        def test_init(self):
            tfqu = TriggerFirstQuestionUpdate(42)
            assert tfqu.chat_id == 42

        def test_trigger_first_question(self, dp):

            def job_callback(c):
                pass

            job = Job(job_callback, context=42, repeat=False)
            context = CallbackContext.from_job(job, dp)
            TriggerFirstQuestionUpdate.trigger_first_question(context)
            update = context.update_queue.get()
            assert isinstance(update, TriggerFirstQuestionUpdate)
            assert update.chat_id == 42

    @pytest.fixture(scope='function')
    def answer_handler(self, game_handler):
        member = Member(1,
                        first_name='first',
                        last_name='last',
                        nickname='nickname',
                        gender=Gender.DIVERSE,
                        date_of_birth=dt.date(dt.date.today().year - 21, 12, 31),
                        instruments=instruments.AltoSaxophone(),
                        address='Universitätsplatz 2, 38106 Braunschweig')
        poll = Poll(123, 'question', [member.first_name, member.last_name], 0, False, False,
                    Poll.QUIZ, False, 0)
        question_1 = Question(member, Question.FIRST_NAME, multiple_choice=True, poll=poll)
        question_2 = Question(member, Question.LAST_NAME, multiple_choice=False)
        game_handler._current_question[1] = question_1
        game_handler._current_question[2] = question_2
        return AnswerHandler(game_handler, None)

    class TestAnswerHandler:

        def test_check_update_and_collect_context(self, answer_handler, callback_context, dp):
            games_in_progress = {1: True, 2: True, 3: False}
            callback_context.bot_data[GAME_IN_PROGRESS_KEY] = games_in_progress
            answer_handler.game_handler.games_in_progress = callback_context.bot_data[
                GAME_IN_PROGRESS_KEY]

            update_1 = Update(1, poll_answer=PollAnswer(123, None, [0]))
            out = answer_handler.check_update(update_1)
            assert out[0] == 1
            assert isinstance(out[1], Question)
            assert out[1].attribute == Question.FIRST_NAME

            context = copy(callback_context)
            answer_handler.collect_additional_context(context, update_1, dp, out)
            assert context.games_chat_id == 1
            assert context.answer_is_correct is True

            update_2 = Update(2, message=Message(1, None, None, None, text='wrong'))
            out = answer_handler.check_update(update_2)
            assert out[0] == 2
            assert isinstance(out[1], Question)
            assert out[1].attribute == Question.LAST_NAME

            context = copy(callback_context)
            answer_handler.collect_additional_context(context, update_2, dp, out)
            assert context.games_chat_id == 2
            assert context.answer_is_correct is False

            update_3 = Update(3, pre_checkout_query=True)
            assert not answer_handler.check_update(update_3)

    def test_init(self, game_handler):
        assert game_handler.start_command == 'start'
        assert game_handler.exit_command == 'exit'
        assert game_handler.config_handlers == []
        assert pytest.approx(game_handler.question_timeout) == 1.11
        gh = ConcreteGameHandler(start_command='start', exit_command='exit', config_handlers=[])
        assert gh.question_timeout == 0

    def test_entry_callback(self, game_handler, monkeypatch, callback_context, bot):
        entry_test_flag = False
        busy_test_flag = False

        def entry_callback(*args, **kwargs):
            nonlocal entry_test_flag
            entry_test_flag = True

        def send_message(*args, **kwargs):
            nonlocal busy_test_flag
            chat_id = args[0] == 3
            text = 'leider immer' in args[1]
            busy_test_flag = chat_id and text

        monkeypatch.setattr(game_handler, 'entry_callback', entry_callback)
        monkeypatch.setattr(callback_context.bot, 'send_message', send_message)
        dp = callback_context.dispatcher
        dp.add_handler(game_handler)

        entry_update = Update(1,
                              message=Message(
                                  1,
                                  User(1, 'first', False),
                                  None,
                                  Chat(1, 'private'),
                                  text='/start',
                                  entities=[MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)],
                                  bot=bot))
        dp.process_update(entry_update)
        assert game_handler.games_in_progress[1] is True
        assert entry_test_flag is True
        assert game_handler.conversations[(1,)] == game_handler.CONFIGURING
        assert game_handler.number_of_sent_questions[1] == 0

        game_handler.games_in_progress[3] = True
        busy_update = Update(1,
                             message=Message(
                                 1,
                                 User(1, 'first', False),
                                 None,
                                 Chat(3, 'group'),
                                 text='/start',
                                 entities=[MessageEntity(MessageEntity.BOT_COMMAND, 0, 6)],
                                 bot=bot))
        dp.process_update(busy_update)
        assert game_handler.games_in_progress[3] is True
        assert busy_test_flag is True
        assert (3,) not in game_handler.conversations

    def test_handle_configuration_update(self, game_handler, callback_context, monkeypatch):
        sending_test_flag = False

        def _send_next_message(*args):
            nonlocal sending_test_flag
            sending_test_flag = args[0] == 1

        dp = callback_context.dispatcher
        dp.add_handler(game_handler)
        game_handler._conversations[(1,)] = game_handler.CONFIGURING
        gcu = GameConfigurationUpdate(
            1,
            multiple_choice=True,
            question_attributes=[Question.FIRST_NAME, Question.LAST_NAME],
            hint_attributes=[Question.INSTRUMENT],
            number_of_questions=5)
        dp.process_update(gcu)
        assert game_handler.multiple_choice == {1: True}
        assert game_handler.question_attributes == {1: [Question.FIRST_NAME, Question.LAST_NAME]}
        assert game_handler.hint_attributes == {1: [Question.INSTRUMENT]}
        assert game_handler.number_of_questions == {1: 5}
        assert game_handler.conversations[(1,)] == game_handler.GUESSING

        sleep(0.2)
        assert sending_test_flag is True

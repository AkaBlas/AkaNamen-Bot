#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the GameHandler class."""
from components import Question, GameConfigurationUpdate, question_text
from components.constants import ORCHESTRA_KEY, GAME_IN_PROGRESS_KEY

import random

from _collections import defaultdict
from abc import ABC, abstractmethod
from threading import Lock

from telegram.ext import (ConversationHandler, CallbackContext, TypeHandler, CommandHandler,
                          Handler, Job, Dispatcher)
from telegram import Update, Poll

from typing import Dict, List, Optional, TYPE_CHECKING, Callable, Union, Tuple
if TYPE_CHECKING:
    from components import Orchestra  # noqa: F401


class TriggerFirstQuestionUpdate:

    def __init__(self, chat_id: int) -> None:
        self.chat_id = chat_id

    @staticmethod
    def trigger_first_question(context: CallbackContext) -> None:
        chat_id = context.job.context
        context.update_queue.put(TriggerFirstQuestionUpdate(chat_id))


class AnswerHandler(Handler):

    def __init__(self, game_handler: 'GameHandler', callback: Callable[[Update, CallbackContext],
                                                                       str]) -> None:
        super().__init__(callback)
        self.game_handler = game_handler

    def check_update(self, update: Update) -> Optional[Tuple[int, Question]]:
        games_in_progress = self.game_handler.games_in_progress
        for chat_id, is_active in games_in_progress.items():
            if is_active and self.game_handler.current_question[chat_id].check_update(update):
                return chat_id, self.game_handler.current_question[chat_id]
        return None

    def collect_additional_context(self, context: CallbackContext, update: Update,
                                   dispatcher: Dispatcher, check_result: Tuple[int,
                                                                               Question]) -> None:
        context.games_chat_id = check_result[0]
        context.question = check_result[1]
        context.answer_is_correct = context.question.check_answer(update)


class GameHandler(ABC, ConversationHandler):
    """
    A :class:`telegram.ext.ConversationHandler` acting as base class for game handlers for the
    specific games of the AkaNamen Bot. A game conversation has the following structure:

    * A new game is begun by a command set as :attr:`start_command`. The initial update is handled
      by :meth:`entry_callback` and transitions the conversation in the :attr:`CONFIGURING` state.
    * For the :attr:`CONFIGURING` state, any list of handlers may be set as
      :attr:`config_handlers`, e.g. a nested :class:`telegram.ext.ConversationHandler` can be used
      with a corresponding :attr:`telegram.ext.ConversationHandler.map_to_parent`.
      To exit the :attr:`CONFIGURING` state, enqueue a :class:`components.GameConfigurationUpdate`
      in the :attr:`telegram.ext.Dispatcher.update_queue`.

      The :class:`components.GameConfigurationUpdate` is then used to actually set the
      configuration parameters collected from the user. You may subclass it to allow for more
      settings, but you must make sure that the attributes are named exactly like the corresponding
      attributes of the game handler class receiving those updates.

      The configuration process must ensure that enough members with the selected attributes
      are available to actually build questions.
    * In the :attr:`GUESSING` state, the methods :meth:`send_next_question` and
      :meth:`handle_answer` are used. If :attr:`question_timeout` is greater than zero, any
      question will be marked as answered after :attr:`question_timeout` seconds and the next
      question is asked. In that case, :meth:`question_timeout` is called with the corresponding
      ``chat_id``.
      To end the game, return :attr:`telegram.ext.ConversationHandler.END` from either of the
      mentioned methods.
      Alternatively, you may return :attr:`RECONFIGURING`, to enter the corresponding state.
    * Any game can be interrupted at any point by the command set as :attr:`exit_command`. For
      multiple choice games, the last poll will be closed in that case.

    POLLS MUST BE SEND AS NON ANONYMUS IN ORDER TO RECEIVE POLL ANSWERS
    BIRTDAYS MUST BE ENTERED AS DD.MM.
    FOR ISTRUMENT FREE TEXT, SHOW KEYBOARD WITH AVAILABLE OPTIONS

    Args:
        start_command: The command to be used to start the components.
        exit_command: The command to be used to interrupt the components.
        config_handlers: Handlers for the :attr:`CONFIGURING` state.
        question_timeout: Close questions after :attr:`question_timeout` seconds. Defaults to ``0``
            , i.e. no timeout.
    """

    def __init__(self,
                 start_command: str,
                 exit_command: str,
                 config_handlers: List[Handler],
                 question_timeout: Optional[int] = None) -> None:
        self.games_in_progress: Dict[int, bool] = {}

        self._start_command = start_command.strip('/').strip(' ')
        self._exit_command = exit_command.strip('/').strip(' ')
        self._config_handlers = config_handlers

        if question_timeout is None:
            self._question_timeout = 0
        else:
            self._question_timeout = question_timeout

        self._current_question: Dict[int, Question] = {}
        self._current_question_lock = Lock()

        self._current_question_message_id: Dict[int, Question] = {}
        self._current_question_message_id_lock = Lock()

        self._multiple_choice: Dict[int, bool] = {}
        self._multiple_choice_lock = Lock()

        self._question_attributes: Dict[int, List[str]] = {}
        self._question_attributes_lock = Lock()

        self._hint_attributes: Dict[int, List[str]] = {}
        self._hint_attributes_lock = Lock()

        self._number_of_questions: Dict[int, int] = {}
        self._number_of_questions_lock = Lock()

        self._number_of_sent_questions: Dict[int, int] = {}
        self._number_of_sent_questions_lock = Lock()

        self._question_timeout_jobs: Dict[int, Job] = {}
        self._question_timeout_jobs_lock = Lock()

        ConversationHandler.__init__(
            self,
            entry_points=[CommandHandler(self.start_command, self._entry_callback)],
            states={
                self.CONFIGURING:
                    self.config_handlers
                    + [TypeHandler(GameConfigurationUpdate, self._handle_configuration_update)],
                self.GUESSING: [
                    TypeHandler(TriggerFirstQuestionUpdate, self._send_first_question),
                    AnswerHandler(self, self._handle_answer)
                ],  # noqa: E122
            },
            fallbacks=[CommandHandler(self._exit_command, self._exit_callback)],
            per_user=False,
        )

    @property
    def start_command(self) -> str:
        """The command to be used to start the components."""
        return self._start_command

    @property
    def exit_command(self) -> str:
        """The command to be used to interrupt the components."""
        return self._exit_command

    @property
    def config_handlers(self) -> List[Handler]:
        """Handlers for the :attr:`CONFIGURING` state."""
        return self._config_handlers

    @property
    def question_timeout(self) -> int:
        """Timeout for questions. If ``0``, there is not timeout."""
        return self._question_timeout

    @property
    def current_question(self) -> Dict[int, Question]:
        """
        For each chat ID ``chat_id``, ``current_question[chat_id]`` is a
        :class:`components.Question` instance representing the question currently asked in the chat
        for this components.
        """
        with self._current_question_lock:
            return self._current_question

    @property
    def current_question_message_id(self) -> Dict[int, Question]:
        """
        For each chat ID ``chat_id``, ``current_question_message_id[chat_id]`` is the message id
        of the question currently asked in the chat for this components.
        """
        with self._current_question_message_id_lock:
            return self._current_question_message_id

    @property
    def multiple_choice(self) -> Dict[int, bool]:
        """
        For each chat ID ``chat_id``, ``multiple_choice[chat_id]`` indicates, whether the current
        game of that chat is multiple choice or not.
        """
        with self._multiple_choice_lock:
            return self._multiple_choice

    @property
    def question_attributes(self) -> Dict[int, List[str]]:
        """
        For each chat ID ``chat_id``, ``question_attributes[chat_id]`` is a list of the attributes
        to be asked for in the questions.
        """
        with self._question_attributes_lock:
            return self._question_attributes

    @property
    def hint_attributes(self) -> Dict[int, List[str]]:
        """
        For each chat ID ``chat_id``, ``hint_attributes[chat_id]`` is a list of the attributes
        to be given as hint in the questions.
        """
        with self._hint_attributes_lock:
            return self._hint_attributes

    @property
    def number_of_questions(self) -> Dict[int, int]:
        """
        For each chat ID ``chat_id``, ``number_of_questions[chat_id]`` is the number of questions
        to be asked in the chats components.
        """
        with self._number_of_questions_lock:
            return self._number_of_questions

    @property
    def number_of_sent_questions(self) -> Dict[int, int]:
        """
        For each chat ID ``chat_id``, ``number_of_questions[chat_id]`` is the number of questions
        that where already asked in the chats components.
        """
        with self._number_of_sent_questions_lock:
            return self._number_of_sent_questions

    @abstractmethod
    def entry_callback(self, update: Update, context: CallbackContext) -> None:
        """
        Initial callback for the game, triggered by a message containing :attr:`start_command`.

        Note:
            Must be implemented by any concrete subclass.

        Args:
            update: The :class:`telegram.Update`.
            context: The :class:`telegram.ext.CallbackContext`.
        """

    def handle_answer(self, update: Update, context: CallbackContext):
        """
        Will by called, when a user gives an answer to a question. Override to e.g. update the
        users score.

        Args:
            update: The :class:`telegram.Update`.
            context: The :class:`telegram.ext.CallbackContext`.
        """
        pass

    def end_callback(self, update: Update, context: CallbackContext):
        """
        Will by called, after handling the last answer of the components. Override to e.g. show the
        users score.

        Args:
            update: The :class:`telegram.Update`.
            context: The :class:`telegram.ext.CallbackContext`.
        """
        pass

    def exit_callback(self, update: Update, context: CallbackContext):
        """
        Will by called, if the game is interrupted by the user.

        Args:
            update: The :class:`telegram.Update`.
            context: The :class:`telegram.ext.CallbackContext`.
        """
        pass

    def _entry_callback(self, update: Update, context: CallbackContext) -> str:
        if GAME_IN_PROGRESS_KEY in context.bot_data:
            self.games_in_progress = context.bot_data[GAME_IN_PROGRESS_KEY]
            games_in_progress = self.games_in_progress
        else:
            games_in_progress = defaultdict(lambda: False)
            context.bot_data[GAME_IN_PROGRESS_KEY] = games_in_progress
            self.games_in_progress = games_in_progress

        chat_id = update.effective_chat.id
        if games_in_progress.get(chat_id, False):
            update.message.reply_text('Es kann leider immer nur ein Spiel laufen.')
            return self.END
        else:
            games_in_progress[chat_id] = True
            self.number_of_sent_questions[chat_id] = 0
            self.entry_callback(update, context)
            return self.CONFIGURING

    def _exit_callback(self, update: Update, context: CallbackContext) -> int:
        chat_id = context.games_chat_id
        if chat_id is None:
            raise ValueError('I need a chat_id in GameHandler._exit_callback!')
        if self.multiple_choice[chat_id]:
            context.bot.stop_poll(chat_id=chat_id,
                                  message_id=self.current_question_message_id[chat_id])
        context.games_in_progress[chat_id] = False
        self.exit_callback(update, context)
        return self.END

    def _handle_configuration_update(self, update: GameConfigurationUpdate,
                                     context: CallbackContext) -> str:
        print('IM HERE YOU BICH')
        chat_id = update.chat_id
        attrs = [a for a in dir(update) if a != 'chat_id']
        for attr in attrs:
            if hasattr(self, f'_{attr}'):
                # get the lock
                with getattr(self, f'_{attr}_lock'):
                    # Set the attribute for the correct chat_id
                    self_attr = getattr(self, f'_{attr}')
                    self_attr[chat_id] = getattr(update, attr)
        job = context.job_queue.run_once(TriggerFirstQuestionUpdate.trigger_first_question,
                                         0.1,
                                         context=chat_id)
        with self._question_timeout_jobs_lock:
            self._question_timeout_jobs[chat_id] = job
        return self.GUESSING

    def _send_or_end(self, chat_id: int, update: Update, context: CallbackContext) -> str:
        if self.number_of_sent_questions[chat_id] == self.number_of_questions[chat_id]:
            self.end_callback(update, context)
            return self.END
        else:
            if self.multiple_choice[chat_id]:
                context.bot.stop_poll(chat_id=chat_id,
                                      message_id=self.current_question_message_id[chat_id])
            self._send_next_question(chat_id, update, context)
            return self.GUESSING

    def _trigger_question_timeout(self, context: CallbackContext):
        update = context.job.context[0]
        callback_context = context.job.context[1]

        if isinstance(update, TriggerFirstQuestionUpdate):
            chat_id = update.chat_id
        else:
            chat_id = callback_context.games_chat_id

        self._send_or_end(chat_id, update, callback_context)

    def _send_next_question(self, chat_id: int, update: Union[Update, TriggerFirstQuestionUpdate],
                            context: CallbackContext) -> Question:
        bot = context.bot
        orchestra = context.bot_data[ORCHESTRA_KEY]

        question_attribute = random.choice(self.question_attributes[chat_id])

        if question_attribute == Question.ADDRESS:
            # GameConfigurationUpdate makes sure that this is allowed
            hint_attribute = Question.FULL_NAME
        else:
            hint_attributes = [a for a in self.hint_attributes[chat_id] if a != question_attribute]
            hint_attribute = random.choice(hint_attributes)

        member_hint_attribute = Question.MAP_ATTRIBUTES[hint_attribute]
        member_question_attribute = Question.MAP_ATTRIBUTES[question_attribute]

        # A this point, we just assume that such members exist. The config process should
        # be taking care of that.
        potential_members = [
            m for m in orchestra.members
            if (getattr(m, member_hint_attribute) and getattr(m, member_question_attribute))
        ]
        # MyPy thinks that choice returns an int ...
        member = random.choice(potential_members)  # type: ignore

        # Generate the question text
        multiple_choice = self.multiple_choice[chat_id]
        question_txt = question_text(member, question_attribute, hint_attribute, multiple_choice)

        if multiple_choice:
            potential_answer_members = [
                m for m in orchestra.members
                if m not in getattr(orchestra, orchestra.ATTRS_TO_LISTS[member_question_attribute])
                [member_question_attribute]
            ]
            # Comparing Klaus to Gerda would be too obvious ...
            if question_attribute == Question.FIRST_NAME:
                potential_answer_members = [
                    p for p in potential_answer_members if p.gender == member.gender
                ]
            answer_members = random.sample(potential_answer_members, 3)

            all_members = answer_members + [member]
            random.shuffle(all_members)
            correct_option_id = all_members.index(member)
            options = [getattr(m, hint_attribute) for m in all_members]

            message = bot.send_poll(chat_id=chat_id,
                                    question=question_txt,
                                    options=options,
                                    is_anonymous=False,
                                    type=Poll.QUIZ,
                                    correct_option_id=correct_option_id)

            question = Question(member=member, attribute=question_attribute, poll=message.poll)
        else:
            message = bot.send_message(chat_id=chat_id, text=question_txt)
            question = Question(member=member, attribute=question_attribute, multiple_choice=False)

        self.number_of_sent_questions[chat_id] += 1
        self.current_question[chat_id] = question
        self.current_question_message_id[chat_id] = message.message_id

        with self._question_timeout_jobs_lock:
            if self.question_timeout > 0:
                self._question_timeout_jobs[chat_id] = context.job_queue.run_once(
                    self._trigger_question_timeout,
                    self.question_timeout,
                    context=(update, context))
        return question

    def _send_first_question(self, update: TriggerFirstQuestionUpdate, context: CallbackContext):
        self._send_next_question(update.chat_id, update, context)

    def _handle_answer(self, update: Update, context: CallbackContext) -> str:
        chat_id = context.games_chat_id

        if chat_id is None:
            raise ValueError('I need a chat_id in GameHandler._handle_answer!')

        with self._question_timeout_jobs_lock:
            timeout_job = self._question_timeout_jobs.pop(chat_id, None)
            if timeout_job is not None:
                timeout_job.schedule_removal()

        self.handle_answer(update, context)
        return self._send_or_end(chat_id, update, context)

    # States
    CONFIGURING = 'configuring'
    """:obj:`str`: Configuration state of the components."""
    GUESSING = 'guessing'
    """:obj:`str`: Guessing state of the game, i.e. the state where the questions are answered."""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Question class."""
from components import Question, Orchestra, question_text, PHOTO_OPTIONS, Score, \
    AttributeManager

import random
from telegram import Update, Bot, Poll, InputMediaPhoto
from typing import List, Optional, Tuple


class Questioner:
    """
    Helper class generating and tracking the questions of a single game for a single user.

    Attributes:
        member (:class:`components.Member`): The member, this instance is associated with.
        orchestra (:class:`components.Orchestra`): The orchestra, this instance is associated with.
        hint_attributes (List[:obj:`str`]): Subset of the keys of
            :attr:`components.Question.SUPPORTED_ATTRIBUTES`. These will be given as hints for the
            questions.
        question_attributes (List[:obj:`str`]): Subset of the keys of
            :attr:`components.Question.SUPPORTED_ATTRIBUTES`. These will be asked for in the
            questions.
        number_of_questions (:obj:`int`): Number of questions to ask the user.
        number_of_questions_asked (:obj:`int`): Number of questions already asked.
        current_question (:class:`components.Question`): Optional. The question currently presented
            to the user.
        bot (:class:`telegram.Bot`): The bot to use for asking questions.
        multiple_choice (:obj:`bool`): Whether the question to be asked are multiple choice or free
            text.
        score (:class:`components.Score`): The score for this game.

    Args:
        user_id: The ID of the user this instance is associated with.
        orchestra: The orchestra, this instance is associated with.
        hint_attributes: List of strings, appearing either in
            :attr:`components.Question.SUPPORTED_ATTRIBUTES`. These will be given as hints for the
            questions. May be empty, in which case all available attributes are allowed.
        question_attributes: List of strings, appearing either in
            :attr:`components.Question.SUPPORTED_ATTRIBUTES`. These will be asked for in the
            questions. May be empty, in which case all available attributes are allowed.
        number_of_questions: Number of questions to ask the user.
        bot: The bot to use for asking questions.
        multiple_choice: Whether the question to be asked are multiple choice or free text.
            Defaults to :obj:`True`.

        Note:
            ``fe/male_first_names`` is valid for neither :attr:`hint_attributes` nor
            :attr:`question_attributes`.
    """

    def __init__(self,
                 user_id: int,
                 orchestra: Orchestra,
                 hint_attributes: List[str],
                 question_attributes: List[str],
                 number_of_questions: int,
                 bot: Bot,
                 multiple_choice: bool = True) -> None:

        self.bot = bot
        self.multiple_choice = multiple_choice
        self.orchestra = orchestra
        self.member = self.orchestra.members[user_id]
        self.score = Score(member=self.member)
        self.current_question: Optional[Question] = None
        self._available_members_recurse = True

        if number_of_questions <= 0:
            raise ValueError('Number of questions must be greater than zero. Joke Cookie.')
        else:
            self.number_of_questions = number_of_questions
        self.number_of_questions_asked = 0

        # Filter stupid input
        if (len(hint_attributes) == 1 and len(question_attributes) == 1
                and hint_attributes == question_attributes):
            raise ValueError('Allowing the same single attribute for both hints and questions '
                             'wont be very interesting.')

        # Filter generally unsupported input
        for index, ha in enumerate(hint_attributes):
            if ha in Question.SUPPORTED_ATTRIBUTES:
                hint_attributes[index] = ha
            else:
                raise ValueError(f'Unsupported hint attribute {ha}.')
        for index, qa in enumerate(question_attributes):
            if qa in Question.SUPPORTED_ATTRIBUTES:
                question_attributes[index] = qa
            else:
                raise ValueError(f'Unsupported question attribute {qa}.')

        # Filter input unsupported for the orchestras state
        questionable = self.orchestra.questionable(self.multiple_choice,
                                                   exclude_members=[self.member])

        available_hints = [q[0] for q in questionable]
        available_questions = [q[1] for q in questionable]
        for ha in hint_attributes:
            if ha not in available_hints:
                raise ValueError(f'Attribute {ha} not available as hint for this orchestra.')
        for qa in question_attributes:
            if qa not in available_questions:
                raise ValueError(f'Attribute {qa} not available as question for this orchestra.')

        if not hint_attributes:
            hint_attributes = list(q[0].description for q in questionable)
        if not question_attributes:
            question_attributes = list(q[1].description for q in questionable)

        # yapf: disable
        if not any(
                (ha, qa) in questionable for ha in hint_attributes for qa in question_attributes):
            # yapf: enable
            raise ValueError('No valid hint-question combination available.')

        self.hint_attributes = hint_attributes
        self.question_attributes = question_attributes

    def check_update(self, update: Update) -> bool:
        """
        Checks, if th given update is a valid response to the current question and can be handled
        by :meth:`current_question.check_answer`. Will return :obj:`False`, if there is no current
        question.

        Args:
            update: The :class:`telegram.Update` to be tested.
        """
        if not update.effective_user:
            return False
        if update.effective_user.id != self.member.user_id:
            return False
        if not self.current_question:
            return False
        return self.current_question.check_update(update)

    def handle_update(self, update: Update) -> None:
        """
        Handles the given update. Call only, if :meth:`check_update` returned :obj:`True`.

        Args:
            update: The :class:`telegram.Update` to be tested.
        """
        question = self.current_question

        if not question:
            raise RuntimeError('I dont have a current question.')
        is_correct = question.check_answer(update)
        self.score.answers += 1
        self.score.correct += int(is_correct)

        if not question.multiple_choice:
            if is_correct:
                text = 'Das war richtig! 👍'
            else:
                text = (f'Das war leider nicht korrekt. 😕 '
                        f'Die richtige Antwort lautet »{question.correct_answer}«')
            update.message.reply_text(text=text)

    def questionable(self) -> List[Tuple[AttributeManager, AttributeManager]]:
        """
        Gives a list of tuples of :class:`components.AttributeManager` instances, each representing
        a pair of hint attribute and question attribute, which is questionable for
        :attr:`orchestra` *and* is allowed for this questioner instance.
        """
        return [(h, q)
                for (h, q) in self.orchestra.questionable(self.multiple_choice,
                                                          exclude_members=[self.member])
                if h in self.hint_attributes and q in self.question_attributes]

    def ask_question(self) -> None:
        """
        Asks the next question, if there is another.

        Raises:
            RuntimeError: If there are no more questions to be asked.
        """
        if self.number_of_questions_asked == self.number_of_questions:
            raise RuntimeError('No more questions to ask!')

        hint_manager, question_manager = random.choice(self.questionable())
        hint_attribute = hint_manager.description
        question_attribute = question_manager.description

        if question_manager.description == Question.PHOTO:
            multiple_choice = True
            photo_question = True
        else:
            multiple_choice = self.multiple_choice
            photo_question = False

        if multiple_choice:
            member, hint, opts, index = hint_manager.build_question_with(
                question_manager, multiple_choice=True, exclude_members=[self.member])
            question = question_text(member,
                                     question_attribute,
                                     hint_attribute,
                                     multiple_choice=True)
            options = list(str(o) for o in opts)

            # Truncate long options
            for idx, o in enumerate(options):
                if len(o) > 100:
                    options[idx] = o[:96] + ' ...'

            # Send photos if needed
            if photo_question:
                self.bot.send_media_group(
                    chat_id=self.member.user_id,
                    media=[InputMediaPhoto(options[0]),
                           InputMediaPhoto(options[1])])
                self.bot.send_media_group(
                    chat_id=self.member.user_id,
                    media=[InputMediaPhoto(options[2]),
                           InputMediaPhoto(options[3])])
            if hint_attribute == Question.PHOTO:
                self.bot.send_photo(chat_id=self.member.user_id, photo=hint)

            # Send the question
            poll = self.bot.send_poll(chat_id=self.member.user_id,
                                      question=question,
                                      options=(PHOTO_OPTIONS if photo_question else options),
                                      is_anonymous=False,
                                      type=Poll.QUIZ,
                                      correct_option_id=index).poll
            self.current_question = Question(member,
                                             question_attribute,
                                             poll=poll,
                                             multiple_choice=multiple_choice)
        else:
            member, hint, _ = hint_manager.build_question_with(question_manager,
                                                               multiple_choice=False,
                                                               exclude_members=[self.member])
            question = question_text(member,
                                     question_attribute,
                                     hint_attribute,
                                     multiple_choice=False,
                                     hint_value=hint)
            if hint_attribute == Question.PHOTO:
                self.bot.send_photo(chat_id=self.member.user_id,
                                    photo=member.photo_file_id,
                                    caption=question)
            else:
                self.bot.send_message(chat_id=self.member.user_id, text=question)
            self.current_question = Question(member,
                                             question_attribute,
                                             multiple_choice=multiple_choice)

        self.number_of_questions_asked += 1

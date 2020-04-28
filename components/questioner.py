#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Question class."""
from components import Member, Question, Orchestra, question_text, PHOTO_OPTIONS, Score

import random
from telegram import Update, Bot, Poll
from collections import defaultdict
from typing import List, Dict, Set, Optional


class Questioner:
    """
    Helper class generating and tracking the questions of a single game for a single user.

    Attributes:
        member (:class:`components.Member`): The member, this instance is associated with.
        orchestra (:class:`components.Orchestra`): The orchestra, this instance is associated with.
        hint_attributes (List[:obj:`str`]): Subset of
            :attr:`components.Question.SUPPORTED_ATTRIBUTES`. These will be given as hints for the
            questions.
        question_attributes (List[:obj:`str`]): Subset of
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
        used_members (Dict[:obj:`str`, Set[:class:`components.Member`]]): For every attribute in
            :attr:`hint_attributes` the corresponding set will contain all members of
            :attr:`orchestra`, whose corresponding attribute was already subject to a question
            *and was answered correctly`.

    Args:
        user_id: The ID of the user this instance is associated with.
        orchestra: The orchestra, this instance is associated with.
        hint_attributes: Subset of :attr:`components.Question.SUPPORTED_ATTRIBUTES`. These will be
            given as hints for the questions. May be empty, in which case all are allowed.
        question_attributes: Subset of :attr:`components.Question.SUPPORTED_ATTRIBUTES`. These will
            be asked for in the questions. May be empty, in which case all are allowed.
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
        self.used_members: Dict[str, Set[Member]] = defaultdict(set)
        self._available_members_recurse = True

        if number_of_questions <= 0:
            raise ValueError('Number of questions must be greater than zero. Joke Cookie.')
        else:
            self.number_of_questions = number_of_questions
        self.number_of_question_asked = 0

        if (len(hint_attributes) == len(question_attributes)
                and hint_attributes == question_attributes):
            raise ValueError('Allowing the same single attribute for both hints and questions '
                             'wont be very interesting.')

        if not hint_attributes:
            hint_attributes = orchestra.questionable
        if not question_attributes:
            question_attributes = question_attributes

        if not hint_attributes or not question_attributes:
            raise ValueError('hint_attributes and question_attributes must not be empty.')

        questionable = [orchestra.DICTS_TO_ATTRS[q] for q in orchestra.questionable]

        for ha in hint_attributes:
            if ha not in questionable:
                raise ValueError(f'{ha} is not a questionable attribute for this orchestra.')

        for qa in question_attributes:
            if ((('female_first_names' not in orchestra.questionable
                  or 'male_first_names' not in orchestra.questionable)
                 and qa == Question.FIRST_NAME) or qa not in questionable):
                raise ValueError(f'{qa} is not a questionable attribute for this orchestra.')

        self.hint_attributes = hint_attributes
        self.question_attributes = question_attributes

    def _clear_used_members(self):
        self.used_members = defaultdict(set)

    def available_members(self, hint_attribute) -> Dict[str, Set[Member]]:
        """
        For an attribute ``k`` in :attr:`question_attribute`, the corresponding value is the set
        of all members of :attr:`orchestra`, which have both the :attr:`hint_attribute` passed to
        this function an the attribute ``k`` acting as key for this very set *and* and not listed
        in the corresponding set of :attr:`used_members`.

        Note:
            * If ``hint_attribute`` is in :attr:`question_attributes`, it will not be present as
              key.
            * Attributes, whose corresponding sets have fewer than four members, are discarded.
            * If the resulting dictionary would only have entries with fewer than four members,
              :attr:`used_members` will automatically be emptied and the result is re-computed.
        """
        out = defaultdict(set)
        question_attributes = [qh for qh in self.question_attributes if qh != hint_attribute]
        for m in self.orchestra.members.values():
            if m[hint_attribute] is not None:
                for attr in question_attributes:
                    if m[attr] is not None:
                        out[attr].add(m)
        out = {k: v for k, v in out.items() if len(v) >= 4}
        if not out and self._available_members_recurse:
            self._clear_used_members()
            self._available_members_recurse = False
            return self.available_members(hint_attribute)
        else:
            self._available_members_recurse = True
            return out

    def check_update(self, update: Update) -> bool:
        """
        Checks, if th given update is a valid response to the current question and can be handled
        by :meth:`current_question.check_answer`. Will return :obj:`False`, if there is no current
        question.

        Args:
            update: The :class:`telegram.Update` to be tested.
        """
        if update.effective_user.id != self.member.user_id:
            return False
        if not self.current_question:
            return False
        return self.current_question.check_update(update)

    def handle_update(self, update: Update) -> None:
        """
        Handles the given update by updating the :class:`components.UserScore` of
        :attr:`member`. Call only, if :meth:`check_update` returned :obj:`True`.

        Args:
            update: The :class:`telegram.Update` to be tested.
        """
        question = self.current_question

        if not question:
            raise ValueError('I dont have a current question.')
        is_correct = question.check_answer(update)
        self.member.user_score.add_to_score(1, int(is_correct))
        self.score.answers += 1
        self.score.correct += int(is_correct)
        
        if is_correct:
            self.used_members[question.attribute].add(question.member)

        if not question.multiple_choice:
            if is_correct:
                text = 'Das wir richtig! 👍'
            else:
                text = (f'Das war leider nicht korrekt. 😕'
                        f'Die richtige Antwort lautet »{question.correct_answer}«')
            update.message.reply_text(text)

    def ask_question(self):
        """
        Asks the next question.
        """
        hint_attribute = random.choice(self.hint_attributes)
        multiple_choice = True if hint_attribute == Question.PHOTO else self.multiple_choice

        available_members = self.available_members(hint_attribute)
        question_attribute = random.choice(available_members.keys())

        member = random.choice(available_members[question_attribute])
        question = question_text(member, question_attribute, hint_attribute, multiple_choice)

        if multiple_choice:
            index, members = self.orchestra.draw_members(member, question_attribute)
            poll = self.bot.send_poll(
                chat_id=self.member.user_id,
                question=question,
                options=(PHOTO_OPTIONS if question_attribute == Question.PHOTO else
                         [m[question_attribute] for m in members]),
                is_anonymous=False,
                type=Poll.QUIZ,
                correct_option_id=index)
            self.current_question = Question(member, question_attribute, poll=poll)
        else:
            self.bot.send_message(chat_id=self.member.user_id, text=question)
            self.current_question = Question(member,
                                             question_attribute,
                                             multiple_choice=multiple_choice)

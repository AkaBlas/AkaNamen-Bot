#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Question class."""
from components import Member, Question, Orchestra, question_text, PHOTO_OPTIONS, Score

import random
from telegram import Update, Bot, Poll, InputMediaPhoto
from collections import defaultdict
from typing import List, Dict, Set, Optional


class Questioner:
    """
    Helper class generating and tracking the questions of a single game for a single user.

    Attributes:
        member (:class:`components.Member`): The member, this instance is associated with.
        orchestra (:class:`components.Orchestra`): The orchestra, this instance is associated with.
        hint_attributes (List[:obj:`str`]): Subset of the keys of
            :attr:`components.Orchestra.DICTS_TO_ATTRS`. These will be given as hints for the
            questions.
        question_attributes (List[:obj:`str`]): Subset of the keys of
            :attr:`components.Orchestra.DICTS_TO_ATTRS`. These will be asked for in the
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
        hint_attributes: List of strings, appearing either in
            :attr:`components.Question.SUPPORTED_ATTRIBUTES` or as keys in
            :attr:`components.Orchestra.DICTS_TO_ATTRS`. These will be given as hints for the
            questions. May be empty, in which case all available attributes are allowed.
        question_attributes: List of strings, appearing either in
            :attr:`components.Question.SUPPORTED_ATTRIBUTES` or as keys in
            :attr:`components.Orchestra.DICTS_TO_ATTRS`. These will be asked for in the
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
        self.used_members: Dict[str, Set[Member]] = defaultdict(set)
        self._available_members_recurse = True

        if number_of_questions <= 0:
            raise ValueError('Number of questions must be greater than zero. Joke Cookie.')
        else:
            self.number_of_questions = number_of_questions
        self.number_of_question_asked = 0

        # Filter stupid input
        if (len(hint_attributes) == 1 and len(question_attributes) == 1
                and hint_attributes == question_attributes):
            raise ValueError('Allowing the same single attribute for both hints and questions '
                             'wont be very interesting.')

        # Filter generally unsupported input
        for index, ha in enumerate(hint_attributes):
            if ha in Question.SUPPORTED_ATTRIBUTES:
                hint_attributes[index] = Orchestra.ATTRS_TO_DICTS[Question.MAP_ATTRIBUTES[ha]]
            elif ha not in Orchestra.DICTS_TO_ATTRS:
                raise ValueError(f'Unsupported hint attribute {ha}.')
        for index, qa in enumerate(question_attributes):
            if qa in Question.SUPPORTED_ATTRIBUTES:
                question_attributes[index] = Orchestra.ATTRS_TO_DICTS[Question.MAP_ATTRIBUTES[qa]]
            elif qa not in Orchestra.DICTS_TO_ATTRS:
                raise ValueError(f'Unsupported question attribute {qa}.')

        # Filter input unsupported for the orchestras state
        available_hints = [q[0] for q in self.orchestra.questionable]
        available_questions = [q[1] for q in self.orchestra.questionable]
        for ha in hint_attributes:
            if ha not in available_hints:
                raise ValueError(f'Attribute {ha} not available as hint for this orchestra.')
        for qa in question_attributes:
            if qa not in available_questions:
                raise ValueError(f'Attribute {qa} not available as question for this orchestra.')

        if not hint_attributes:
            _hint_attributes = set(q[0] for q in self.orchestra.questionable)
            _hint_attributes.discard('dates_of_birth')
            hint_attributes = list(_hint_attributes)
        if not question_attributes:
            _question_attributes = set(q[1] for q in self.orchestra.questionable)
            _question_attributes.discard('male_first_names')
            _question_attributes.discard('female_first_names')
            _question_attributes.discard('dates_of_birth')
            question_attributes = list(_question_attributes)

        if not hint_attributes or not question_attributes:
            raise ValueError('hint_attributes and question_attributes must not be empty.')

        self.hint_attributes = hint_attributes
        self.question_attributes = question_attributes

    def _clear_used_members(self) -> None:
        self.used_members = defaultdict(set)

    def available_members(self, hint_attribute: str) -> Dict[str, Set[Member]]:
        """
        For an attribute ``k`` in :attr:`question_attribute`, the corresponding value is the set
        of all members of :attr:`orchestra`, which have both the :attr:`hint_attribute` passed to
        this function and the attribute ``k`` acting as key for this very set *and* and are
        not listed in the corresponding set of :attr:`used_members`.

        Note:
            * If ``hint_attribute`` is in :attr:`question_attributes`, it will not be present as
              key.
            * Attributes, whose corresponding sets have fewer than four members, are discarded.
            * If the resulting dictionary would only have entries with fewer than four members,
              :attr:`used_members` will automatically be emptied and the result is re-computed.

        Args:
            hint_attribute: Must be present in either :attr:`components.Orchestra.DICTS_TO_ATTRS`
                as key or in :attr:`components.Question.SUPPORTED_ATTRIBUTES`.

        Raises:
            ValueError: If :attr:`hint_attribute` is invalid.
        """
        out: Dict[str, Set[Member]] = defaultdict(set)
        question_attributes = [qh for qh in self.question_attributes if qh != hint_attribute]
        if hint_attribute in Question.SUPPORTED_ATTRIBUTES:
            hint_attribute = Orchestra.ATTRS_TO_DICTS[Question.MAP_ATTRIBUTES[hint_attribute]]

        if hint_attribute not in Orchestra.DICTS_TO_ATTRS.keys():
            raise ValueError(f'Unsupported value {hint_attribute} for hint_attribute.')

        members_attribute = Orchestra.DICTS_TO_ATTRS[hint_attribute]
        for m in self.orchestra.members.values():
            if m[members_attribute]:
                for attr in question_attributes:
                    if m[Orchestra.DICTS_TO_ATTRS[attr]]:
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
        if not update.effective_user:
            return False
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
            key = Orchestra.ATTRS_TO_DICTS[Question.MAP_ATTRIBUTES[question.attribute]]
            self.used_members[key].add(question.member)

        if not question.multiple_choice:
            if is_correct:
                text = 'Das war richtig! 👍'
            else:
                text = (f'Das war leider nicht korrekt. 😕 '
                        f'Die richtige Antwort lautet »{question.correct_answer}«')
            update.message.reply_text(text=text)

    def ask_question(self) -> None:
        """
        Asks the next question.
        """
        if len(self.question_attributes) == 1:
            choose_from = [ha for ha in self.hint_attributes if ha != self.question_attributes[0]]
        else:
            choose_from = self.hint_attributes
        hint_attribute = random.choice(choose_from)

        available_members = self.available_members(hint_attribute)
        question_attribute: str = random.choice(list(available_members.keys()))
        supported_question_attribute = Question.PAM_ATTRIBUTES[
            Orchestra.DICTS_TO_ATTRS[question_attribute]]

        if Orchestra.DICTS_TO_ATTRS[question_attribute] == Question.PHOTO:
            multiple_choice = True
            photo_question = True
        else:
            multiple_choice = self.multiple_choice
            photo_question = False

        member: Member = random.choice(list(available_members[question_attribute]))
        question = question_text(member, question_attribute, hint_attribute, multiple_choice)

        if multiple_choice:
            index, members = self.orchestra.draw_members(member, question_attribute)

            if isinstance(member[Orchestra.DICTS_TO_ATTRS[question_attribute]], list):
                options = [
                    str(random.choice(
                        m[Orchestra.DICTS_TO_ATTRS[question_attribute]]))  # type: ignore
                    for m in members
                ]
            else:
                options = [str(m[Orchestra.DICTS_TO_ATTRS[question_attribute]]) for m in members]

            # Truncate options
            for idx, o in enumerate(options):
                if len(o) > 100:
                    options[idx] = o[:96] + ' ...'

            # Send photos if needed
            if photo_question:
                self.bot.send_media_group(chat_id=self.member.user_id,
                                          media=[
                                              InputMediaPhoto(members[0].photo_file_id),
                                              InputMediaPhoto(members[1].photo_file_id)
                                          ])
                self.bot.send_media_group(chat_id=self.member.user_id,
                                          media=[
                                              InputMediaPhoto(members[2].photo_file_id),
                                              InputMediaPhoto(members[3].photo_file_id)
                                          ])
            if Orchestra.DICTS_TO_ATTRS[hint_attribute] == Question.PHOTO:
                self.bot.send_photo(chat_id=self.member.user_id, photo=member.photo_file_id)

            # Send the question
            poll = self.bot.send_poll(chat_id=self.member.user_id,
                                      question=question,
                                      options=(PHOTO_OPTIONS if photo_question else options),
                                      is_anonymous=False,
                                      type=Poll.QUIZ,
                                      correct_option_id=index).poll
            self.current_question = Question(member,
                                             supported_question_attribute,
                                             poll=poll,
                                             multiple_choice=multiple_choice)
        else:
            if Orchestra.DICTS_TO_ATTRS[hint_attribute] == Question.PHOTO:
                self.bot.send_photo(chat_id=self.member.user_id,
                                    photo=member.photo_file_id,
                                    caption=question)
            else:
                self.bot.send_message(chat_id=self.member.user_id, text=question)
            self.current_question = Question(member,
                                             supported_question_attribute,
                                             multiple_choice=multiple_choice)

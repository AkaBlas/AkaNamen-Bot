#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the GameConfigurationUpdate class."""
from .question import Question

from types import SimpleNamespace
from typing import List


class GameConfigurationUpdate(SimpleNamespace):
    """
    Enqueue an instance of this class during the :attr:`components.GameHandler.CONFIGURING` state
    to go to the :attr:`components.GameHandler.GUESSING` state.

    Attributes:
        chat_id (:obj:`int`): The chat ID this update is created for.
        multiple_choice (:obj:`bool`): Whether the game is to be a multiple choice components.
        question_attributes (List[:obj:`str`]): A list of attributes that are to be asked.
        hint_attributes (List[:obj:`str`]): A list of attributes that may be given as hint.
        number_of_questions (:obj:`int`): How many questions are to be asked.

    Args:
        chat_id: The chat ID this update is created for.
        multiple_choice: Whether the game is to be a multiple choice components. Defaults to
            :obj:`True`.
        question_attributes: A list of attributes that are to be asked. See
            :attr:`Question.SUPPORTED_ATTRIBUTES`. Pass an empty list to allow any attribute.
        hint_attributes: A list of attributes that may be given as hint. See
            :attr:`Question.SUPPORTED_ATTRIBUTES`. Pass an empty list to allow any attribute.
        number_of_questions: How many questions are to be asked.
    """

    def __init__(self, chat_id: int, multiple_choice: bool, question_attributes: List[str],
                 hint_attributes: List[str], number_of_questions: int) -> None:
        super().__init__()

        if len(question_attributes) == 1 and len(hint_attributes) == 1:
            if question_attributes == hint_attributes:
                raise ValueError('Allowing only the same attribute for question and hint '
                                 'won\'t make much of an interesting game.')

        if any([x not in Question.SUPPORTED_ATTRIBUTES for x in question_attributes]):
            raise ValueError('Unsupported attributes in question_attributes!')

        if any([x not in Question.SUPPORTED_ATTRIBUTES for x in hint_attributes]):
            raise ValueError('Unsupported attributes in hint_attributes!')

        if (Question.ADDRESS in question_attributes and not multiple_choice
                and Question.FULL_NAME not in hint_attributes):
            raise ValueError('Asking for addresses as free text is only supported for full name '
                             'hints.')

        self.chat_id = chat_id
        self.multiple_choice = multiple_choice
        self.question_attributes = question_attributes or Question.SUPPORTED_ATTRIBUTES
        self.hint_attributes = hint_attributes or Question.SUPPORTED_ATTRIBUTES
        self.number_of_questions = number_of_questions

    def __dir__(self) -> List[str]:
        # Gives a list of the attributes of this object
        # This is the main reason, we inherit from SimpleNamespace
        return list(self.__dict__.keys())

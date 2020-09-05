#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Question class."""
from components import MessageType, UpdateType

from telegram import Poll, Update

from typing import TYPE_CHECKING, Union, List

if TYPE_CHECKING:
    from components import Member  # noqa: F401


class Question:
    """
    Representation of a single question asked in an AkaNamen Bot components.

    Attributes:
        member (:class:`components.Member`): The member, who's attribute is the correct answer.
        attribute (:obj:`str`): The attribute that is asked for.
        multiple_choice (:obj:`bool`): If :obj:`False`, the question is to be answered with
            "free text" instead of choosing an option from a poll.
        poll (:class:`telegram.Poll`): The poll sent to the user/chat.

    Args:
        member: The member, whose attribute is the correct answer.
        attribute: The attribute that is asked for. Must be one of :attr:`SUPPORTED_ATTRIBUTES`.
        multiple_choice: If :obj:`False`, the question is to be answered with "free text" instead
            of choosing an option from a poll. Defaults to :obj:`True`.
        poll: The poll sent to the user/chat. Pass this if and only if :attr:`multiple_choice` is
         :obj:`True` .
    """

    def __init__(self,
                 member: 'Member',
                 attribute: str,
                 multiple_choice: bool = True,
                 poll: Poll = None) -> None:
        if attribute not in self.SUPPORTED_ATTRIBUTES:
            raise ValueError('Attribute not supported.')

        if multiple_choice ^ bool(poll):
            raise ValueError('Pass a poll if and only if multiple_choice is True.')
        elif multiple_choice:
            if poll is None or poll.correct_option_id is None:
                raise ValueError('The poll must be a quiz poll with an correct_option_id.')

        if attribute == self.PHOTO and not multiple_choice:
            raise ValueError('Photos are supported only as multiple choice.')

        if bool(member[attribute]) is False:
            raise ValueError("The member doesn't have the required attribute.")

        self.member: 'Member' = member
        self.attribute: str = attribute
        self.multiple_choice: bool = multiple_choice
        self.poll = poll

    def check_update(self, update: Update) -> bool:
        """
        Checks, if th given update is a valid response to this question and can be handled by
        :meth:`check_answer`.

        Args:
            update: The :class:`telegram.Update` to be tested.
        """
        if self.multiple_choice:
            return (UpdateType.relevant_type(update) == UpdateType.POLL_ANSWER
                    and update.poll_answer.poll_id == self.poll.id)  # type: ignore
        else:
            if self.attribute in [
                    self.FIRST_NAME, self.LAST_NAME, self.NICKNAME, self.BIRTHDAY, self.AGE,
                    self.INSTRUMENT, self.FULL_NAME
            ]:
                return MessageType.relevant_type(update) == MessageType.TEXT
            # self.attribute == self.ADDRESS:
            else:
                return MessageType.relevant_type(update) in [
                    MessageType.TEXT, MessageType.LOCATION
                ]

    @property
    def correct_answer(self) -> Union[str, List[str]]:
        """The correct answer for this question."""
        if self.multiple_choice and self.poll:
            return self.poll.options[self.poll.correct_option_id]
        else:
            attribute = self.member[self.attribute]
            if isinstance(attribute, list):
                return ', '.join(str(a) for a in attribute)
            return str(attribute)

    def check_answer(self, update: Update) -> bool:
        """
        Checks, if the given answer is correct.

        Args:
            update: The :class:`telegram.Update`.
        """
        if self.multiple_choice:
            poll_answer = update.poll_answer

            return poll_answer.option_ids[0] == self.poll.correct_option_id  # type: ignore
        else:
            if update.message and update.message.text:
                answer = update.message.text.strip(' ').strip('\n')
            else:
                answer = None

            if self.attribute in [self.FIRST_NAME, self.LAST_NAME, self.NICKNAME, self.FULL_NAME]:
                accuracy = getattr(self.member, f'compare_{self.attribute}_to')(answer)
                return accuracy >= 0.85
            elif self.attribute == self.BIRTHDAY:
                bd_string = self.member.birthday.replace('0', '').replace('.', '')  # type: ignore
                answer = answer.replace('.', '').replace(',', '').replace(';', '')
                answer = answer.replace('0', '').replace(' ', '')
                return answer == bd_string
            elif self.attribute == self.AGE:
                return answer == str(self.member.age)
            elif self.attribute == self.INSTRUMENT:
                return self.member.compare_instruments_to(answer) >= 0.85
            # self.attribute == self.ADDRESS:
            else:
                if answer:
                    return self.member.compare_address_to(answer) >= 0.85
                else:
                    location = update.message.location
                    return self.member.distance_of_address_to(
                        (location.latitude, location.longitude)) <= 0.2

    FIRST_NAME: str = 'first_name'
    """:obj:`str`: First name of an AkaBlas member"""
    LAST_NAME: str = 'last_name'
    """:obj:`str`: Last name of an AkaBlas member"""
    NICKNAME: str = 'nickname'
    """:obj:`str`: Nickname of an AkaBlas member"""
    FULL_NAME: str = 'full_name'
    """:obj:`str`: Full name of an AkaBlas member"""
    BIRTHDAY: str = 'birthday'
    """:obj:`str`: Birthday of an AkaBlas member"""
    AGE: str = 'age'
    """:obj:`str`: Age of an AkaBlas member"""
    INSTRUMENT: str = 'instruments'
    """:obj:`str`: Instrument of an AkaBlas member"""
    ADDRESS: str = 'address'
    """:obj:`str`: Instrument of an AkaBlas member"""
    PHOTO: str = 'photo_file_id'
    """:obj:`str`: Photo of an AkaBlas member"""
    SUPPORTED_ATTRIBUTES = [
        FIRST_NAME, LAST_NAME, NICKNAME, BIRTHDAY, AGE, INSTRUMENT, ADDRESS, FULL_NAME, PHOTO
    ]
    """List[:obj:`str`]: Attributes usable for questions"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Question class."""
from fuzzywuzzy import fuzz

from telegram import Poll, Update

from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from akablas import Member  # noqa: F401


class Question:
    """
    Representation of a single question asked in an AkaNamen Bot game.

    Attributes:
        member (:class:`akablas.Member`): The member, whos attribute is the correct answer.
        attribute (:obj:`str`): The attribute that is asked for.
        multiple_choice (:obj:`bool`): If :obj:`False`, the question is to be answered with
            "free text" instead of choosing an option from a poll.
        poll (:class:`telegram.Poll`): The poll sent to the user/chat.

    Args:
        member: The member, whos attribute is the correct answer.
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
                 poll: Optional[Poll] = None) -> None:
        if multiple_choice ^ bool(poll):
            raise ValueError('Pass a poll if and only if multiple_choice is True.')
        elif multiple_choice:
            if poll is None or poll.correct_option_id is None:
                raise ValueError('The poll must be a quiz poll with an correct_option_id.')

        if attribute not in self.SUPPORTED_ATTRIBUTES:
            raise ValueError('Attribute not supported.')

        raise_error = False
        if attribute in [self.FIRST_NAME, self.LAST_NAME, self.NICKNAME]:
            raise_error = getattr(member, attribute) is None
        elif attribute in [self.BIRTHDAY, self.AGE]:
            raise_error = member.date_of_birth is None
        elif attribute == self.INSTRUMENT:
            raise_error = member.instruments is []
        elif attribute == self.ADDRESS:
            raise_error = member.address is None
        if raise_error:
            raise ValueError('The member doesn\'t have the required attribute.')

        self.member = member
        self.attribute = attribute
        self.multiple_choice = multiple_choice
        self.poll = poll

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

            if self.attribute in [self.FIRST_NAME, self.LAST_NAME, self.NICKNAME]:
                accuracy = getattr(self.member, f'compare_{self.attribute}_to')(answer)
                return accuracy >= 0.85
            elif self.attribute == self.BIRTHDAY:
                bd_string = self.member.date_of_birth.strftime('%d.%m.')  # type: ignore
                return max(fuzz.ratio(bd_string, answer),
                           fuzz.partial_ratio(bd_string, answer)) >= 85
            elif self.attribute == self.AGE:
                return answer == str(self.member.age)
            elif self.attribute == self.INSTRUMENT:
                return answer in self.member.instruments
            else:  # self.attribute == self.ADDRESS:
                if answer:
                    return self.member.compare_address_to(answer) >= 0.85
                else:
                    location = update.message.location
                    return self.member.distance_of_address_to((location.latitude,
                                                               location.longitude)) <= 0.2

    FIRST_NAME: str = 'first_name'
    """:obj:`str`: First name of an AkaBlas member"""
    LAST_NAME: str = 'last_name'
    """:obj:`str`: Last name of an AkaBlas member"""
    NICKNAME: str = 'nickname'
    """:obj:`str`: Nickname of an AkaBlas member"""
    BIRTHDAY: str = 'birthday'
    """:obj:`str`: Birthday of an AkaBlas member"""
    AGE: str = 'age'
    """:obj:`str`: Age of an AkaBlas member"""
    INSTRUMENT: str = 'instrument'
    """:obj:`str`: Instrument of an AkaBlas member"""
    ADDRESS: str = 'address'
    """:obj:`str`: Instrument of an AkaBlas member"""
    SUPPORTED_ATTRIBUTES = [FIRST_NAME, LAST_NAME, NICKNAME, BIRTHDAY, AGE, INSTRUMENT, ADDRESS]
    """List[:obj:`str`]: Attributes usable for questions"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Orchestra class."""
from akablas import Member, Instrument
from utils import PicklableBase
from game import Score

import datetime as dt

from threading import Lock
from typing import Set, Dict, List, Optional
from collections import defaultdict
from copy import copy

StrMemberDict = Dict[str, Set[Member]]
IntMemberDict = Dict[int, Set[Member]]
DateMemberDict = Dict[dt.date, Set[Member]]
InstrMemberDict = Dict[dt.date, Set[Instrument]]


class Orchestra(PicklableBase):
    """
    An orchestra. Keeps tracks of its members.
    """

    def __init__(self) -> None:
        self._members: Dict[int, Member] = dict()
        self._first_names: StrMemberDict = defaultdict(set)
        self._last_names: StrMemberDict = defaultdict(set)
        self._nicknames: StrMemberDict = defaultdict(set)
        self._genders: StrMemberDict = defaultdict(set)
        self._dates_of_birth: DateMemberDict = defaultdict(set)
        self._instruments: InstrMemberDict = defaultdict(set)
        self._addresses: StrMemberDict = defaultdict(set)

        self._ages_cache_date: Optional[dt.date] = None
        self._ages: IntMemberDict = defaultdict(set)

        self._members_lock: Lock = Lock()
        self._first_names_lock: Lock = Lock()
        self._last_names_lock: Lock = Lock()
        self._nicknames_lock: Lock = Lock()
        self._genders_lock: Lock = Lock()
        self._dates_of_birth_lock: Lock = Lock()
        self._instruments_lock: Lock = Lock()
        self._addresses_lock: Lock = Lock()
        self._ages_lock: Lock = Lock()

        self.lists_to_attrs: Dict[str, str] = {
            'first_names': 'first_name',
            'last_names': 'last_name',
            'nicknames': 'nickname',
            'genders': 'gender',
            'dates_of_birth': 'date_of_birth',
            'instruments': 'instruments',
            'addresses': 'address',
            'ages': 'age',
        }

    @property
    def members(self) -> Dict[int, Member]:
        """
        All the members of the orchestra. The keys are the :attr:`akablas.Member.user_id` s, the
        values are the actual members.
        """
        with self._members_lock:
            return self._members

    @members.setter
    def members(self, value: Set[Member]) -> None:
        raise ValueError('This attribute can\'t be overridden!')

    @property
    def first_names(self) -> StrMemberDict:
        """
        A :class:`collections.defaultdict`. For each key, all members with the corresponding first
        name are the values.
        """
        with self._first_names_lock:
            return self._first_names

    @first_names.setter
    def first_names(self, value: StrMemberDict) -> None:
        raise ValueError('This attribute can\'t be overridden!')

    @property
    def last_names(self) -> StrMemberDict:
        """
        A :class:`collections.defaultdict`. For each key, all members with the corresponding last
        name are the values.
        """
        with self._last_names_lock:
            return self._last_names

    @last_names.setter
    def last_names(self, value: StrMemberDict) -> None:
        raise ValueError('This attribute can\'t be overridden!')

    @property
    def nicknames(self) -> StrMemberDict:
        """
        A :class:`collections.defaultdict`. For each key, all members with the corresponding
        nickname are the values.
        """
        with self._nicknames_lock:
            return self._nicknames

    @nicknames.setter
    def nicknames(self, value: StrMemberDict) -> None:
        raise ValueError('This attribute can\'t be overridden!')

    @property
    def genders(self) -> StrMemberDict:
        """
        A :class:`collections.defaultdict`. For each key, all members with the corresponding
        gender are the values.
        """
        with self._genders_lock:
            return self._genders

    @genders.setter
    def genders(self, value: StrMemberDict) -> None:
        raise ValueError('This attribute can\'t be overridden!')

    @property
    def dates_of_birth(self) -> DateMemberDict:
        """
        A :class:`collections.defaultdict`. For each key, all members with the corresponding
        date of birth are the values. The keys are :class:`datetime.date` objects.
        """
        with self._dates_of_birth_lock:
            return self._dates_of_birth

    @dates_of_birth.setter
    def dates_of_birth(self, value: DateMemberDict) -> None:
        raise ValueError('This attribute can\'t be overridden!')

    @property
    def instruments(self) -> InstrMemberDict:
        """
        A :class:`collections.defaultdict`. For each key, all members that play the corresponding
        instrument the values. The keys are :class:`akablas.Instrument` objects.
        """
        with self._instruments_lock:
            return self._instruments

    @instruments.setter
    def instruments(self, value: InstrMemberDict) -> None:
        raise ValueError('This attribute can\'t be overridden!')

    @property
    def addresses(self) -> StrMemberDict:
        """
        A :class:`collections.defaultdict`. For each key, all members with the corresponding
        address are the values.
        """
        with self._addresses_lock:
            return self._addresses

    @addresses.setter
    def addresses(self, value: StrMemberDict) -> None:
        raise ValueError('This attribute can\'t be overridden!')

    @property
    def ages(self) -> IntMemberDict:
        """
        A :class:`collections.defaultdict`. For each key, all members with the corresponding
        age (on evaluation time) are the values.
        """
        with self._ages_lock:
            today = dt.date.today()
            # Compute age only once a day
            if not self._ages_cache_date or (today - self._ages_cache_date).days > 0:
                self._ages = defaultdict(set)
                for m in self.members.values():
                    if m.age:
                        self._ages[m.age].add(m)
                self._ages_cache_date = today
            return self._ages

    @ages.setter
    def ages(self, value: InstrMemberDict) -> None:
        raise ValueError('This attribute can\'t be overridden!')

    def register_member(self, member: Member) -> None:
        """
        Registers a new member for this orchestra.

        Note:
            Copies the member so changes to the instance wont directly affect the orchestra.
            Use :meth:`update_member` to update the information about this member.

        Args:
            member: The new member

        Raises:
            ValueError: If member is already registered.
        """
        if member.user_id in self.members:
            raise ValueError('This member is already registered.')

        new_member = copy(member)
        self.members[new_member.user_id] = new_member
        for list_name, attr in self.lists_to_attrs.items():
            attribute = getattr(new_member, attr)
            if attribute is not None:
                list_ = getattr(self, list_name)
                if isinstance(attribute, list):
                    for e in attribute:
                        list_[e].add(new_member)
                else:
                    list_[attribute].add(new_member)

    def kick_member(self, member: Member) -> None:
        """
        Kicks a member from the orchestra.

        Args:
            member: The member to kick.

        Raises:
            ValueError: If member is not registered.
        """
        if member.user_id not in self.members:
            raise ValueError('This member is not registered.')

        old_member = self.members[member.user_id]
        del self.members[member.user_id]

        for list_name, attr in self.lists_to_attrs.items():
            attribute = getattr(old_member, attr)
            list_ = getattr(self, list_name)
            if isinstance(attribute, list):
                for e in attribute:
                    list_[e].discard(old_member)
            else:
                list_[attribute].discard(old_member)

    def update_member(self, member: Member) -> None:
        """
        Updates the information of a member. As :meth:`register_user`, this will copy the
        member. To update the information again, call this method again.

        Args:
            member: The member with new information.
        """
        self.kick_member(member)
        self.register_member(member)

    def _score(self, attr: str) -> List[Score]:
        if attr == 'overall':
            attr = f'overall_score'
        else:
            attr = f'{attr}s_score'

        return sorted([getattr(m.user_score, attr) for m in self.members.values()], reverse=True)

    def _score_text(self,
                    attr: str,
                    length: Optional[int] = None,
                    html: Optional[bool] = False) -> str:
        sorted_scores = self._score(attr)

        text = ''
        lines = length or len(sorted_scores)
        left_offset = len(str(min(lines, length or lines))) + 2

        for i, score in enumerate(sorted_scores):
            if length is None or i < length:
                if score.member and score.member.full_name:
                    name = score.member.full_name
                else:
                    name = 'Anonym'

                if html:
                    name_line = (f'{i + 1:{left_offset - 2}}. <b>{name}:</b> '
                                 f'{score.correct} / {score.answers}')
                else:
                    name_line = (f'{i + 1:{left_offset - 2}}. {name}: '
                                 f'{score.correct} / {score.answers}')

                full_bars = int(score.ratio // 10)
                empty_bars = 10 - full_bars
                ratio_line = left_offset * ' ' + full_bars * '▬' + empty_bars * '▭'
                ratio_line += f'  {score.ratio:5.2f} %'

                if i > 0:
                    text += '\n'

                text += f'{name_line}\n{ratio_line}'

        return text

    @property
    def todays_score(self) -> List[Score]:
        """
        Gives a list of each members score of today sorted descending by :attr:`game.Score.ratio` .
        """
        return self._score('today')

    def todays_score_text(self, length: Optional[int] = None, html: Optional[bool] = False) -> str:
        """
        String representation of :attr:`todays_score`.

        Args:
            length: Maximum number of members to display. If not passed, will write down all
                members.
            html: If :obj:`True`, will embed HTML tags in the string. Use this to send the string
                with a Telegram bot using :attr:`telegram.ParseMode.HTML`.

        """
        return self._score_text('today', length=length, html=html)

    @property
    def weeks_score(self) -> List[Score]:
        """
        Gives a list of each members score of the current week sorted descending by
        :attr:`game.Score.ratio` .
        """
        return self._score('week')

    def weeks_score_text(self, length: Optional[int] = None, html: Optional[bool] = False) -> str:
        """
        String representation of :attr:`weeks_score`.

        Args:
            length: Maximum number of members to display. If not passed, will write down all
                members.
            html: If :obj:`True`, will embed HTML tags in the string. Use this to send the string
                with a Telegram bot using :attr:`telegram.ParseMode.HTML`.

        """
        return self._score_text('week', length=length, html=html)

    @property
    def months_score(self) -> List[Score]:
        """
        Gives a list of each members score of the current month sorted descending by
        :attr:`game.Score.ratio` .
        """
        return self._score('month')

    def months_score_text(self, length: Optional[int] = None, html: Optional[bool] = False) -> str:
        """
        String representation of :attr:`months_score`.

        Args:
            length: Maximum number of members to display. If not passed, will write down all
                members.
            html: If :obj:`True`, will embed HTML tags in the string. Use this to send the string
                with a Telegram bot using :attr:`telegram.ParseMode.HTML`.

        """
        return self._score_text('month', length=length, html=html)

    @property
    def years_score(self) -> List[Score]:
        """
        Gives a list of each members score of the current year sorted descending by
        :attr:`game.Score.ratio` .
        """
        return self._score('year')

    def years_score_text(self, length: Optional[int] = None, html: Optional[bool] = False) -> str:
        """
        String representation of :attr:`years_score`.

        Args:
            length: Maximum number of members to display. If not passed, will write down all
                members.
            html: If :obj:`True`, will embed HTML tags in the string. Use this to send the string
                with a Telegram bot using :attr:`telegram.ParseMode.HTML`.

        """
        return self._score_text('year', length=length, html=html)

    @property
    def overall_score(self) -> List[Score]:
        """
        Gives a list of each members overall score sorted descending by :attr:`game.Score.ratio` .
        """
        return self._score('overall')

    def overall_score_text(self,
                           length: Optional[int] = None,
                           html: Optional[bool] = False) -> str:
        """
        String representation of :attr:`overall_score`.

        Args:
            length: Maximum number of members to display. If not passed, will write down all
                members.
            html: If :obj:`True`, will embed HTML tags in the string. Use this to send the string
                with a Telegram bot using :attr:`telegram.ParseMode.HTML`.

        """
        return self._score_text('overall', length=length, html=html)

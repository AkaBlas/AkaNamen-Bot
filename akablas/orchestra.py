#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Orchestra class."""
from akablas import Member, Instrument

import datetime as dt

from threading import Lock
from typing import Set, Dict, Any, Union
from collections import defaultdict
from copy import copy

StrMemberDict = Dict[str, Set[Member]]
DateMemberDict = Dict[dt.date, Set[Member]]
InstrMemberDict = Dict[dt.date, Set[Instrument]]


class Orchestra:
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

        self._members_lock: Lock = Lock()
        self._first_names_lock: Lock = Lock()
        self._last_names_lock: Lock = Lock()
        self._nicknames_lock: Lock = Lock()
        self._genders_lock: Lock = Lock()
        self._dates_of_birth_lock: Lock = Lock()
        self._instruments_lock: Lock = Lock()
        self._addresses_lock: Lock = Lock()

        self.lists_to_attrs: Dict[str, str] = {
            'first_names': 'first_name',
            'last_names': 'last_name',
            'nicknames': 'nickname',
            'genders': 'gender',
            'dates_of_birth': 'date_of_birth',
            'instruments': 'instruments',
            'addresses': 'address'
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
                list_: Dict[Union[str, dt.date, Instrument],
                            Set[Member]] = getattr(self, list_name)
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
            list_: Dict[Union[str, dt.date, Instrument], Set[Member]] = getattr(self, list_name)
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

    # Make sure that pickling works
    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        for key in [k for k in state if k.endswith('_lock')]:
            state[key] = None
        return state

    def __setstate__(self, state: Dict[str, Any]):
        for key in [k for k in state if k.endswith('_lock')]:
            state[key] = Lock()
        self.__dict__.update(state)

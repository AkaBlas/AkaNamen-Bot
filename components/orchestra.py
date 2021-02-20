#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Orchestra class."""
from copy import deepcopy
from threading import Lock

from typing import Dict, List, Optional, Tuple, Any, Set, Iterable, NoReturn

from components import (
    Member,
    PicklableBase,
    Score,
    AttributeManager,
    ChangingAttributeManager,
    NameManager,
    PhotoManager,
)


class Orchestra(PicklableBase):
    """
    An orchestra. Keeps tracks of its members.

    Note:
        Orchestra instance support subscription for all attribute managers listed as keys of
        :attr:`SUBSCRIPTABLE`.

    Attributes:
        attribute_managers (Dict[:obj:`str`, :class:`components.AttributeManager`]): A dictionary
            of attribute managers keeping track of the members
    """

    def __init__(self) -> None:
        self._members: Dict[int, Member] = dict()
        self._members_lock = Lock()
        self.attribute_managers: Dict[str, AttributeManager] = {
            'address': AttributeManager(
                'address', list(self.ATTRIBUTE_MANAGERS.difference(['address']))
            ),
            'age': ChangingAttributeManager(
                'age', list(self.ATTRIBUTE_MANAGERS.difference(['age', 'birthday']))
            ),
            'birthday': AttributeManager(
                'birthday', list(self.ATTRIBUTE_MANAGERS.difference(['birthday', 'age']))
            ),
            'first_name': NameManager(
                'first_name', list(self.ATTRIBUTE_MANAGERS.difference(['first_name', 'full_name']))
            ),
            'full_name': NameManager(
                'full_name',
                list(
                    self.ATTRIBUTE_MANAGERS.difference(
                        ['full_name', 'first_name', 'last_name', 'nickname']
                    )
                ),
            ),
            'instruments': AttributeManager(
                'instruments', list(self.ATTRIBUTE_MANAGERS.difference(['instruments']))
            ),
            'last_name': AttributeManager(
                'last_name', list(self.ATTRIBUTE_MANAGERS.difference(['last_name', 'full_name']))
            ),
            'nickname': AttributeManager(
                'nickname', list(self.ATTRIBUTE_MANAGERS.difference(['nickname', 'full_name']))
            ),
            'photo_file_id': PhotoManager(
                'photo_file_id', list(self.ATTRIBUTE_MANAGERS.difference(['photo_file_id']))
            ),
            'joined': AttributeManager(
                'joined', list(self.ATTRIBUTE_MANAGERS.difference(['joined', 'age', 'birthday']))
            ),
            'functions': AttributeManager(
                'functions',
                list(
                    self.ATTRIBUTE_MANAGERS.difference(['functions', 'age', 'birthday', 'joined'])
                ),
            ),
        }

    def __getitem__(self, item: str) -> Any:
        if item not in self.SUBSCRIPTABLE:
            raise KeyError(
                'Orchestra either does not have such an attribute or does not support '
                'subscription for it.'
            )
        if item == 'addresses':
            item = 'address'
        elif item not in ['instruments', 'address', 'functions']:
            item = item.rstrip('s')
        return self.attribute_managers[item]

    @property
    def members(self) -> Dict[int, Member]:
        """
        All the members of the orchestra. The keys are the :attr:`components.Member.user_id` s, the
        values are the actual members.
        """
        with self._members_lock:
            return self._members

    @members.setter
    def members(self, value: Set[Member]) -> NoReturn:  # pylint: disable=R0201
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

        self.members[member.user_id] = deepcopy(member)
        for a_m in self.attribute_managers.values():
            a_m.register_member(member)

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

        self.members.pop(member.user_id)
        for a_m in self.attribute_managers.values():
            a_m.kick_member(member)

    def update_member(self, member: Member) -> None:
        """
        Updates the information of a member. As :meth:`register_user`, this will copy the
        member. To update the information again, call this method again.

        Args:
            member: The member with new information.
        """
        self.kick_member(member)
        self.register_member(member)

    def questionable(
        self,
        multiple_choice: bool = True,
        exclude_members: Iterable[Member] = None,
    ) -> List[Tuple[AttributeManager, AttributeManager]]:
        """
        Gives a list of tuples of :class:`components.AttributeManager` instances, each representing
        a pair of hint attribute and question attribute, which have enough different values for the
        orchestras members to generate questions from it.

        Args:
            multiple_choice: Optional. Whether the questions will be multiple choice or free text.
                Defaults to :obj:`True`.
            exclude_members: Optional. Members to exclude from serving as hint.
        """
        out = []
        for a_m in self.attribute_managers.values():
            for b_m in self.attribute_managers.values():
                if b_m.description == 'photo_file_id':
                    if a_m.is_hintable_with(
                        b_m, multiple_choice=True, exclude_members=exclude_members
                    ):
                        out.append((a_m, b_m))
                elif a_m.is_hintable_with(
                    b_m, multiple_choice=multiple_choice, exclude_members=exclude_members
                ):
                    out.append((a_m, b_m))
        return out

    def _score(self, attr: str) -> List[Score]:
        if attr == 'overall':
            attr = 'overall_score'
        else:
            attr = f'{attr}s_score'

        scores = {
            member: getattr(member.user_score, attr)
            for member in self.members.values()
            if getattr(member.user_score, attr).answers > 0
        }
        membered_scores = []
        for member, score in scores.items():
            score.member = member
            membered_scores.append(score)
        return []

    def _score_text(self, attr: str, length: int = None, html: Optional[bool] = False) -> str:
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
                    name_line = (
                        f'{i + 1:{left_offset - 2}}. <b>{name}:</b> '
                        f'{score.correct} / {score.answers}'
                    )
                else:
                    name_line = (
                        f'{i + 1:{left_offset - 2}}. {name}: ' f'{score.correct} / {score.answers}'
                    )

                full_bars = int(score.ratio // 10)
                empty_bars = 10 - full_bars
                ratio_line = left_offset * ' ' + full_bars * '▬' + empty_bars * '▭'
                ratio_line += f'  {score.ratio:5.2f} %'

                if i > 0:
                    text += '\n'

                text += f'{name_line}\n{ratio_line}'

        if not text:
            text = (
                'Noch keine Einträge vorhanden. Schnell ein /spiel_starten, dann bist Du auf '
                'Platz 1! 😎 '
            )

        return text

    @property
    def todays_score(self) -> List[Score]:
        """
        Gives a list of each members score of today sorted descending by
        :attr:`components.Score.ratio` .
        """
        return self._score('today')

    def todays_score_text(self, length: int = None, html: Optional[bool] = False) -> str:
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
        :attr:`components.Score.ratio` .
        """
        return self._score('week')

    def weeks_score_text(self, length: int = None, html: Optional[bool] = False) -> str:
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
        :attr:`components.Score.ratio` .
        """
        return self._score('month')

    def months_score_text(self, length: int = None, html: Optional[bool] = False) -> str:
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
        :attr:`components.Score.ratio` .
        """
        return self._score('year')

    def years_score_text(self, length: int = None, html: Optional[bool] = False) -> str:
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
        Gives a list of each members overall score sorted descending by
        :attr:`components.Score.ratio` .
        """
        return self._score('overall')

    def overall_score_text(self, length: int = None, html: Optional[bool] = False) -> str:
        """
        String representation of :attr:`overall_score`.

        Args:
            length: Maximum number of members to display. If not passed, will write down all
                members.
            html: If :obj:`True`, will embed HTML tags in the string. Use this to send the string
                with a Telegram bot using :attr:`telegram.ParseMode.HTML`.

        """
        return self._score_text('overall', length=length, html=html)

    def copy(self) -> 'Orchestra':
        """
        Returns a (deep) copy of this orchestra.
        """
        new_orchestra = self.__class__()

        for member in self.members.values():
            new_orchestra.register_member(member.copy())

        return new_orchestra

    def __eq__(self, other: object) -> bool:
        return False

    TO_HR: Dict[str, str] = {
        'first_names': 'Vorname',
        'first_name': 'Vorname',
        'last_names': 'Nachname',
        'last_name': 'Nachname',
        'full_names': 'Ganzer Name',
        'full_name': 'Ganzer Name',
        'nicknames': 'Spitzname',
        'nickname': 'Spitzname',
        'instruments': 'Instrument',
        'addresses': 'Adresse',
        'address': 'Adresse',
        'ages': 'Alter',
        'age': 'Alter',
        'joined': 'Beitrittsjahr',
        'functions': 'Ämter',
        'birthdays': 'Geburtstag',
        'birthday': 'Geburtstag',
        'photo_file_ids': 'Foto',
        'photo_file_id': 'Foto',
    }
    """Dict[:obj:`str`, :obj:`str`]: A map from the names of the different properties of this
    class to the human readable strings."""

    SUBSCRIPTABLE = [
        'address',
        'addresses',
        'age',
        'ages',
        'birthday',
        'birthdays',
        'first_name',
        'first_names',
        'full_name',
        'full_names',
        'instruments',
        'last_name',
        'last_names',
        'nickname',
        'nicknames',
        'photo_file_id',
        'photo_file_ids',
        'joined',
        'functions',
    ]
    """List[:obj:`str`]: Attribute managers supported by subscription."""
    ATTRIBUTE_MANAGERS = {
        'address',
        'age',
        'birthday',
        'first_name',
        'full_name',
        'instruments',
        'last_name',
        'nickname',
        'photo_file_id',
        'joined',
        'functions',
    }

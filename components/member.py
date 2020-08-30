#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Member class."""
from __future__ import annotations

from components import Instrument
from components.helpers import setlocale
from .userscore import UserScore

import datetime as dt
import numpy as np
import pandas as pd
import vobject
import requests
import shutil
import re

from geopy import Photon, distance
from geopy.exc import GeopyError
from tempfile import TemporaryFile, NamedTemporaryFile
from configparser import ConfigParser
from collections import defaultdict
from camelot import read_pdf
from typing import Optional, Union, List, Tuple, IO, Dict, Any

from fuzzywuzzy import fuzz
from telegram import Bot, User


class Member:
    """
    A member of AkaBlas.

    Note:
        Orchestra instance support subscription for all properties and attributes listed in
        :attr:`SUBSCRIPTABLE`.

    Attributes:
        user_id (:obj:`int`): The Telegram user_id.
        phone_number (:obj:`str`): Optional. Phone number.
        first_name (:obj:`str`): Optional. First name.
        last_name (:obj:`str`): Optional. Last name.
        nickname (:obj:`str`): Optional. Nickname.
        gender (:obj:`str`): Optional. Gender.
        date_of_birth (:class:`datetime.date`): Optional. : Date of birth.
        photo_file_id (:obj:`str`): Optional. Telegram file ID of the user photo
        allow_contact_sharing (:obj:`bool`): Whether sharing this members contact information with
            others is allowed.
        user_score (:class:`components.UserScore`): A highscore associated with this member.

    Args:
        user_id: The Telegram user_id.
        phone_number: Phone number.
        first_name: First name.
        last_name: Last name.
        nickname: Nickname.
        gender: Gender.
        date_of_birth: Date of birth.
        instruments: Instrument(s) this member plays.
        address: Address. Only address `or`` latitude and longitude may be passed.
        latitude: Latitude of address. Only address `or`` latitude and longitude may
            be passed.
        longitude: Longitude of address. Only address `or`` latitude and longitude may
            be passed.
        photo_file_id: Telegram file ID of the user photo
        allow_contact_sharing: Whether sharing this users contact information with others is
            allowed. Defaults to :obj:`False`.
    """

    def __init__(self,
                 user_id: Union[str, int],
                 phone_number: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 nickname: str = None,
                 gender: str = None,
                 date_of_birth: dt.date = None,
                 instruments: Union[List[Instrument], Instrument] = None,
                 address: str = None,
                 latitude: float = None,
                 longitude: float = None,
                 photo_file_id: str = None,
                 allow_contact_sharing: Optional[bool] = False) -> None:
        if sum([x is not None for x in [longitude, latitude]]) == 1:
            raise ValueError('Either none of longitude and latitude or both must be passed!')
        if longitude and address:
            raise ValueError('Only address or longitude and latitude may be passed!')

        self.user_id: int = int(user_id)
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.photo_file_id = photo_file_id
        self.allow_contact_sharing = allow_contact_sharing
        self.user_score = UserScore(self)

        # See https://github.com/python/mypy/issues/3004
        self.instruments = instruments  # type: ignore

        self._geo_locator: Photon = Photon(timeout=5)
        self._address: Optional[str] = None
        self._longitude: Optional[float] = None
        self._latitude: Optional[float] = None
        self._raw_address: Optional[dict] = None
        if address:
            self.set_address(address=address)
        if longitude and latitude:
            self.set_address(coordinates=(latitude, longitude))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Member):
            return self.user_id == other.user_id
        return False

    def __hash__(self) -> int:
        return self.user_id

    def __getitem__(self, item: str) -> Union[str, dt.date, int, List[Instrument], None, float]:
        if item not in self.SUBSCRIPTABLE:
            raise KeyError('Member either does not have such an attribute or does not support '
                           'subscription for it.')
        return getattr(self, item)

    def __setitem__(self, item: str, value: Any) -> None:
        if item not in self.SUBSCRIPTABLE:
            raise KeyError('Member either does not have such an attribute or does not support '
                           'subscription for it.')
        return setattr(self, item, value)

    def to_str(self) -> str:
        with setlocale('de_DE.UTF-8'):
            return (f'Name: {self.full_name or "-"}\n'
                    f'Geschlecht: {self.gender if self.gender else "-"}\n'
                    f'Geburtstag: '
                    f'{self.date_of_birth.strftime("%d. %B %Y") if self.date_of_birth else "-"}\n'
                    f'Instrument/e: {", ".join([str(i) for i in self.instruments]) or "-"}\n'
                    f'Adresse: {self.address or "-"}\n'
                    f'Mobil: {self.phone_number or "-"}\n'
                    f'Photo: {"🖼" if self.photo_file_id else "-"}\n'
                    f'Daten an AkaBlasen weitergeben: '
                    f'{"Aktiviert" if self.allow_contact_sharing else "Deaktiviert"}')

    def set_address(self,
                    address: str = None,
                    coordinates: Tuple[float, float] = None) -> Optional[str]:
        """
        Tries to get the missing data from the Open Street Map API. Exactly one of the optional
        parameters must be passed.

        Args:
            address: The address.
            coordinates: Coordinates as tuple of latitude and longitude.

        Returns:
            The found address.
        """
        if bool(address and coordinates) or not bool(address or coordinates):
            raise ValueError('Exactly one of the parameters must be passed!')
        try:
            if address:
                location = self._geo_locator.geocode(address)
            else:
                location = self._geo_locator.reverse(coordinates)
        except GeopyError:
            self._raw_address = None
            self._address = None
            self._longitude = None
            self._latitude = None

            return self._address

        if location:
            if 'properties' in location.raw:
                raw = location.raw['properties']
                if ('street' in raw and 'postcode' in raw and 'housenumber' in raw
                        and 'city' in raw and 'country' in raw):
                    raw['city'] = raw['city'].replace('Brunswick', 'Braunschweig')
                    self._address = (f"{raw['street']} {raw['housenumber']}, {raw['postcode']} "
                                     f"{raw['city']}")
                    if raw['country'] != 'Germany':
                        self._address += f" {raw['country']}"
                    self._raw_address = raw
                else:
                    self._address = location.address
            else:
                self._address = location.address

            self._latitude = location.latitude
            self._longitude = location.longitude
        else:
            self._raw_address = None
            self._address = None
            self._longitude = None
            self._latitude = None

        return self._address

    def clear_address(self) -> None:
        """
        Deletes the address of this member.
        """
        self._raw_address = None
        self._address = None
        self._longitude = None
        self._latitude = None

    @property
    def full_name(self) -> Optional[str]:
        """
        Full name of the member. May be :obj:`None`.
        """
        if not any([self.first_name, self.last_name, self.nickname]):
            return None
        elif self.first_name is None and self.last_name is None:
            return self.nickname
        nickname: Optional[str] = None
        if self.nickname is not None:
            nickname = f'"{self.nickname}"'
        return ' '.join([n for n in [self.first_name, nickname, self.last_name] if n is not None])

    @property
    def address(self) -> Optional[str]:
        """
        Address of the member.
        """
        return self._address

    @address.setter
    def address(self, value: str) -> None:
        raise ValueError('Please use set_address to update the address!')

    @property
    def latitude(self) -> Optional[float]:
        """
        Latitude of the members address.
        """
        return self._latitude

    @latitude.setter
    def latitude(self, value: float) -> None:
        raise ValueError('Please use set_address to update the latitude!')

    @property
    def longitude(self) -> Optional[float]:
        """
        Longitude of the members address.
        """
        return self._longitude

    @longitude.setter
    def longitude(self, value: float) -> None:
        raise ValueError('Please use set_address to update the longitude!')

    @property
    def instruments(self) -> List[Instrument]:
        """
        Instrument(s) this member plays. List may be empty
        """
        return self._instruments

    @instruments.setter
    def instruments(self, instruments: Optional[Union[List[Instrument], Instrument]]) -> None:
        if instruments is None:
            self._instruments = []
        elif isinstance(instruments, Instrument):
            self._instruments = [instruments]
        else:
            self._instruments = instruments

    @property
    def instruments_str(self) -> Optional[str]:
        """
        Stringified list of the instrument(s) the member plays. May be empty.
        """
        if self.instruments:
            return ', '.join(str(i) for i in self.instruments)
        return None

    @property
    def vcard_filename(self) -> str:
        """
        Gives a filename of the vcard generated by :attr:`vcard`.
        """
        return f'{self.full_name}.vcf'.replace(' ', '_').replace('"', '')

    def vcard(self, bot: Bot) -> IO:
        """
        Gives a vCard of the member.

        Args:
            bot: A Telegram bot to retrieve the members photo (if set). Must be the same bot that
                retrieved the file ID.

        Returns:
            The vCard as `open` file. Make sure to close it!

        Raises:
            ValueError: If sharing contact information is not allowed.
        """
        if not self.allow_contact_sharing:
            raise ValueError('This member does not allow sharing it\'s contact information.')

        with TemporaryFile() as photo_file:
            vcard = vobject.vCard()
            if self.full_name:
                vcard.add('fn').value = self.full_name.replace('"', '')
            else:
                vcard.add('fn').value = ''
            vcard.add('n').value = vobject.vcard.Name(family=self.last_name or '',
                                                      given=self.first_name or '')
            vcard.add('nickname').value = self.nickname or ''
            vcard.add('tel').value = self.phone_number or ''
            vcard.add('role').value = self.instruments_str or ''
            vcard.add('org').value = ['AkaBlas e.V.']

            if self.date_of_birth:
                vcard.add('bday').value = self.date_of_birth.strftime('%Y%m%d')

            if self._raw_address:
                vcard.add('adr').value = vobject.vcard.Address(
                    city=self._raw_address['city'],
                    code=self._raw_address['postcode'],
                    street=' '.join(
                        [self._raw_address['street'],
                         self._raw_address.get('housenumber', '')]))

            if self.photo_file_id:
                file = bot.get_file(self.photo_file_id)
                file.download(out=photo_file)
                photo_file.seek(0)
                photo = vcard.add('photo')
                photo.encoding_param = 'B'
                photo.type_param = 'JPG'
                photo.value = photo_file.read()

            vcard_file = TemporaryFile()
            vcard_file.write(vcard.serialize().encode('utf-8'))
            vcard_file.seek(0)
            return vcard_file

    @staticmethod
    def _compare(str1: str, str2: str) -> float:
        str_1 = str1.lower()
        str_2 = str2.lower()
        return max(fuzz.ratio(str_1, str_2), fuzz.partial_ratio(str_1, str_2)) / 100

    def compare_instruments_to(self, string: str) -> float:
        """
        Compares the members instruments to the given string. The comparison is case insensitive.

        Args:
            string: The string to compare to.

        Returns:
            Similarity in percentage.

        Raises:
            ValueError: If the member has no instruments.
        """
        if not self.instruments_str:
            raise ValueError('This member has no instruments.')
        return self._compare(self.instruments_str, string)

    def compare_first_name_to(self, string: str) -> float:
        """
        Compares the members first name to the given string. The comparison is case insensitive.

        Args:
            string: The string to compare to.

        Returns:
            Similarity in percentage.

        Raises:
            ValueError: If the member has no first name.
        """
        if self.first_name is None:
            raise ValueError('This member has no first name.')
        return self._compare(self.first_name, string)

    def compare_last_name_to(self, string: str) -> float:
        """
        Compares the members last name to the given string. The comparison is case insensitive.

        Args:
            string: The string to compare to.

        Returns:
            Similarity in percentage.

        Raises:
            ValueError: If the member has no last name.
        """
        if self.last_name is None:
            raise ValueError('This member has no last name.')
        return self._compare(self.last_name, string)

    def compare_nickname_to(self, string: str) -> float:
        """
        Compares the members nickname to the given string. The comparison is case insensitive.

        Args:
            string: The string to compare to.

        Returns:
            Similarity in percentage.

        Raises:
            ValueError: If the member has no nickname.
        """
        if self.nickname is None:
            raise ValueError('This member has no nickname.')
        return self._compare(self.nickname, string)

    def compare_full_name_to(self, string: str) -> float:
        """
        Compares the members full name to the given string. The comparison is case insensitive.

        Args:
            string: The string to compare to.

        Returns:
            Similarity in percentage.

        Raises:
            ValueError: If the member has no full name.
        """
        if self.full_name is None:
            raise ValueError('This member has no full name.')
        str_1 = self.full_name.lower().replace('"', '')
        str_2 = string.lower()
        return (fuzz.ratio(str_1, str_2) + fuzz.token_set_ratio(str_1, str_2)) / 200

    def compare_address_to(self, string: str) -> float:
        """
        Compares the members address to the given string. The comparison is case insensitive.

        Args:
            string: The string to compare to.

        Returns:
            Similarity in percentage.

        Raises:
            ValueError: If the member has no address.
        """
        if self.address is None:
            raise ValueError('This member has no address.')
        return max(self._compare(self.address.lower(), string.lower()),
                   fuzz.token_set_ratio(self.address.lower(), string.lower()) / 100)

    def distance_of_address_to(self, coordinates: Tuple[float, float]) -> float:
        """
        Computes the distance between the members address and the given coordinates.

        Args:
            coordinates: A tuple of latitude and longitude to compare to.

        Returns:
            The distance in kilometers.

        Raises:
            ValueError: If the member has no address.
        """
        if self.address is None:
            raise ValueError('This member has no address.')
        return distance.distance((self.latitude, self.longitude), coordinates).kilometers

    @property
    def age(self) -> Optional[int]:
        """
        The age of the member at evaluation time. :obj:`None`, if :attr:`date_of_birth` is not set.
        """
        if not self.date_of_birth:
            return None

        today = dt.date.today()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    @property
    def birthday(self) -> Optional[str]:
        """
        The birthday of the member int he format ``DD.MM.``. :obj:`None`, if :attr:`date_of_birth`
        is not set.
        """
        if not self.date_of_birth:
            return None

        return self.date_of_birth.strftime('%d.%m.')

    @staticmethod
    def _get_akadressen() -> pd.DataFrame:

        # A bunch of helpers to parse the downloaded data
        leading_whitespace_pattern = re.compile(r'\b(?=\w)(\w) (\w)')
        trailing_whitespace_pattern = re.compile(r'(\w) ([^0-9])\b(?<=\w)')

        def string_to_date(string: Union[str, np.nan]) -> Optional[dt.date]:
            if string is np.nan:
                return None
            with setlocale('de_DE.UTF-8'):
                string = string.replace('Mrz', dt.datetime(2020, 3, 1).strftime('%b'))
                try:
                    out = dt.datetime.strptime(string, '%d. %b. %y').date()
                except ValueError:
                    out = dt.datetime.strptime(string, '%d. %b. %Y').date()
            return out

        def string_to_instrument(string: str) -> Optional[Instrument]:
            try:
                return Instrument.from_string(string)
            except ValueError:
                return None

        def remove_whitespaces(string: str) -> str:
            string = re.sub(leading_whitespace_pattern, r'\g<1>\g<2>', string)
            return re.sub(trailing_whitespace_pattern, r'\g<1>\g<2>', string)

        def extract_nickname(string: str) -> Optional[str]:
            if '(' in string:
                return string.split('(')[0].strip(' ')
            else:
                return None

        def remove_nickname(string: str) -> str:
            if '(' in string:
                parts = string.split('(')
                string = ' '.join(parts[1:]).replace(')', '')
            return string

        def expand_brunswick(address: str) -> str:
            address = remove_whitespaces(address)
            return address.replace('BS', 'Braunschweig')

        def first_name(string: str) -> str:
            names = string.split(' ')
            if len(names) > 2:
                return ' '.join(names[:-1])
            else:
                return names[0]

        def last_name(string: str) -> str:
            return string.split(' ')[-1]

        # Actually get the file
        config = ConfigParser()
        config.read('bot.ini')
        url = config['akadressen']['url']
        username = config['akadressen']['username']
        password = config['akadressen']['password']

        with NamedTemporaryFile(suffix='.pdf', delete=False) as akadressen:
            response = requests.get(url, auth=(username, password), stream=True)
            if response.status_code == 200:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, akadressen)
                akadressen.close()

                # Read tables from PDF
                tables = read_pdf(akadressen.name, flavor='stream', pages='all')
                # Convert to pandas DataFrame
                df = pd.concat([t.df for t in tables])
                # Rename columns
                df = df.rename(columns={
                    0: 'name',
                    1: 'address',
                    2: 'phone',
                    3: 'date_of_birth',
                    4: 'instrument'
                })
                # Drop empty lines
                df = df.replace(r'^\s*$', np.nan, regex=True)
                df = df.dropna(thresh=4)

                # Parse all the data
                df['date_of_birth'] = df.loc[:, 'date_of_birth'].apply(string_to_date)
                df['instrument'] = df.loc[:, 'instrument'].apply(string_to_instrument)
                df['address'] = df.loc[:, 'address'].apply(expand_brunswick)
                df['name'] = df.loc[:, 'name'].apply(remove_whitespaces)
                df['nickname'] = df.loc[:, 'name'].apply(extract_nickname)
                df['name'] = df.loc[:, 'name'].apply(remove_nickname)
                df['first_name'] = df.loc[:, 'name'].apply(first_name)
                df['last_name'] = df.loc[:, 'name'].apply(last_name)

                return df
            else:
                raise Exception('Could not retrieve AkaDressen.')

    _AKADRESSEN: Optional[pd.DataFrame] = None
    _AKADRESSEN_CACHE_TIME: Optional[dt.date] = None

    @classmethod
    def guess_member(cls, user: User) -> Optional[List['Member']]:
        """
        Tries to guess a :class:`components.Member` from the AkaDressen based on the Telegram
        users attributes. May return no or several hits.

        Args:
            user: A Telegram user.
        """

        def generous_ratio(str1: Optional[str], str2: Optional[str]) -> float:
            if str1 is None or str2 is None:
                return 0.0
            str1 = str1.lower().strip(' ')
            str2 = str2.lower().strip(' ')
            return max(fuzz.ratio(str1, str2), fuzz.partial_ratio(str1, str2),
                       fuzz.token_set_ratio(str1, str2))

        # Refresh AkaDressen
        if (cls._AKADRESSEN_CACHE_TIME is None or dt.date.today() > cls._AKADRESSEN_CACHE_TIME
                or cls._AKADRESSEN is None):
            cls._AKADRESSEN = cls._get_akadressen()
            if cls._AKADRESSEN is not None:
                cls._AKADRESSEN_CACHE_TIME = dt.date.today()

        ranking: Dict[int, float] = defaultdict(lambda: 0.0)
        count = 0
        for row in cls._AKADRESSEN.itertuples(index=True):
            ranking[count] = 0
            for attr in ['first_name', 'last_name']:
                ranking[count] += generous_ratio(getattr(user, attr), getattr(row, attr))
            for attr in ['first_name', 'last_name', 'nickname']:
                ranking[count] += generous_ratio(user.username, getattr(row, attr))

            count += 1

        max_ranking = max(ranking.values())
        if max_ranking == 0:
            return None

        list_df = list(cls._AKADRESSEN.itertuples(index=False))
        all_max_rankings = [list_df[idx] for idx in ranking if ranking[idx] == max_ranking]
        members = []
        for row in all_max_rankings:
            members.append(
                Member(user_id=user.id,
                       first_name=row.first_name,
                       last_name=row.last_name,
                       nickname=row.nickname,
                       address=row.address,
                       instruments=row.instrument,
                       date_of_birth=row.date_of_birth))
        return members

    SUBSCRIPTABLE = sorted([
        'birthday', 'age', 'first_name', 'last_name', 'nickname', 'address', 'latitude',
        'longitude', 'instruments', 'gender', 'phone_number', 'date_of_birth', 'full_name',
        'photo_file_id', 'allow_contact_sharing'
    ])
    """List[:obj:`str`]: Attributes supported by subscription."""

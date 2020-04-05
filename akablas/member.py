#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the Member class."""
from akablas import Instrument
from game import UserScore

import datetime as dt
import vobject

from geopy import Photon, distance
from tempfile import TemporaryFile
from typing import Optional, Union, List, Tuple, IO

from fuzzywuzzy import fuzz
from telegram import Bot


class Member:
    """
    A member of AkaBlas.

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
        user_score (:class:`game.UserScore`): A highscore associated with this member.

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
                 phone_number: Optional[str] = None,
                 first_name: Optional[str] = None,
                 last_name: Optional[str] = None,
                 nickname: Optional[str] = None,
                 gender: Optional[str] = None,
                 date_of_birth: Optional[dt.date] = None,
                 instruments: Optional[Union[List[Instrument], Instrument]] = None,
                 address: Optional[str] = None,
                 latitude: Optional[float] = None,
                 longitude: Optional[float] = None,
                 photo_file_id: Optional[str] = None,
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

        self._geo_locator: Photon = Photon()
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

    def set_address(self,
                    address: Optional[str] = None,
                    coordinates: Optional[Tuple[float, float]] = None) -> Optional[str]:
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

        if address:
            location = self._geo_locator.geocode(address)
        else:
            location = self._geo_locator.reverse(coordinates)

        if location:
            if 'properties' in location.raw:
                raw = location.raw['properties']
                if ('street' in raw and 'postcode' in raw and 'housenumber' in raw
                        and 'city' in raw and 'country' in raw):
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

        if self._address is not None:
            self._address = self._address.replace('Brunswick', 'Braunschweig')

        return self._address

    @property
    def full_name(self) -> Optional[str]:
        """
        Full name of the member. May be :obj:`None`.
        """
        if not any([self.first_name, self.last_name, self.nickname]):
            return None
        return ' '.join(
            [n for n in [self.first_name, self.nickname, self.last_name] if n is not None])

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
    def vcard_filename(self) -> str:
        """
        Gives a filename of the vcard generated by :attr:`vcard`.
        """
        return f'{self.full_name}.vcf'.replace(' ', '_')

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
            vcard.add('fn').value = self.full_name or ''
            vcard.add('n').value = vobject.vcard.Name(family=self.last_name or '',
                                                      given=self.first_name or '')
            vcard.add('tel').value = self.phone_number or ''
            vcard.add('role').value = ', '.join([str(i) for i in self.instruments])
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

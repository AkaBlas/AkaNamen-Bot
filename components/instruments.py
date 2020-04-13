#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains the instrument classes."""
from __future__ import annotations
import sys
import inspect


class Instrument:
    """
    Base class for all instruments. Instruments are comparable, where the order is defined by
    class inheritance. For example:

    .. code-block:: python

        Trumpet() < BrassInstrument() # True
        Flugelhorn() <= Trumpet() # False
        BrassInstrument() == BrassInstrument() # True
        AltoSaxophone() == Saxophone() # False

    Moreover, strings can be tested for equality with instruments. The comparison is case
    insensitive. The string will be compared to the string representation of the instrument.

    .. code-block:: python

        Trumpet() == 'Trompete' # True
        Trumpet() == 'trompete' # True
        Trupmet() == 'Saxophon' # False
    """
    name: str = ''

    @staticmethod
    def from_string(string: str) -> Instrument:
        """
        Given a string representation or an AkaBlas-style abbreviation of an instrument, this will
        return a corresponding :class:`components.Instrument` instance.

        Args:
            string: The string.

        Raises:
            ValueError: If the abbreviation is not known.
        """
        string = string.lower().strip(' ')

        if string == 'flö':
            return Flute()
        elif string == 'kla':
            return Clarinet()
        elif string == 'obe':
            return Oboe()
        elif string == 'hlz':
            return WoodwindInstrument()
        elif string == 'sax':
            return Saxophone()
        elif string == 'asx':
            return AltoSaxophone()
        elif string == 'tsx':
            return TenorSaxophone()
        elif string == 'fag':
            return Bassoon()
        elif string == 'trp':
            return Trumpet()
        elif string in ['flü', Flugelhorn.name.lower()]:
            return Flugelhorn()
        elif string == 'teh':
            return BaritoneHorn()
        elif string == 'hrn':
            return Horn()
        elif string == 'pos':
            return Trombone()
        elif string == 'tub':
            return Tuba()
        elif string == 'tpd':
            return PercussionInstrument()
        elif string == 'git':
            return Guitar()
        elif string == 'bss':
            return BassGuitar()
        else:
            cls_members = inspect.getmembers(sys.modules[__name__], inspect.isclass)
            for cls in cls_members:
                if string == cls[1].name.lower():
                    return cls[1]()
            raise ValueError('Unknown instrument description.')

    def __str__(self) -> str:
        return self.name

    __repr__ = __str__

    def __hash__(self) -> int:
        return int.from_bytes(self.name.encode(), byteorder=sys.byteorder)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return str(self).lower() == other.lower()
        return type(self) is type(other)

    def __lt__(self, other: object) -> bool:
        return isinstance(self, type(other))

    def __gt__(self, other: object) -> bool:
        return not self < other

    def __le__(self, other: object) -> bool:
        return self < other or self == other

    def __ge__(self, other: object) -> bool:
        return other <= self


# Categories of instruments
class WoodwindInstrument(Instrument):
    """
    A woodwind instrument.
    """
    name = 'Holz'


class BrassInstrument(Instrument):
    """
    A brass instrument.
    """
    name = 'Blech'


class HighBrassInstrument(BrassInstrument):
    """
    A high brass instrument.
    """
    name = 'Hochblech'


class LowBrassInstrument(BrassInstrument):
    """
    A low brass instrument.
    """
    name = 'Tiefblech'


class PercussionInstrument(Instrument):
    """
    A percussion instrument.
    """
    name = 'Percussion'


# Single instruments
class Conductor(Instrument):
    """
    A conductor. Yeah, not really an instrument. Neither is mayonnaise, Patrick! Who cares?
    """
    name = 'Anzähler'


class Flute(WoodwindInstrument):
    """
    A flute.
    """
    name = 'Querflöte'


class Clarinet(WoodwindInstrument):
    """
    A clarinet.
    """
    name = 'Klarinette'


class Oboe(WoodwindInstrument):
    """
    An oboe.
    """
    name = 'Oboe'


class Bassoon(WoodwindInstrument):
    """
    A bassoon.
    """
    name = 'Fagott'


class Saxophone(WoodwindInstrument):
    """
    A saxophone.
    """
    name = 'Saxophon'


class AltoSaxophone(Saxophone):
    """
    An alto saxophone.
    """
    name = 'Altsaxophon'


class TenorSaxophone(Saxophone):
    """
    A tenor saxophone.
    """
    name = 'Tenorsaxophon'


class SopranoSaxophone(Saxophone):
    """
    A soprano saxophone.
    """
    name = 'Sopransaxophon'


class BaritoneSaxophone(Saxophone):
    """
    A baritone saxophone.
    """
    name = 'Baritonsaxophon'


class Euphonium(LowBrassInstrument):
    """
    An euphonium.
    """
    name = 'Euphonium'


class BaritoneHorn(LowBrassInstrument):
    """
    A baritone horn.
    """
    name = 'Tenorhorn'


class Baritone(LowBrassInstrument):
    """
    A baritone.
    """
    name = 'Bariton'


class Trombone(LowBrassInstrument):
    """
    A trombone.
    """
    name = 'Posaune'


class Tuba(LowBrassInstrument):
    """
    A tuba.
    """
    name = 'Tuba'


class Trumpet(HighBrassInstrument):
    """
    A trumpet.
    """
    name = 'Trompete'


class Flugelhorn(HighBrassInstrument):
    """
    A flugelhorn.
    """
    name = 'Flügelhorn'


class Horn(HighBrassInstrument):
    """
    A horn.
    """
    name = 'Horn'


class Drums(PercussionInstrument):
    """
    The drums.
    """
    name = 'Schlagzeug'


class Guitar(Instrument):
    """
    A guitar.
    """
    name = 'Gitarre'


class BassGuitar(Guitar):
    """
    A bass guitar.
    """
    name = 'Bass-Gitarre'

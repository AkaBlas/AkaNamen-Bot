#!/usr/bin/env python
import pytest
from components import instruments
from components import (Instrument, WoodwindInstrument, BrassInstrument, HighBrassInstrument,
                        LowBrassInstrument, PercussionInstrument, Flute, Clarinet, Oboe, Bassoon,
                        Saxophone, SopranoSaxophone, AltoSaxophone, TenorSaxophone,
                        BaritoneSaxophone, Euphonium, BaritoneHorn, Baritone, Trombone, Tuba,
                        Trumpet, Flugelhorn, Horn, Drums, Guitar, BassGuitar)


class TestInstruments:

    @pytest.mark.parametrize('cls',
                             [i for i in instruments.__dict__.values() if isinstance(i, type)])
    def test_instruments(self, cls):
        instrument = cls()
        assert isinstance(instrument.name, str)
        assert isinstance(str(instrument), str)

    @pytest.mark.parametrize('cls',
                             [i for i in instruments.__dict__.values() if isinstance(i, type)])
    def test_from_string_by_name(self, cls):
        assert Instrument.from_string(cls.name) == cls()

    @pytest.mark.parametrize('abbr, expected', [('flö', Flute()), ('kla', Clarinet()),
                                                ('obe', Oboe()), ('hlz', WoodwindInstrument()),
                                                ('sax', Saxophone()), ('asx', AltoSaxophone()),
                                                ('tsx', TenorSaxophone()), ('fag', Bassoon()),
                                                ('trp', Trumpet()), ('flü', Flugelhorn()),
                                                ('teh', BaritoneHorn()), ('hrn', Horn()),
                                                ('pos', Trombone()), ('tub', Tuba()),
                                                ('tpd', PercussionInstrument()), ('git', Guitar()),
                                                ('bss', BassGuitar())])
    def test_from_string_by_abbreviation(self, abbr, expected):
        assert Instrument.from_string(abbr) == expected

    @pytest.mark.parametrize('string', ['unknown', 'Geige', 'Violin', 'Brennholz'])
    def test_from_string_unknown(self, string):
        with pytest.raises(ValueError, match='Unknown'):
            Instrument.from_string(string)

    def test_from_string_allowed(self):
        assert Instrument.from_string('tub', []) is None
        assert Instrument.from_string('tub', [Trombone(), 'Schlagzeug']) is None
        assert Instrument.from_string('tub', ['Tuba']) == Tuba()
        assert Instrument.from_string('tub', [Tuba()]) == Tuba()

    @pytest.mark.parametrize('cls',
                             [i for i in instruments.__dict__.values() if isinstance(i, type)])
    def test_global(self, cls):
        instrument = cls()
        assert isinstance(instrument, Instrument)
        assert instrument <= Instrument()
        assert Instrument() >= instrument
        assert instrument < Instrument() or type(instrument) is Instrument
        assert Instrument() > instrument or type(instrument) is Instrument
        assert not instrument > Instrument()
        assert instrument == cls()
        assert hash(instrument) == hash(cls())

    @pytest.mark.parametrize('cls',
                             [i for i in instruments.__dict__.values() if isinstance(i, type)])
    def test_string_equality(self, cls):
        assert cls() == cls.name
        assert cls.name.lower() == cls()
        assert not cls() == f' {cls.name}'
        assert not cls() == 'random string'

    @pytest.mark.parametrize('cls', [WoodwindInstrument, BrassInstrument])
    def test_classes(self, cls):
        instrument = cls()
        assert isinstance(instrument, Instrument)

    @pytest.mark.parametrize('cls', [HighBrassInstrument, LowBrassInstrument])
    def test_brass(self, cls):
        instrument = cls()
        assert isinstance(instrument, BrassInstrument)
        assert instrument <= BrassInstrument()
        assert BrassInstrument() >= instrument
        assert instrument < BrassInstrument()
        assert BrassInstrument() > instrument
        assert not instrument > BrassInstrument()
        assert hash(instrument) != hash(BrassInstrument())
        assert instrument == cls()

    @pytest.mark.parametrize('cls', [Trumpet, Flugelhorn, Horn])
    def test_high_brass(self, cls):
        instrument = cls()
        assert isinstance(instrument, HighBrassInstrument)
        assert instrument <= HighBrassInstrument()
        assert HighBrassInstrument() >= instrument
        assert instrument < HighBrassInstrument()
        assert HighBrassInstrument() > instrument
        assert not instrument > HighBrassInstrument()
        assert hash(instrument) != hash(HighBrassInstrument())
        assert instrument == cls()

    @pytest.mark.parametrize('cls', [Euphonium, Baritone, BaritoneHorn, Tuba, Trombone])
    def test_low_brass(self, cls):
        instrument = cls()
        assert isinstance(instrument, LowBrassInstrument)
        assert instrument <= LowBrassInstrument()
        assert LowBrassInstrument() >= instrument
        assert instrument < LowBrassInstrument()
        assert LowBrassInstrument() > instrument
        assert not instrument > LowBrassInstrument()
        assert hash(instrument) != hash(LowBrassInstrument())
        assert instrument == cls()

    @pytest.mark.parametrize('cls', [
        Flute, Clarinet, Oboe, Saxophone, AltoSaxophone, SopranoSaxophone, BaritoneSaxophone,
        TenorSaxophone, Bassoon
    ])
    def test_wood(self, cls):
        instrument = cls()
        assert isinstance(instrument, WoodwindInstrument)
        assert instrument <= WoodwindInstrument()
        assert WoodwindInstrument() >= instrument
        assert instrument < WoodwindInstrument()
        assert WoodwindInstrument() > instrument
        assert not instrument > WoodwindInstrument()
        assert hash(instrument) != hash(WoodwindInstrument())
        assert instrument == cls()

    @pytest.mark.parametrize('cls',
                             [AltoSaxophone, SopranoSaxophone, BaritoneSaxophone, TenorSaxophone])
    def test_sax(self, cls):
        instrument = cls()
        assert isinstance(instrument, Saxophone)
        assert instrument <= Saxophone()
        assert Saxophone() >= instrument
        assert instrument < Saxophone()
        assert Saxophone() > instrument
        assert not instrument > Saxophone()
        assert hash(instrument) != hash(Saxophone())
        assert instrument == cls()

    def test_percussion(self):
        instrument = Drums()
        assert isinstance(instrument, PercussionInstrument)
        assert instrument <= PercussionInstrument()
        assert PercussionInstrument() >= instrument
        assert instrument < PercussionInstrument()
        assert PercussionInstrument() > instrument
        assert not instrument > PercussionInstrument()
        assert hash(instrument) != hash(PercussionInstrument())
        assert instrument == Drums()

    def test_guitar(self):
        instrument = BassGuitar()
        assert isinstance(instrument, Guitar)
        assert instrument <= Guitar()
        assert Guitar() >= instrument
        assert instrument < Guitar()
        assert Guitar() > instrument
        assert not instrument > Guitar()
        assert hash(instrument) != hash(Guitar())
        assert instrument == BassGuitar()

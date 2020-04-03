#!/usr/bin/env python
import pytest
from akablas import instruments
from akablas.instruments import (Instrument, WoodwindInstrument, BrassInstrument,
                                 HighBrassInstrument, LowBrassInstrument, PercussionInstrument,
                                 Flute, Clarinet, Oboe, Bassoon, Saxophone, SopranoSaxophone,
                                 AltoSaxophone, TenorSaxophone, BaritoneSaxophone, Euphonium,
                                 BaritoneHorn, Baritone, Trombone, Tuba, Trumpet, Flugelhorn, Horn,
                                 Drums)


@pytest.mark.parametrize('cls', [i for i in instruments.__dict__.values() if isinstance(i, type)])
def test_instruments(cls):
    instrument = cls()
    assert isinstance(instrument.name, str)
    assert isinstance(str(instrument), str)


@pytest.mark.parametrize('cls', [i for i in instruments.__dict__.values() if isinstance(i, type)])
def test_global(cls):
    instrument = cls()
    assert isinstance(instrument, Instrument)
    assert instrument <= Instrument()
    assert Instrument() >= instrument
    assert instrument < Instrument() or type(instrument) is Instrument
    assert Instrument() > instrument or type(instrument) is Instrument
    assert not instrument > Instrument()
    assert instrument == cls()
    assert hash(instrument) == hash(cls())


@pytest.mark.parametrize('cls', [WoodwindInstrument, BrassInstrument])
def test_classes(cls):
    instrument = cls()
    assert isinstance(instrument, Instrument)


@pytest.mark.parametrize('cls', [HighBrassInstrument, LowBrassInstrument])
def test_brass(cls):
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
def test_high_brass(cls):
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
def test_low_brass(cls):
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
def test_wood(cls):
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
def test_sax(cls):
    instrument = cls()
    assert isinstance(instrument, Saxophone)
    assert instrument <= Saxophone()
    assert Saxophone() >= instrument
    assert instrument < Saxophone()
    assert Saxophone() > instrument
    assert not instrument > Saxophone()
    assert hash(instrument) != hash(Saxophone())
    assert instrument == cls()


def test_percussion():
    instrument = Drums()
    assert isinstance(instrument, PercussionInstrument)
    assert instrument <= PercussionInstrument()
    assert PercussionInstrument() >= instrument
    assert instrument < PercussionInstrument()
    assert PercussionInstrument() > instrument
    assert not instrument > PercussionInstrument()
    assert hash(instrument) != hash(PercussionInstrument())
    assert instrument == Drums()

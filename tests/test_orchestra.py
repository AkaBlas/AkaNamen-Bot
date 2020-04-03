#!/usr/bin/env python
import pytest
import datetime as dt
import pickle

from akablas import Gender, Member, instruments, Orchestra
from collections import defaultdict
from tempfile import NamedTemporaryFile


@pytest.fixture(scope='function')
def member():
    return Member(user_id=123456)


@pytest.fixture(scope='function')
def orchestra():
    return Orchestra()


class TestOrchestra:

    def test_init(self, orchestra):
        assert isinstance(orchestra.members, dict)
        for list_ in orchestra.lists_to_attrs:
            assert isinstance(getattr(orchestra, list_), defaultdict)

    def test_properties_immutable(self, orchestra):
        with pytest.raises(ValueError, match='overridden'):
            orchestra.members = 1
        for list_ in orchestra.lists_to_attrs:
            with pytest.raises(ValueError, match='overridden'):
                setattr(orchestra, list_, 1)

    def test_register_and_update_member(self, orchestra, member):
        member.first_name = 'first_name'
        member.last_name = 'last_name'
        member.nickname = 'nickname'
        member.gender = Gender.DIVERSE
        member.date_of_birth = dt.date(1996, 8, 10)
        member.instruments = [instruments.Tuba(), instruments.Trumpet()]
        member.set_address(address='Universitätsplatz 2, 38106 Braunschweig')

        orchestra.register_member(member)
        assert orchestra.members == {123456: member}
        assert orchestra.first_names == {'first_name': {member}}
        assert orchestra.last_names == {'last_name': {member}}
        assert orchestra.nicknames == {'nickname': {member}}
        assert orchestra.genders == {Gender.DIVERSE: {member}}
        assert orchestra.instruments == {
            instruments.Tuba(): {member},
            instruments.Trumpet(): {member}
        }
        assert orchestra.dates_of_birth == {dt.date(1996, 8, 10): {member}}
        assert orchestra.addresses == {'Universitätsplatz 2, 38106 Braunschweig': {member}}

        with pytest.raises(ValueError, match='already'):
            orchestra.register_member(member)

        member.first_name = 'First_name'
        member.last_name = 'Last_name'
        member.nickname = 'Nickname'
        member.gender = Gender.MALE
        member.date_of_birth = dt.date(1996, 8, 11)
        member.instruments = instruments.Oboe()
        member.set_address(address='Universitätsplatz 1, 38106 Braunschweig')

        orchestra.update_member(member)
        assert orchestra.members == {123456: member}
        assert orchestra.first_names == {'first_name': set(), 'First_name': {member}}
        assert orchestra.last_names == {'last_name': set(), 'Last_name': {member}}
        assert orchestra.nicknames == {'nickname': set(), 'Nickname': {member}}
        assert orchestra.genders == {Gender.DIVERSE: set(), Gender.MALE: {member}}
        assert orchestra.instruments == {
            instruments.Tuba(): set(),
            instruments.Trumpet(): set(),
            instruments.Oboe(): {member}
        }
        assert orchestra.dates_of_birth == {
            dt.date(1996, 8, 10): set(),
            dt.date(1996, 8, 11): {member}
        }
        assert orchestra.addresses == {
            'Universitätsplatz 2, 38106 Braunschweig': set(),
            'Universitätsplatz 1, 38106 Braunschweig': {member}
        }

    def test_kick_member(self, orchestra, member):
        member.first_name = 'first_name'
        member.last_name = 'last_name'
        orchestra.register_member(member)

        assert orchestra.members == {123456: member}
        orchestra.kick_member(member)

        assert orchestra.members == dict()
        for list_name in orchestra.lists_to_attrs:
            list_ = getattr(orchestra, list_name)
            assert list_ == dict() or all(list_[key] == set() for key in list_)

        with pytest.raises(ValueError, match='not'):
            orchestra.kick_member(member)

    def test_pickle(self, orchestra, member):
        member.first_name = 'John'
        member.last_name = 'Doe'
        orchestra.register_member(member)

        with NamedTemporaryFile() as file:
            pickle.dump(orchestra, file)
            file.flush()
            o = pickle.load(open(file.name, 'rb'))

            assert o.members == {member.user_id: member}
            assert o.first_names['John'] == {member}
            assert o.last_names['Doe'] == {member}

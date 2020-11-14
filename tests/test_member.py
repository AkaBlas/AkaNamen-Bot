#!/usr/bin/env python
import pytest
import datetime as dt
import responses
import pandas as pd
from geopy import Photon
from components import Gender, Member, instruments, UserScore
from telegram import User

from tests.addresses import get_address_from_cache
from tests.check_file_path import check_file_path


@pytest.fixture(scope='function')
def member(monkeypatch):
    return Member(user_id=123456)


@pytest.fixture(scope='module')
def photo_file_id(bot, chat_id):
    with open(check_file_path('tests/data/vcard_photo.png'), 'rb') as file:
        message = bot.send_photo(chat_id=chat_id, photo=file)
        min_file = min(message.photo, key=lambda x: x.file_size)
        return min_file.file_id


@pytest.fixture(
    scope='class',
    params=[
        'foo',
        'bar',
        'a very long long long string',
        'AN ALL UPPERCASE STRING',
        '          ',
        'a-b-c-d',
        '123456789',
    ],
)
def test_string(request):
    return request.param


class TestMember:
    user_id = 123456
    phone_number = 'phone_number'
    first_name = 'first_name'
    last_name = 'last_name'
    nickname = 'nickname'
    gender = Gender.MALE
    date_of_birth = dt.date(1996, 8, 10)
    joined = 2000
    photo_file_id = 'photo_file_id'
    functions = ['Lappenwart', 'Pärchenwart']
    allow_contact_sharing = True
    instruments = [instruments.Tuba(), instruments.Trumpet()]
    address = 'Universitätsplatz 2, 38106 Braunschweig'
    latitude = 52.2736706
    longitude = 10.5296817

    def test_all_args(self, monkeypatch):
        monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)

        member = Member(
            user_id=self.user_id,
            phone_number=self.phone_number,
            first_name=self.first_name,
            last_name=self.last_name,
            nickname=self.nickname,
            gender=self.gender,
            date_of_birth=self.date_of_birth,
            photo_file_id=self.photo_file_id,
            allow_contact_sharing=self.allow_contact_sharing,
            instruments=self.instruments,
            address=self.address,
            joined=self.joined,
            functions=self.functions,
        )
        assert member.user_id == self.user_id
        assert member.phone_number == self.phone_number
        assert member['phone_number'] == self.phone_number
        assert member.first_name == self.first_name
        assert member['first_name'] == self.first_name
        assert member.last_name == self.last_name
        assert member['last_name'] == member.last_name
        assert member.nickname == self.nickname
        assert member['nickname'] == self.nickname
        assert member.gender == self.gender
        assert member['gender'] == self.gender
        assert member.date_of_birth == self.date_of_birth
        assert member['date_of_birth'] == self.date_of_birth
        assert member.joined == self.joined
        assert member['joined'] == self.joined
        assert member.photo_file_id == self.photo_file_id
        assert member['photo_file_id'] == self.photo_file_id
        assert member.allow_contact_sharing == self.allow_contact_sharing
        assert member.instruments == self.instruments
        assert member['instruments'] == self.instruments
        assert member.functions == self.functions
        assert member['functions'] == self.functions
        assert isinstance(member.user_score, UserScore)
        assert member.user_score.member == member

        assert member.address == 'Universitätsplatz 2, 38106 Braunschweig'
        assert member['address'] == 'Universitätsplatz 2, 38106 Braunschweig'
        assert pytest.approx(member.latitude, self.latitude)
        assert pytest.approx(member['latitude'], self.latitude)
        assert pytest.approx(member['longitude'], self.longitude)
        assert pytest.approx(member.longitude, self.longitude)

        def reverse(*args):
            return get_address_from_cache('Universitätsplatz 2, 38106 Braunschweig')

        monkeypatch.setattr(Photon, 'reverse', reverse)

        member = Member(user_id=self.user_id, latitude=self.latitude, longitude=self.longitude)
        assert member.user_id == self.user_id
        assert member.address == 'Universitätsplatz 2, 38106 Braunschweig'
        assert pytest.approx(member.latitude, self.latitude)
        assert pytest.approx(member.longitude, self.longitude)

        member = Member(user_id=self.user_id, instruments=instruments.Bassoon())
        assert member.user_id == self.user_id
        assert member.instruments == [instruments.Bassoon()]

    def test_repr(self, member):
        member.first_name = 'first'
        member.nickname = 'nick'
        member.last_name = 'last'
        assert repr(member) == 'Member(first "nick" last)'
        member = Member(1)
        assert repr(member) == 'Member(1)'

    def test_subscriptable_error(self, member):
        with pytest.raises(KeyError, match='Member either'):
            member['foo']

    def test_instruments_property(self, member):
        assert member.instruments == []
        member.instruments = None
        assert member.instruments == []
        member.instruments = instruments.Oboe()
        assert member.instruments == [instruments.Oboe()]
        member.instruments = [instruments.Oboe(), instruments.Baritone()]
        assert member.instruments == [instruments.Oboe(), instruments.Baritone()]
        member.instruments = [
            instruments.Oboe(),
            instruments.Baritone(),
            instruments.WoodwindInstrument(),
            instruments.Conductor(),
        ]
        assert member.instruments == [instruments.Oboe(), instruments.Baritone()]
        member.instruments = instruments.WoodwindInstrument()
        assert member.instruments == []

    def test_functions_property(self, member):
        assert member.functions == []
        member.functions = None
        assert member.functions == []
        member.functions = 'Wart'
        assert member.functions == ['Wart']
        member.functions = ['Wart1', 'Wart2']
        assert member.functions == ['Wart1', 'Wart2']

    def test_address_and_coordinates(self):
        with pytest.raises(ValueError, match='Only address'):
            Member(
                self.user_id,
                address=self.address,
                latitude=self.latitude,
                longitude=self.longitude,
            )
        with pytest.raises(ValueError, match='Either none'):
            Member(self.user_id, latitude=self.latitude)

    @pytest.mark.parametrize('attr', ['address', 'latitude', 'longitude'])
    def test_immutable_properties(self, member, attr):
        with pytest.raises(ValueError, match=attr):
            setattr(member, attr, 'test')

    def test_set_address(self, member, monkeypatch):
        monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)
        member.set_address(address=self.address)
        assert member.address == 'Universitätsplatz 2, 38106 Braunschweig'
        assert pytest.approx(member.latitude, self.latitude)
        assert pytest.approx(member.longitude, self.longitude)

        def reverse(*args):
            return get_address_from_cache('Universitätsplatz 2, 38106 Braunschweig')

        monkeypatch.setattr(Photon, 'reverse', reverse)

        member.set_address(coordinates=(self.latitude, self.longitude))
        assert member.address == 'Universitätsplatz 2, 38106 Braunschweig'
        assert pytest.approx(member.latitude, self.latitude)
        assert pytest.approx(member.longitude, self.longitude)

        with pytest.raises(ValueError):
            member.set_address(coordinates=(0, 1), address='address')

        with pytest.raises(ValueError):
            member.set_address()

    def test_set_address_international(self, member, monkeypatch):
        monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)
        assert 'Denmark' in member.set_address(address='Hammervej 20, 7160 Tørring, Dänemark')

    def test_set_address_bad_response_1(self, monkeypatch):
        member = Member(1)

        def geocode_1(*args, **kwargs):
            return None

        monkeypatch.setattr(Photon, 'geocode', geocode_1)
        assert member.set_address(address=self.address) is None
        assert member.latitude is None
        assert member.longitude is None
        assert member._raw_address is None

    def test_set_address_bad_response_2(self, monkeypatch):
        member = Member(1)

        def geocode_2(*args, **kwargs):
            location = get_address_from_cache(args[1])
            location.raw.clear()
            return location

        monkeypatch.setattr(Photon, 'geocode', geocode_2)
        assert 'Universitätsplatz' in member.set_address(address=self.address)
        assert member.latitude is not None
        assert member.longitude is not None
        assert member._raw_address is None

    def test_set_address_bad_response_3(self, monkeypatch):
        member = Member(1)

        def geocode_3(*args, **kwargs):
            location = get_address_from_cache(args[1])
            if 'properties' in location.raw:
                location.raw['properties'].clear()
            return location

        monkeypatch.setattr(Photon, 'geocode', geocode_3)
        assert 'Universitätsplatz' in member.set_address(address=self.address)
        assert member.latitude is not None
        assert member.longitude is not None
        assert member._raw_address is None

    def test_full_name(self, member):
        assert member.full_name is None

        member.first_name = self.first_name
        assert member.full_name == self.first_name
        assert member['full_name'] == self.first_name

        member.last_name = self.last_name
        assert member.full_name == ' '.join([self.first_name, self.last_name])
        assert member['full_name'] == ' '.join([self.first_name, self.last_name])

        member.nickname = self.nickname
        assert member.full_name == ' '.join(
            [self.first_name, f'"{self.nickname}"', self.last_name]
        )
        assert member['full_name'] == ' '.join(
            [self.first_name, f'"{self.nickname}"', self.last_name]
        )

        member.first_name = None
        assert member.full_name == ' '.join([f'"{self.nickname}"', self.last_name])
        assert member['full_name'] == ' '.join([f'"{self.nickname}"', self.last_name])

    def test_instruments_str(self, member):
        member.instruments = None
        assert member.instruments_str is None

        member.instruments = instruments.Tuba()
        assert member.instruments_str == 'Tuba'

        member.instruments = [instruments.Tuba(), instruments.Trumpet()]
        assert member.instruments_str == 'Tuba, Trompete'

    def test_functions_str(self, member):
        member.functions = None
        assert member.functions_str is None

        member.functions = 'Wart'
        assert member.functions_str == 'Wart'

        member.functions = ['Wart1', 'Wart2']
        assert member.functions_str == 'Wart1, Wart2'

    def test_vcard_filename(self, member):
        member.first_name = self.first_name
        member.last_name = self.last_name
        assert member.vcard_filename == f'{self.first_name}_{self.last_name}.vcf'

    def test_vcard(self, member, bot, photo_file_id, monkeypatch):
        monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)

        with pytest.raises(ValueError):
            member.vcard(bot)

        with member.vcard(bot, admin=True) as vcard:
            vcard_string = vcard.read().decode('utf-8')
            assert 'NAME' in vcard_string

        member.allow_contact_sharing = True
        with member.vcard(bot) as vcard:
            vcard_string = vcard.read().decode('utf-8')
            assert 'NAME' in vcard_string

        member.nickname = 'test'
        with member.vcard(bot) as vcard:
            vcard_string = vcard.read().decode('utf-8')
            assert 'ADR' not in vcard_string
            assert 'PHOTO' not in vcard_string
            assert 'BDAY' not in vcard_string

        member.date_of_birth = dt.date(1990, 1, 1)
        with member.vcard(bot) as vcard:
            vcard_string = vcard.read().decode('utf-8')
            assert 'BDAY:19900101' in vcard_string

        member.set_address(address='Universitätsplatz 2, 38106 Braunschweig')
        with member.vcard(bot) as vcard:
            vcard_string = vcard.read().decode('utf-8')
            assert 'Universitätsplatz 2' in vcard_string

        member.photo_file_id = photo_file_id
        with member.vcard(bot) as vcard:
            vcard_string = vcard.read().decode('utf-8')
            assert 'PHOTO;ENCODING=B;' in vcard_string

        member.instruments = self.instruments
        with member.vcard(bot) as vcard:
            vcard_string = vcard.read().decode('utf-8')
            assert 'ORG:AkaBlas e.V.;Tuba\, Trompete' in vcard_string

        member.gender = Gender.MALE
        with member.vcard(bot) as vcard:
            vcard_string = vcard.read().decode('utf-8')
            assert 'GENDER:M' in vcard_string

        member.functions = self.functions
        with member.vcard(bot) as vcard:
            vcard_string = vcard.read().decode('utf-8')
            assert 'TITLE:Lappenwart\, Pärchenwart' in vcard_string

    def test_age(self, member, today):
        assert member.age is None
        member.date_of_birth = dt.date(1999, 12, 31)
        assert member.age == today.year - 2000
        assert member['age'] == today.year - 2000

    def test_birthday(self, member, today):
        assert member.birthday is None
        member.date_of_birth = dt.date(1999, 12, 31)
        assert member.birthday == '31.12.'
        assert member['birthday'] == '31.12.'

    def test_distance_of_address_to(self, member, monkeypatch):
        monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)

        with pytest.raises(ValueError, match='This member has no'):
            member.distance_of_address_to((52.273549, 10.529447))

        def reverse(*args):
            return get_address_from_cache('Universitätsplatz 2, 38106 Braunschweig')

        monkeypatch.setattr(Photon, 'reverse', reverse)

        member.set_address(coordinates=(52.2736706, 10.5296817))
        assert member.distance_of_address_to((52.2736706, 10.5296817)) == pytest.approx(
            0, abs=0.02
        )

        assert member.distance_of_address_to((52.280073, 10.544101)) == pytest.approx(
            1.215, abs=0.01
        )

    def test_compare_address_to(self, member, test_string, monkeypatch):
        with pytest.raises(ValueError, match='This member has no'):
            member.compare_address_to(test_string)

        monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)
        member.set_address('Universitätsplatz 2, 38106 Braunschweig')
        assert 0 <= member.compare_address_to(test_string) <= 1
        assert member.compare_address_to(member.address) == pytest.approx(1)

    def test_compare_nickname_to(self, member, test_string):
        with pytest.raises(ValueError, match='This member has no'):
            member.compare_nickname_to(test_string)

        member.nickname = 'Jochen'
        assert 0 <= member.compare_nickname_to(test_string) <= 1
        assert member.compare_nickname_to(member.nickname) == pytest.approx(1)

    def test_compare_first_name_to(self, member, test_string):
        with pytest.raises(ValueError, match='This member has no'):
            member.compare_first_name_to(test_string)

        member.first_name = 'Jochen'
        assert 0 <= member.compare_first_name_to(test_string) <= 1
        assert member.compare_first_name_to(member.first_name) == pytest.approx(1)

    def test_compare_last_name_to(self, member, test_string):
        with pytest.raises(ValueError, match='This member has no'):
            member.compare_last_name_to(test_string)

        member.last_name = 'Jochen'
        assert 0 <= member.compare_last_name_to(test_string) <= 1
        assert member.compare_last_name_to(member.last_name) == pytest.approx(1)

    def test_compare_instruments_to(self, member, test_string):
        with pytest.raises(ValueError, match='This member has no'):
            member.compare_instruments_to(test_string)

        member.instruments = self.instruments
        assert 0 <= member.compare_instruments_to(test_string) <= 1
        assert member.compare_instruments_to(member.instruments_str) == pytest.approx(1)
        assert member.compare_instruments_to('Tuba') == pytest.approx(1)

    def test_compare_functions_to(self, member, test_string):
        with pytest.raises(ValueError, match='This member holds no'):
            member.compare_functions_to(test_string)

        member.functions = self.functions
        assert 0 <= member.compare_functions_to(test_string) <= 1
        assert member.compare_functions_to('Lappenwart') == pytest.approx(1)
        assert member.compare_functions_to('Wart') < 1

    def test_compare_functions_to_gendering(self, member):
        member.functions = 'Pärchenwart'
        member.gender = None

        assert member.compare_functions_to('Männerwart') < 1
        assert member.compare_functions_to('Frauenwart') < 1

        member.gender = Gender.MALE

        assert member.compare_functions_to('Männerwart') < 1
        assert member.compare_functions_to('Frauenwart') == pytest.approx(1)

        member.gender = Gender.FEMALE

        assert member.compare_functions_to('Männerwart') == pytest.approx(1)
        assert member.compare_functions_to('Frauenwart') < 1

        assert member.functions == ['Pärchenwart']

    def test_copy(self, monkeypatch):
        monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)

        member = Member(
            user_id=self.user_id,
            phone_number=self.phone_number,
            first_name=self.first_name,
            last_name=self.last_name,
            nickname=self.nickname,
            gender=self.gender,
            date_of_birth=self.date_of_birth,
            photo_file_id=self.photo_file_id,
            allow_contact_sharing=self.allow_contact_sharing,
            instruments=self.instruments,
            address=self.address,
            joined=self.joined,
            functions=self.functions,
        )
        new_member = member.copy()

        assert new_member is not member
        assert new_member.user_id == member.user_id
        assert new_member.phone_number == member.phone_number
        assert new_member.first_name == member.first_name
        assert new_member.last_name == member.last_name
        assert new_member.nickname == member.nickname
        assert new_member.gender == member.gender
        assert new_member.date_of_birth == member.date_of_birth
        assert new_member.photo_file_id == member.photo_file_id
        assert new_member.allow_contact_sharing == member.allow_contact_sharing
        assert new_member.instruments == member.instruments
        assert new_member.address == member.address
        assert new_member._raw_address == member._raw_address
        assert new_member._address == member._address
        assert new_member._longitude == member._longitude
        assert new_member._latitude == member._latitude
        assert new_member.joined == member.joined
        assert new_member.functions == member.functions

    def test_copy_backwards_compat(self):
        member = Member(1)
        del member._functions
        del member.joined

        new_member = member.copy()
        assert new_member.functions == []
        assert new_member.joined is None

    def test_to_string(self, member, monkeypatch):
        monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)

        assert member.to_str() == (
            'Name: -\n'
            'Geschlecht: -\n'
            'Geburtstag: -\n'
            'Instrument/e: -\n'
            'Dabei seit: -\n'
            'Ämter: -\n'
            'Adresse: -\n'
            'Mobil: -\n'
            'Foto: -\n'
            'Daten an AkaBlasen weitergeben: Deaktiviert'
        )
        member.first_name = self.first_name
        member.nickname = self.nickname
        member.last_name = self.last_name
        member.gender = Gender.MALE
        member.set_address(self.address)
        member.date_of_birth = self.date_of_birth
        member.joined = self.joined
        member.functions = self.functions
        member.photo_file_id = self.photo_file_id
        member.phone_number = self.phone_number
        member.instruments = [instruments.Tuba(), instruments.Trumpet()]
        member.allow_contact_sharing = True
        assert member.to_str() == (
            'Name: first_name "nickname" last_name\n'
            f'Geschlecht: {Gender.MALE}\n'
            'Geburtstag: 10. August 1996\n'
            'Instrument/e: Tuba, Trompete\n'
            'Dabei seit: 2000\n'
            'Ämter: Lappenwart, Pärchenwart\n'
            'Adresse: Universitätsplatz 2, 38106 Braunschweig\n'
            'Mobil: phone_number\n'
            'Foto: 🖼\n'
            'Daten an AkaBlasen weitergeben: Aktiviert'
        )

    @responses.activate
    def test_guess_member(self, monkeypatch):
        monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)

        Member.set_akadressen_credentials('http://all', 'http://active', '', '')

        with open(check_file_path('tests/data/akadressen.pdf'), 'rb') as akadressen:
            responses.add(
                responses.GET,
                'http://all',
                body=akadressen.read(),
                stream=True,
                status=200,
                adding_headers={'Transfer-Encoding': 'chunked'},
            )

        with open(check_file_path('tests/data/akadressen-active.pdf'), 'rb') as akadressen_active:
            responses.add(
                responses.GET,
                'http://active',
                body=akadressen_active.read(),
                stream=True,
                status=200,
                adding_headers={'Transfer-Encoding': 'chunked'},
            )

        assert Member._AKADRESSEN_CACHE_TIME is None
        assert Member._AKADRESSEN is None
        user_1 = User(1, is_bot=False, first_name='John', last_name='Doe')
        members = Member.guess_member(user_1)
        assert Member._AKADRESSEN_CACHE_TIME == dt.date.today()
        assert isinstance(Member._AKADRESSEN, pd.DataFrame)
        assert len(members) == 1
        member = members[0]
        assert member.user_id == 1
        assert member.last_name == 'Doe'
        assert member.first_name == 'John'
        assert member.nickname == 'Jonny'
        assert member.date_of_birth == dt.date(2000, 1, 1)
        assert member.instruments == [instruments.Trumpet()]
        assert member.address == 'Münzstraße 5, 38100 Braunschweig'
        assert member.joined == 2004

        Member._AKADRESSEN = None
        user_2 = User(2, is_bot=False, first_name='Marcel', last_name='Marcel')
        members = Member.guess_member(user_2)
        assert Member._AKADRESSEN_CACHE_TIME == dt.date.today()
        assert isinstance(Member._AKADRESSEN, pd.DataFrame)
        assert len(members) == 1
        member = members[0]
        assert member.user_id == 2
        assert member.last_name == 'Marcel'
        assert member.first_name == 'Marcel'
        assert member.nickname is None
        assert member.date_of_birth == dt.date(2000, 5, 1)
        assert member.instruments == []
        assert member.address == 'Universitätsplatz 2, 38106 Braunschweig'
        assert member.joined == 2005

        test_flag = False

        def _get_akadressen(*args, **kwargs):
            nonlocal test_flag
            test_flag = True

        monkeypatch.setattr(Member, '_get_akadressen', _get_akadressen)

        user_3 = User(3, is_bot=False, first_name='Test', username='Das Brot')
        members = Member.guess_member(user_3)
        assert Member._AKADRESSEN_CACHE_TIME == dt.date.today()
        assert isinstance(Member._AKADRESSEN, pd.DataFrame)
        assert not test_flag
        assert len(members) == 1
        member = members[0]
        assert member.user_id == 3
        assert member.last_name == 'Zufall'
        assert member.first_name == 'Rainer'
        assert member.nickname == 'Das Brot'
        assert member.date_of_birth == dt.date(2007, 7, 5)
        assert member.instruments == [instruments.Flute()]
        assert member.address == 'Bültenweg 74-75, 38106 Braunschweig'
        assert member.joined is None

        user_4 = User(1, is_bot=False, first_name=None)
        assert Member.guess_member(user_4) is None

    def test_equality(self, member):
        a = member
        b = Member(member.user_id, allow_contact_sharing=True)
        c = Member(123)
        d = Photon()

        assert a == b
        assert hash(a) == hash(b)

        assert a != c
        assert hash(a) != hash(c)

        assert a != d
        assert hash(a) != hash(d)

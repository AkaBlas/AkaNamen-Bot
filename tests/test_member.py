#!/usr/bin/env python
import pytest
import datetime as dt
from geopy import Photon
from akablas import Gender, Member, instruments
from game import UserScore


@pytest.fixture(scope='function')
def member():
    return Member(user_id=123456)


@pytest.fixture(scope='module')
def photo_file_id(bot, chat_id):
    with open('tests/data/vcard_photo.png', 'rb') as file:
        message = bot.send_photo(chat_id=chat_id, photo=file)
        min_file = min(message.photo, key=lambda x: x.file_size)
        return min_file.file_id


@pytest.fixture(scope='class',
                params=[
                    'foo', 'bar', 'a very long long long string', 'AN ALL UPPERCASE STRING',
                    '          ', 'a-b-c-d', '123456789'
                ])
def test_string(request):
    return request.param


class TestMember:
    user_id = 123456
    phone_number = 'phone_number'
    first_name = 'first_name'
    last_name = 'last_name'
    nickname = 'nickname'
    gender = Gender.DIVERSE
    date_of_birth = dt.date(1996, 8, 10)
    photo_file_id = 'photo_file_id'
    allow_contact_sharing = True
    instruments = [instruments.Tuba(), instruments.Trumpet()]
    address = 'Universitätsplatz 2, 38106 Braunschweig'
    latitude = 52.2736706
    longitude = 10.5296817

    def test_all_args(self):
        member = Member(user_id=self.user_id,
                        phone_number=self.phone_number,
                        first_name=self.first_name,
                        last_name=self.last_name,
                        nickname=self.nickname,
                        gender=self.gender,
                        date_of_birth=self.date_of_birth,
                        photo_file_id=self.photo_file_id,
                        allow_contact_sharing=self.allow_contact_sharing,
                        instruments=self.instruments,
                        address=self.address)
        assert member.user_id == self.user_id
        assert member.phone_number == self.phone_number
        assert member.first_name == self.first_name
        assert member.last_name == self.last_name
        assert member.nickname == self.nickname
        assert member.gender == self.gender
        assert member.date_of_birth == self.date_of_birth
        assert member.photo_file_id == self.photo_file_id
        assert member.allow_contact_sharing == self.allow_contact_sharing
        assert member.instruments == self.instruments
        assert isinstance(member.user_score, UserScore)
        assert member.user_score.member == member

        assert member.address == 'Universitätsplatz 2, 38106 Braunschweig'
        assert pytest.approx(member.latitude, self.latitude)
        assert pytest.approx(member.longitude, self.longitude)

        member = Member(user_id=self.user_id, latitude=self.latitude, longitude=self.longitude)
        assert member.user_id == self.user_id
        assert member.address == 'Universitätsplatz 2, 38106 Braunschweig'
        assert pytest.approx(member.latitude, self.latitude)
        assert pytest.approx(member.longitude, self.longitude)

        member = Member(user_id=self.user_id, instruments=instruments.Bassoon())
        assert member.user_id == self.user_id
        assert member.instruments == [instruments.Bassoon()]

    def test_instruments_property(self, member):
        assert member.instruments == []
        member.instruments = None
        assert member.instruments == []
        member.instruments = instruments.Oboe()
        assert member.instruments == [instruments.Oboe()]
        member.instruments = [instruments.Oboe(), instruments.Baritone]
        assert member.instruments == [instruments.Oboe(), instruments.Baritone]

    def test_address_and_coordinates(self):
        with pytest.raises(ValueError, match='Only address'):
            Member(self.user_id,
                   address=self.address,
                   latitude=self.latitude,
                   longitude=self.longitude)
        with pytest.raises(ValueError, match='Either none'):
            Member(self.user_id, latitude=self.latitude)

    @pytest.mark.parametrize('attr', ['address', 'latitude', 'longitude'])
    def test_immutable_properties(self, member, attr):
        with pytest.raises(ValueError, match=attr):
            setattr(member, attr, 'test')

    def test_set_address(self, member):
        member.set_address(address=self.address)
        assert member.address == 'Universitätsplatz 2, 38106 Braunschweig'
        assert pytest.approx(member.latitude, self.latitude)
        assert pytest.approx(member.longitude, self.longitude)

        member.set_address(coordinates=(self.latitude, self.longitude))
        assert member.address == 'Universitätsplatz 2, 38106 Braunschweig'
        assert pytest.approx(member.latitude, self.latitude)
        assert pytest.approx(member.longitude, self.longitude)

        with pytest.raises(ValueError):
            member.set_address(coordinates=(0, 1), address='address')

        with pytest.raises(ValueError):
            member.set_address()

    def test_set_address_bad_response(self, member, monkeypatch):

        def geocode_1(*args, **kwargs):
            return None

        monkeypatch.setattr(member._geo_locator, 'geocode', geocode_1)
        assert member.set_address(address=self.address) is None
        assert member.latitude is None
        assert member.longitude is None
        assert member._raw_address is None

        def geocode_2(*args, **kwargs):
            location = Photon().geocode(*args, **kwargs)
            location.raw.clear()
            return location

        monkeypatch.setattr(member._geo_locator, 'geocode', geocode_2)
        assert 'Universitätsplatz' in member.set_address(address=self.address)
        assert member.latitude is not None
        assert member.longitude is not None
        assert member._raw_address is None

        def geocode_3(*args, **kwargs):
            location = Photon().geocode(*args, **kwargs)
            location.raw['properties'].clear()
            return location

        monkeypatch.setattr(member._geo_locator, 'geocode', geocode_3)
        assert 'Universitätsplatz' in member.set_address(address=self.address)
        assert member.latitude is not None
        assert member.longitude is not None
        assert member._raw_address is None

    def test_set_address_international(self, member):
        assert 'Denmark' in member.set_address(address='Hammervej 20, 7160 Tørring, Dänemark')

    def test_full_name(self, member):
        assert member.full_name is None

        member.first_name = self.first_name
        assert member.full_name == self.first_name

        member.last_name = self.last_name
        assert member.full_name == ' '.join([self.first_name, self.last_name])

        member.nickname = self.nickname
        assert member.full_name == ' '.join([self.first_name, self.nickname, self.last_name])

        member.first_name = None
        assert member.full_name == ' '.join([self.nickname, self.last_name])

    def test_vcard_filename(self, member):
        member.first_name = self.first_name
        member.last_name = self.last_name
        assert member.vcard_filename == f'{self.first_name}_{self.last_name}.vcf'

    def test_vcard(self, member, bot, photo_file_id):
        with pytest.raises(ValueError):
            member.vcard(bot)

        member.allow_contact_sharing = True
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

    def test_age(self, member, today):
        assert member.age is None
        member.date_of_birth = dt.date(1999, 12, 31)
        assert member.age == today.year - 2000

    def test_birthday(self, member, today):
        assert member.birthday is None
        member.date_of_birth = dt.date(1999, 12, 31)
        assert member.birthday == '31.12.'

    def test_distance_of_address_to(self, member):
        with pytest.raises(ValueError, match='This member has no'):
            member.distance_of_address_to((52.273549, 10.529447))

        member.set_address(coordinates=(52.273549, 10.529447))
        assert member.distance_of_address_to((52.273549, 10.529447)) == pytest.approx(0, abs=0.02)

        assert member.distance_of_address_to((52.280073, 10.544101)) == pytest.approx(1.245,
                                                                                      abs=0.01)

    def test_compare_address_to(self, member, test_string):
        with pytest.raises(ValueError, match='This member has no'):
            member.compare_address_to(test_string)

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

#!/usr/bin/env python
import pytest
import os
import datetime as dt
import pickle

from components import Gender, Member, instruments, Orchestra, Score
from collections import defaultdict
from tempfile import NamedTemporaryFile


@pytest.fixture(scope='function')
def member():
    return Member(user_id=123456)


@pytest.fixture(scope='function')
def orchestra():
    return Orchestra()


def score_orchestra(date):
    o = Orchestra()
    offset = dt.timedelta(weeks=100)
    m_1 = Member(1, first_name='One')
    m_1.user_score.add_to_score(8, 4, date)
    m_1.user_score.add_to_score(10, 10, date - offset)
    m_2 = Member(2, first_name='Two')
    m_2.user_score.add_to_score(4, 2, date)
    m_2.user_score.add_to_score(10, 10, date - offset)
    m_3 = Member(3, first_name='Three')
    m_3.user_score.add_to_score(3, 1, date)
    m_3.user_score.add_to_score(10, 10, date - offset)
    m_4 = Member(4, first_name='Four')
    m_4.user_score.add_to_score(4, 1, date)
    m_4.user_score.add_to_score(10, 10, date - offset)
    for m in [m_1, m_2, m_3, m_4]:
        o.register_member(m)
    return o


class TestOrchestra:

    def test_init(self, orchestra):
        assert isinstance(orchestra.members, dict)
        for dict_ in orchestra.DICTS_TO_ATTRS:
            assert isinstance(getattr(orchestra, dict_), dict)

    def test_properties_immutable(self, orchestra):
        with pytest.raises(ValueError, match='overridden'):
            orchestra.members = 1
        for dict_ in orchestra.DICTS_TO_ATTRS:
            with pytest.raises(ValueError, match='overridden'):
                setattr(orchestra, dict_, 1)

    def test_register_and_update_member(self, orchestra, member, today):
        member.first_name = 'first_name'
        member.last_name = 'last_name'
        member.nickname = 'nickname'
        member.gender = Gender.MALE
        member.date_of_birth = dt.date(1999, 12, 31)
        member.instruments = [instruments.Tuba(), instruments.Trumpet()]
        member.set_address(address='Universitätsplatz 2, 38106 Braunschweig')

        orchestra.register_member(member)
        assert orchestra.members == {123456: member}
        assert orchestra.members[123456] is not member
        assert orchestra.first_names == {'first_name': {member}}
        assert orchestra.last_names == {'last_name': {member}}
        assert orchestra.nicknames == {'nickname': {member}}
        assert orchestra.genders == {Gender.MALE: {member}}
        assert orchestra.instruments == {
            instruments.Tuba(): {member},
            instruments.Trumpet(): {member}
        }
        assert orchestra.dates_of_birth == {dt.date(1999, 12, 31): {member}}
        assert orchestra.addresses == {'Universitätsplatz 2, 38106 Braunschweig': {member}}
        assert orchestra.ages == {today.year - 2000: {member}}
        assert orchestra.birthdays == {'31.12.': {member}}

        with pytest.raises(ValueError, match='already'):
            orchestra.register_member(member)

        member.first_name = 'First_name'
        member.last_name = 'Last_name'
        member.nickname = 'Nickname'
        member.gender = Gender.FEMALE
        member.date_of_birth = dt.date(2000, 12, 31)
        member.instruments = instruments.Oboe()
        member.set_address(address='Universitätsplatz 1, 38106 Braunschweig')

        orchestra.update_member(member)
        assert orchestra.members == {123456: member}
        assert orchestra.members[123456] is not member
        assert orchestra.first_names == {'first_name': set(), 'First_name': {member}}
        assert orchestra.last_names == {'last_name': set(), 'Last_name': {member}}
        assert orchestra.nicknames == {'nickname': set(), 'Nickname': {member}}
        assert orchestra.genders == {Gender.MALE: set(), Gender.FEMALE: {member}}
        assert orchestra.instruments == {
            instruments.Tuba(): set(),
            instruments.Trumpet(): set(),
            instruments.Oboe(): {member}
        }
        assert orchestra.dates_of_birth == {
            dt.date(1999, 12, 31): set(),
            dt.date(2000, 12, 31): {member}
        }
        assert orchestra.addresses == {
            'Universitätsplatz 2, 38106 Braunschweig': set(),
            'Universitätsplatz 1, 38106 Braunschweig': {member}
        }
        assert orchestra.ages == {today.year - 2000: set(), today.year - 2001: {member}}
        assert orchestra.birthdays == {'31.12.': {member}}

    def test_gender_first_names(self, orchestra):
        assert orchestra.questionable == []
        orchestra.register_member(Member(4, first_name='John', gender=Gender.MALE))
        orchestra.register_member(Member(5, first_name='Mike', gender=Gender.MALE))
        orchestra.register_member(Member(6, first_name='Tina', gender=Gender.FEMALE))
        orchestra.register_member(Member(7, first_name='Rita', gender=Gender.FEMALE))
        orchestra.register_member(Member(8, first_name='Linda', gender=Gender.FEMALE))
        orchestra.register_member(Member(9, first_name='Sandra', gender=Gender.FEMALE))
        orchestra.register_member(Member(10, first_name='Brad', gender=Gender.MALE))
        orchestra.register_member(Member(11, first_name='Marc', gender=Gender.MALE))

        assert orchestra.male_first_names == {
            'John': {Member(4)},
            'Mike': {Member(5)},
            'Brad': {Member(10)},
            'Marc': {Member(11)}
        }
        assert orchestra.female_first_names == {
            'Tina': {Member(6)},
            'Rita': {Member(7)},
            'Linda': {Member(8)},
            'Sandra': {Member(9)}
        }

    def test_ages_caching(self, member, today):

        class AgesOrchestra(Orchestra):

            def __init__(self, *args, **kwargs):
                self.test_flag = 0
                self.__ages = defaultdict(set)
                super().__init__(*args, **kwargs)

            @property  # type: ignore
            def _ages(self):
                return self.__ages

            @_ages.setter
            def _ages(self, value):
                self.__ages = value
                self.test_flag += 1

        orchestra = AgesOrchestra()
        assert orchestra.test_flag == 1
        member.date_of_birth = dt.date(1999, 12, 31)
        orchestra.register_member(member)
        assert orchestra.ages == {today.year - 2000: {member}}
        assert orchestra.test_flag == 2

        # Make sure ages isn't recomputed
        assert orchestra.ages == {today.year - 2000: {member}}
        assert orchestra.test_flag == 2

        # Make sure ages is recomputed
        orchestra._ages_cache_date = orchestra._ages_cache_date - dt.timedelta(days=1)
        assert orchestra.ages == {today.year - 2000: {member}}
        assert orchestra.test_flag == 3

    def test_kick_member(self, orchestra, member):
        member.first_name = 'first_name'
        member.last_name = 'last_name'
        orchestra.register_member(member)

        assert orchestra.members == {123456: member}
        orchestra.kick_member(member)

        assert orchestra.members == dict()
        for list_name in orchestra.DICTS_TO_ATTRS:
            list_ = getattr(orchestra, list_name)
            assert list_ == dict() or all(list_[key] == set() for key in list_)

        with pytest.raises(ValueError, match='not'):
            orchestra.kick_member(member)

    @pytest.mark.skipif(os.name == 'nt',
                        reason="Not worth the struggle stetting this up for windows.")
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

    def test_scores(self, today):
        todays_score = score_orchestra(today).todays_score
        weeks_score = score_orchestra(today - dt.timedelta(days=today.weekday())).weeks_score
        months_score = score_orchestra(today - dt.timedelta(days=today.day - 1)).months_score
        years_score = score_orchestra(dt.date(today.year, 1, 1)).years_score
        overall_score = score_orchestra(today).overall_score

        for score in [todays_score, weeks_score, months_score, years_score]:
            assert score[0].member == Member(1)
            assert score[0] == Score(8, 4)
            assert score[1].member == Member(2)
            assert score[1] == Score(4, 2)
            assert score[2].member == Member(3)
            assert score[2] == Score(3, 1)
            assert score[3].member == Member(4)
            assert score[3] == Score(4, 1)

        assert overall_score[0].member == Member(2)
        assert overall_score[0] == Score(14, 12)
        assert overall_score[1].member == Member(3)
        assert overall_score[1] == Score(13, 11)
        assert overall_score[2].member == Member(4)
        assert overall_score[2] == Score(14, 11)
        assert overall_score[3].member == Member(1)
        assert overall_score[3] == Score(18, 14)

    def test_score_texts(self, today):
        todays_score_text = score_orchestra(today).todays_score_text()
        weeks_score_text = score_orchestra(today - dt.timedelta(
            days=today.weekday())).weeks_score_text()
        months_score_text = score_orchestra(today - dt.timedelta(days=today.day
                                                                 - 1)).months_score_text()
        years_score_text = score_orchestra(dt.date(today.year, 1, 1)).years_score_text()
        overall_score_text = score_orchestra(today).overall_score_text()

        expected = ('1. One: 4 / 8\n   ▬▬▬▬▬▭▭▭▭▭  50.00 %\n2. Two: 2 / 4\n   ▬▬▬▬▬▭▭▭▭▭  50.00 %'
                    '\n3. Three: 1 / 3\n   ▬▬▬▭▭▭▭▭▭▭  33.33 %\n4. Four: 1 / 4\n   ▬▬▭▭▭▭▭▭▭▭  '
                    '25.00 %')
        expected_overall = ('1. Two: 12 / 14\n   ▬▬▬▬▬▬▬▬▭▭  85.71 %\n'
                            '2. Three: 11 / 13\n   ▬▬▬▬▬▬▬▬▭▭  84.62 %\n'
                            '3. Four: 11 / 14\n   ▬▬▬▬▬▬▬▭▭▭  78.57 %\n'
                            '4. One: 14 / 18\n   ▬▬▬▬▬▬▬▭▭▭  77.78 %')

        for score_text in [
                todays_score_text, weeks_score_text, months_score_text, years_score_text
        ]:
            assert score_text == expected

        assert expected_overall == overall_score_text

    def test_score_texts_length(self, today):
        todays_score_text = score_orchestra(today).todays_score_text(length=2)
        weeks_score_text = score_orchestra(today
                                           - dt.timedelta(days=today.weekday())).weeks_score_text(
                                               length=2)
        months_score_text = score_orchestra(today
                                            - dt.timedelta(days=today.day - 1)).months_score_text(
                                                length=2)
        years_score_text = score_orchestra(dt.date(today.year, 1, 1)).years_score_text(length=2)
        overall_score_text = score_orchestra(today).overall_score_text(length=2)

        expected = '1. One: 4 / 8\n   ▬▬▬▬▬▭▭▭▭▭  50.00 %\n2. Two: 2 / 4\n   ▬▬▬▬▬▭▭▭▭▭  50.00 %'
        expected_overall = ('1. Two: 12 / 14\n   ▬▬▬▬▬▬▬▬▭▭  85.71 %\n'
                            '2. Three: 11 / 13\n   ▬▬▬▬▬▬▬▬▭▭  84.62 %')

        for score_text in [
                todays_score_text, weeks_score_text, months_score_text, years_score_text
        ]:
            assert score_text == expected

        assert expected_overall == overall_score_text

    def test_score_texts_html(self, today):
        todays_score_text = score_orchestra(today).todays_score_text(html=True)
        weeks_score_text = score_orchestra(today
                                           - dt.timedelta(days=today.weekday())).weeks_score_text(
                                               html=True)
        months_score_text = score_orchestra(today
                                            - dt.timedelta(days=today.day - 1)).months_score_text(
                                                html=True)
        years_score_text = score_orchestra(dt.date(today.year, 1, 1)).years_score_text(html=True)
        overall_score_text = score_orchestra(today).overall_score_text(html=True)

        expected = ('1. <b>One:</b> 4 / 8\n   ▬▬▬▬▬▭▭▭▭▭  50.00 %\n'
                    '2. <b>Two:</b> 2 / 4\n   ▬▬▬▬▬▭▭▭▭▭  50.00 %\n'
                    '3. <b>Three:</b> 1 / 3\n   ▬▬▬▭▭▭▭▭▭▭  33.33 %\n'
                    '4. <b>Four:</b> 1 / 4\n   ▬▬▭▭▭▭▭▭▭▭  25.00 %')
        expected_overall = ('1. <b>Two:</b> 12 / 14\n   ▬▬▬▬▬▬▬▬▭▭  85.71 %\n'
                            '2. <b>Three:</b> 11 / 13\n   ▬▬▬▬▬▬▬▬▭▭  84.62 %\n'
                            '3. <b>Four:</b> 11 / 14\n   ▬▬▬▬▬▬▬▭▭▭  78.57 %\n'
                            '4. <b>One:</b> 14 / 18\n   ▬▬▬▬▬▬▬▭▭▭  77.78 %')

        for score_text in [
                todays_score_text, weeks_score_text, months_score_text, years_score_text
        ]:
            assert score_text == expected

        assert expected_overall == overall_score_text

    def test_score_text_large_number(self, today):
        o = score_orchestra(today)

        for i in range(5, 101):
            o.register_member(Member(i))

        assert o.todays_score_text().partition('\n')[0] == '  1. One: 4 / 8'
        assert o.weeks_score_text().partition('\n')[0] == '  1. One: 4 / 8'
        assert o.months_score_text().partition('\n')[0] == '  1. One: 4 / 8'
        assert o.years_score_text().partition('\n')[0] == '  1. One: 4 / 8'
        assert o.overall_score_text().partition('\n')[0] == '  1. Two: 12 / 14'

    def test_score_text_anonymous_member(self):
        o = Orchestra()
        o.register_member(Member(1))
        assert 'Anonym' in o.todays_score_text()
        assert 'Anonym' in o.weeks_score_text()
        assert 'Anonym' in o.months_score_text()
        assert 'Anonym' in o.years_score_text()
        assert 'Anonym' in o.overall_score_text()

    def test_questionable(self, orchestra):
        assert orchestra.questionable == []
        orchestra.register_member(Member(1, first_name='John'))
        orchestra.register_member(Member(2, first_name='John'))
        orchestra.register_member(Member(3, first_name='John'))
        orchestra.register_member(Member(4, first_name='John'))
        assert orchestra.questionable == []
        orchestra.register_member(Member(5, first_name='Mike'))
        orchestra.register_member(Member(6, first_name='Brad'))
        orchestra.register_member(Member(7, first_name='Marc'))
        assert orchestra.questionable == ['first_names']

    def test_questionable_with_gender(self, orchestra):
        assert orchestra.questionable == []
        orchestra.register_member(Member(4, first_name='John', gender=Gender.MALE))
        orchestra.register_member(Member(5, first_name='Mike', gender=Gender.MALE))
        orchestra.register_member(Member(6, first_name='Brad', gender=Gender.FEMALE))
        orchestra.register_member(Member(7, first_name='Marc', gender=Gender.FEMALE))
        assert orchestra.questionable == ['first_names']
        orchestra.register_member(Member(8, first_name='John', gender=Gender.FEMALE))
        orchestra.register_member(Member(9, first_name='Mike', gender=Gender.FEMALE))
        orchestra.register_member(Member(10, first_name='Brad', gender=Gender.MALE))
        orchestra.register_member(Member(11, first_name='Marc', gender=Gender.MALE))
        assert sorted(orchestra.questionable) == sorted(
            ['first_names', 'female_first_names', 'male_first_names'])

    def test_draw_members_errors(self, orchestra, member):
        with pytest.raises(ValueError, match='Attribute not supported.'):
            orchestra.draw_members(member, 'some attribute')

        with pytest.raises(ValueError, match='Not enough members'):
            orchestra.draw_members(member, 'first_name')

    def test_draw_members(self, orchestra):
        member = Member(1, last_name='John')
        orchestra.register_member(member)
        orchestra.register_member(Member(2, last_name='John'))
        orchestra.register_member(Member(3, last_name='Brad'))
        orchestra.register_member(Member(4, last_name='Brad'))
        orchestra.register_member(Member(5, last_name='Mike'))
        orchestra.register_member(Member(6, last_name='Mike'))
        orchestra.register_member(Member(7, last_name='Marc'))
        orchestra.register_member(Member(8, last_name='Marc'))

        index, members = orchestra.draw_members(member, 'last_name')
        assert members[index] is member
        assert len(set([m.user_id for m in members])) == 4
        assert len(set([m.last_name for m in members])) == 4

        index, members = orchestra.draw_members(member, 'last_names')
        assert members[index] is member
        assert len(set([m.user_id for m in members])) == 4
        assert len(set([m.last_name for m in members])) == 4

    def test_draw_members_gendered(self, orchestra):
        assert orchestra.questionable == []
        member_1 = Member(4, first_name='John', gender=Gender.MALE)
        member_2 = Member(8, first_name='Linda', gender=Gender.FEMALE)
        orchestra.register_member(member_1)
        orchestra.register_member(Member(5, first_name='Mike', gender=Gender.MALE))
        orchestra.register_member(Member(6, first_name='Tina', gender=Gender.FEMALE))
        orchestra.register_member(Member(7, first_name='Rita', gender=Gender.FEMALE))
        orchestra.register_member(member_2)
        orchestra.register_member(Member(9, first_name='Sandra', gender=Gender.FEMALE))
        orchestra.register_member(Member(10, first_name='Brad', gender=Gender.MALE))
        orchestra.register_member(Member(11, first_name='Marc', gender=Gender.MALE))

        index, members = orchestra.draw_members(member_1, 'male_first_names')
        assert members[index] is member_1
        assert len(set([m.user_id for m in members])) == 4
        assert len(set([m.first_name for m in members])) == 4
        assert all([m.gender == Gender.MALE for m in members])

        index, members = orchestra.draw_members(member_2, 'female_first_names')
        assert members[index] is member_2
        assert len(set([m.user_id for m in members])) == 4
        assert len(set([m.first_name for m in members])) == 4
        assert all([m.gender == Gender.FEMALE for m in members])

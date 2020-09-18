#!/usr/bin/env python
from uuid import uuid4

import pytest
import datetime as dt
from geopy import Photon

from components import Gender, Member, instruments, Orchestra, Score, AttributeManager

from tests.addresses import get_address_from_cache


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


def score_orchestra_anonymous(date):
    o = Orchestra()
    offset = dt.timedelta(weeks=100)
    m_1 = Member(1)
    m_1.user_score.add_to_score(8, 4, date)
    m_1.user_score.add_to_score(10, 10, date - offset)
    o.register_member(m_1)
    return o


class TestOrchestra:

    def test_init_and_subscriptable(self, orchestra):
        assert isinstance(orchestra.members, dict)
        for dict_ in orchestra.SUBSCRIPTABLE:
            assert isinstance(orchestra[dict_], AttributeManager)

    def test_subscriptable_error(self, orchestra):
        with pytest.raises(KeyError, match='Orchestra either'):
            orchestra['foo']

    def test_register_and_update_member(self, orchestra, member, today, monkeypatch):
        monkeypatch.setattr(Photon, 'geocode', get_address_from_cache)

        member.first_name = 'first_name'
        member.last_name = 'last_name'
        member.nickname = 'nickname'
        member.photo_file_id = 'photo_file_id'
        member.gender = Gender.MALE
        member.date_of_birth = dt.date(1999, 12, 31)
        member.instruments = [instruments.Tuba(), instruments.Trumpet()]
        member.set_address(address='Universitätsplatz 2, 38106 Braunschweig')

        orchestra.register_member(member)
        assert orchestra.members == {123456: member}
        assert orchestra.members[123456] is not member
        assert orchestra.members[123456].user_score.member is not member
        assert orchestra.attribute_managers['first_name'].male_data == {'first_name': {member}}
        assert orchestra.attribute_managers['last_name'].data == {'last_name': {member}}
        assert orchestra.attribute_managers['nickname'].data == {'nickname': {member}}
        assert orchestra.attribute_managers['full_name'].data == {
            'first_name "nickname" last_name': {member}
        }
        assert orchestra.attribute_managers['instruments'].data == {
            instruments.Tuba(): {member},
            instruments.Trumpet(): {member}
        }
        assert orchestra.attribute_managers['address'].data == {
            'Universitätsplatz 2, 38106 Braunschweig': {member}
        }
        assert orchestra.attribute_managers['age'].data == {today.year - 2000: {member}}
        assert orchestra.attribute_managers['birthday'].data == {'31.12.': {member}}
        assert orchestra.attribute_managers['photo_file_id'].data == {'photo_file_id': {member}}

        with pytest.raises(ValueError, match='already'):
            orchestra.register_member(member)

        member.first_name = 'First_name'
        member.last_name = 'Last_name'
        member.nickname = 'Nickname'
        member.photo_file_id = 'Photo_File_ID'
        member.gender = Gender.FEMALE
        member.date_of_birth = dt.date(2000, 12, 31)
        member.instruments = instruments.Oboe()
        member.set_address(address='Universitätsplatz 1, 38106 Braunschweig')

        orchestra.update_member(member)
        assert orchestra.members == {123456: member}
        assert orchestra.members[123456] is not member
        assert orchestra.members[123456].user_score.member is not member
        assert orchestra.attribute_managers['first_name'].female_data == {'First_name': {member}}
        assert orchestra.attribute_managers['last_name'].data == {'Last_name': {member}}
        assert orchestra.attribute_managers['nickname'].data == {'Nickname': {member}}
        assert orchestra.attribute_managers['instruments'].data == {instruments.Oboe(): {member}}
        assert orchestra.attribute_managers['address'].data == {
            'Universitätsplatz 1, 38106 Braunschweig': {member}
        }
        assert orchestra.attribute_managers['age'].data == {today.year - 2001: {member}}
        assert orchestra.attribute_managers['birthday'].data == {'31.12.': {member}}
        assert orchestra.attribute_managers['photo_file_id'].data == {'Photo_File_ID': {member}}

    def test_kick_member(self, orchestra, member):
        member.first_name = 'first_name'
        member.last_name = 'last_name'
        orchestra.register_member(member)

        assert orchestra.members == {123456: member}
        orchestra.kick_member(member)

        assert orchestra.members == dict()
        for am in orchestra.attribute_managers.values():
            am.available_members == set()

        with pytest.raises(ValueError, match='not'):
            orchestra.kick_member(member)

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

    def test_score_texts_empty(self, today, orchestra):
        todays_score_text = orchestra.todays_score_text()
        weeks_score_text = orchestra.weeks_score_text()
        months_score_text = orchestra.months_score_text()
        years_score_text = orchestra.years_score_text()
        overall_score_text = orchestra.overall_score_text()

        expected = 'Noch keine Einträge vorhanden.'

        for score_text in [
                todays_score_text, weeks_score_text, months_score_text, years_score_text,
                overall_score_text
        ]:
            assert score_text.startswith(expected)

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

        assert o.todays_score_text().partition('\n')[0] == '1. One: 4 / 8'
        assert o.weeks_score_text().partition('\n')[0] == '1. One: 4 / 8'
        assert o.months_score_text().partition('\n')[0] == '1. One: 4 / 8'
        assert o.years_score_text().partition('\n')[0] == '1. One: 4 / 8'
        assert o.overall_score_text().partition('\n')[0] == '1. Two: 12 / 14'

    def test_score_text_anonymous_member(self, today):
        todays_score_text = score_orchestra_anonymous(today).todays_score_text()
        weeks_score_text = score_orchestra_anonymous(today - dt.timedelta(
            days=today.weekday())).weeks_score_text()
        months_score_text = score_orchestra_anonymous(today - dt.timedelta(
            days=today.day - 1)).months_score_text()
        years_score_text = score_orchestra_anonymous(dt.date(today.year, 1, 1)).years_score_text()
        overall_score_text = score_orchestra_anonymous(today).overall_score_text()

        for score_text in [
                todays_score_text, weeks_score_text, months_score_text, years_score_text,
                overall_score_text
        ]:
            assert 'Anonym' in score_text

    def test_questionable(self, orchestra):
        assert orchestra.questionable() == []
        orchestra.register_member(Member(1, first_name='John', gender=Gender.MALE))
        orchestra.register_member(Member(2, first_name='John', gender=Gender.MALE))
        orchestra.register_member(Member(3, first_name='John', gender=Gender.MALE))
        orchestra.register_member(Member(4, first_name='John', gender=Gender.MALE))
        assert orchestra.questionable() == []
        orchestra.register_member(Member(5, first_name='Mike', gender=Gender.MALE))
        orchestra.register_member(Member(6, first_name='Brad', gender=Gender.MALE))
        orchestra.register_member(Member(7, first_name='Marc', gender=Gender.MALE))
        orchestra.register_member(Member(8, first_name='Joe', gender=Gender.MALE))
        assert orchestra.questionable() == []
        orchestra.register_member(
            Member(9, first_name='Dong', last_name='Silver', gender=Gender.MALE))
        assert orchestra.questionable() == [('last_name', 'first_name')]
        assert orchestra.questionable(exclude_members=[Member(9)]) == []

    def test_questionable_multiple_choice_first_name(self, orchestra):
        assert orchestra.questionable() == []
        orchestra.register_member(Member(1, first_name='John', last_name='test'))
        orchestra.register_member(Member(5, first_name='Mike', last_name='test'))
        orchestra.register_member(Member(6, first_name='Brad', last_name='test'))
        orchestra.register_member(Member(7, first_name='Marc', last_name='test'))
        orchestra.register_member(Member(8, first_name='Joe', last_name='test'))
        assert orchestra.questionable() == []
        assert orchestra.questionable(multiple_choice=False) == [('first_name', 'last_name')]

    def test_questionable_multiple_choice_photo(self, orchestra):
        assert orchestra.questionable() == []
        orchestra.register_member(Member(1, first_name='John', photo_file_id=str(uuid4())))
        orchestra.register_member(Member(5, first_name='Mike', photo_file_id=str(uuid4())))
        orchestra.register_member(Member(6, first_name='Brad', photo_file_id=str(uuid4())))
        orchestra.register_member(Member(7, first_name='Marc', photo_file_id=str(uuid4())))
        orchestra.register_member(Member(8, first_name='Joe', photo_file_id=str(uuid4())))
        assert orchestra.questionable() == []
        assert orchestra.questionable(multiple_choice=False) == [('photo_file_id', 'first_name'),
                                                                 ('photo_file_id', 'full_name')]

#!/usr/bin/env python
import pytest
import datetime as dt

from akablas import Member, Gender, instruments
from game import Question

from telegram import Poll, PollAnswer, Update, Message, Location


class TestQuestion:
    member = Member(1,
                    first_name='first',
                    last_name='last',
                    nickname='nickname',
                    gender=Gender.DIVERSE,
                    date_of_birth=dt.date(dt.date.today().year - 21, 12, 31),
                    instruments=instruments.AltoSaxophone(),
                    address='Universitätsplatz 2, 38106 Braunschweig')
    poll = Poll(123, 'question', ['Opt1', 'Opt2'], 0, False, False, Poll.QUIZ, False, 1)

    def test_init(self):
        for attr in Question.SUPPORTED_ATTRIBUTES:
            q = Question(self.member, attr, multiple_choice=False)
            assert q.member == self.member
            assert q.attribute == attr
            assert q.multiple_choice is False

            q = Question(self.member, attr, poll=self.poll)
            assert q.member == self.member
            assert q.attribute == attr
            assert q.multiple_choice is True
            assert q.poll == self.poll

    def test_init_errors(self):
        member = Member(1)
        invalid_poll = Poll(123, 'question', ['Opt1', 'Opt2'], 0, False, False, Poll.REGULAR, True)

        with pytest.raises(ValueError, match='must be a quiz poll'):
            Question(member, Question.AGE, poll=invalid_poll)

        with pytest.raises(ValueError, match='poll if and only if'):
            Question(member, Question.AGE, multiple_choice=False, poll=self.poll)
        with pytest.raises(ValueError, match='poll if and only if'):
            Question(member, Question.AGE)

        with pytest.raises(ValueError, match='Attribute not supported'):
            Question(member, 'attribute')

        for attr in Question.SUPPORTED_ATTRIBUTES:
            with pytest.raises(ValueError, match='the required attribute'):
                Question(member, attr, multiple_choice=False)

    def test_class_attributes(self):
        assert isinstance(Question.SUPPORTED_ATTRIBUTES, list)
        for attr in Question.SUPPORTED_ATTRIBUTES:
            assert isinstance(attr, str)

    def test_check_update_multiple_choice(self):
        valid_update = Update(1, poll_answer=PollAnswer(123, None, [1]))
        invalid_update = Update(1, message=True)

        for attr in Question.SUPPORTED_ATTRIBUTES:
            q = Question(self.member, attr, poll=self.poll)
            assert q.check_update(valid_update)
            assert not q.check_update(invalid_update)

    def test_check_update_free_text(self):
        valid_update = Update(1, message=Message(1, None, None, None, text='text'))
        invalid_update = Update(1, poll_answer=PollAnswer(123, None, [1]))

        for attr in Question.SUPPORTED_ATTRIBUTES:
            q = Question(self.member, attr, multiple_choice=False)
            assert q.check_update(valid_update)
            assert not q.check_update(invalid_update)

        q = Question(self.member, Question.ADDRESS, multiple_choice=False)

        valid_update = Update(1,
                              message=Message(1,
                                              None,
                                              None,
                                              None,
                                              location=Location(longitude=1, latitude=1)))
        invalid_update = Update(1, poll_answer=PollAnswer(123, None, [1]))
        assert q.check_update(valid_update)
        assert not q.check_update(invalid_update)

    def test_check_answer_multiple_choice(self):
        correct_update = Update(1, poll_answer=PollAnswer(123, None, [1]))
        false_update = Update(1, poll_answer=PollAnswer(123, None, [0]))

        for attr in Question.SUPPORTED_ATTRIBUTES:
            q = Question(self.member, attr, poll=self.poll)
            assert q.check_answer(correct_update)
            assert not q.check_answer(false_update)
            assert q.correct_answer == 'Opt2'

    @pytest.mark.parametrize('answer, result', [('first', True), ('FiRsT', True), ('FIRST', True),
                                                (' first', True), ('first name', True),
                                                ('last', False), ('none', False),
                                                ('some very wrong answer', False)])
    def test_check_answer_free_text_first_name(self, answer, result):
        q = Question(self.member, Question.FIRST_NAME, multiple_choice=False)
        update = Update(1, message=Message(1, None, None, None, text=answer))
        assert q.check_answer(update) is result
        assert q.correct_answer == self.member.first_name

    @pytest.mark.parametrize('answer, result', [('last', True), ('LaSt', True), ('LAST', True),
                                                (' last', True), ('last name', True),
                                                ('first', False), ('none', False),
                                                ('some very wrong answer', False)])
    def test_check_answer_free_text_last_name(self, answer, result):
        q = Question(self.member, Question.LAST_NAME, multiple_choice=False)
        update = Update(1, message=Message(1, None, None, None, text=answer))
        assert q.check_answer(update) is result
        assert q.correct_answer == self.member.last_name

    @pytest.mark.parametrize('answer, result', [('nickname', True), ('NiCKnAMe', True),
                                                ('NICKNAME', True), (' nickname', True),
                                                ('nick name', True), ('first name', False),
                                                ('none', False),
                                                ('some very wrong answer', False)])
    def test_check_answer_free_text_nickname(self, answer, result):
        q = Question(self.member, Question.NICKNAME, multiple_choice=False)
        update = Update(1, message=Message(1, None, None, None, text=answer))
        assert q.check_answer(update) is result
        assert q.correct_answer == self.member.nickname

    @pytest.mark.parametrize('answer, result', [('first nick last', True),
                                                ('FiRSt niCKnaMe LaSt', True),
                                                ('FIRST NICKNAME LAST', True),
                                                ('  FIRST   NICK   LAST  ', True),
                                                ('first last', True), ('first nick', True),
                                                ('nick last', True), ('nick', False),
                                                ('last', False), ('fisrt nik lst', True),
                                                ('first', False), ('none', False),
                                                ('some very wrong answer', False)])
    def test_check_answer_free_text_full_name(self, answer, result):
        self.member.nickname = 'nick'
        q = Question(self.member, Question.FULL_NAME, multiple_choice=False)
        update = Update(1, message=Message(1, None, None, None, text=answer))
        assert q.check_answer(update) is result
        assert q.correct_answer == self.member.full_name

    @pytest.mark.parametrize('answer, result', [('31.12.', True), ('31 12', True), ('3112', True),
                                                ('  31 12 ', True), ('31:12:', False),
                                                ('31 11', False), ('30.12.', False),
                                                ('01.14.', False),
                                                ('some very wrong answer', False)])
    def test_check_answer_free_text_birthday(self, answer, result):
        q = Question(self.member, Question.BIRTHDAY, multiple_choice=False)
        update = Update(1, message=Message(1, None, None, None, text=answer))
        assert q.check_answer(update) is result
        assert q.correct_answer == str(self.member.birthday)

    @pytest.mark.parametrize('answer, result', [('20', True), ('  20', True), ('21', False),
                                                ('20  ', True), ('19', False), (' 30', False),
                                                ('some very wrong answer', False)])
    def test_check_answer_free_text_age(self, answer, result):
        q = Question(self.member, Question.AGE, multiple_choice=False)
        update = Update(1, message=Message(1, None, None, None, text=answer))
        assert q.check_answer(update) is result
        assert q.correct_answer == str(self.member.age)

    @pytest.mark.parametrize('answer, result', [(str(instruments.AltoSaxophone()), True),
                                                (f' {instruments.AltoSaxophone()} ', True),
                                                (str(instruments.SopranoSaxophone()), False),
                                                (f'{instruments.Saxophone()} ', False)])
    def test_check_answer_free_text_instrument(self, answer, result):
        q = Question(self.member, Question.INSTRUMENT, multiple_choice=False)
        update = Update(1, message=Message(1, None, None, None, text=answer))
        assert q.check_answer(update) is result
        assert q.correct_answer == str(self.member.instruments)

    @pytest.mark.parametrize('answer, result', [('Universitätsplatz, Braunschweig', True),
                                                ('Univeritätsplatz 2, Braunschweig', True),
                                                ('Universitätpltz 3, BRAUNSCHWEIG', True),
                                                ('Schleinitzstraße 19, Braunschweig', False),
                                                ('Schleinitzstraße 19, 38106 Braunschweig', False),
                                                ('Universitätsplatz 2, 38106 Braunschweig', True),
                                                ('Universtatsplatz Braunschweig', True)])
    def test_check_answer_free_text_location_text(self, answer, result):
        q = Question(self.member, Question.ADDRESS, multiple_choice=False)
        update = Update(1, message=Message(1, None, None, None, text=answer))
        assert q.check_answer(update) is result
        assert q.correct_answer == self.member.address

    @pytest.mark.parametrize('answer, result', [((52.273450, 10.529699), True),
                                                ((52.273450, 10.529699), True),
                                                ((52.274507, 10.528648), True),
                                                ((52.277041, 10.528380), False),
                                                ((52.280024, 10.544396), False)])
    def test_check_answer_free_text_location_coords(self, answer, result):
        q = Question(self.member, Question.ADDRESS, multiple_choice=False)
        update = Update(1,
                        message=Message(1, None, None, None, location=Location(*reversed(answer))))
        assert q.check_answer(update) is result
        assert q.correct_answer == self.member.address

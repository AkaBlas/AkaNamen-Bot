#!/usr/bin/env python
import random
import datetime as dtm
import pytest

from components import Member, AttributeManager, NameManager, Gender, Tuba, Trombone, \
    Trumpet, Drums, Bassoon, Clarinet, Horn, Flute, ChangingAttributeManager


@pytest.fixture(scope='function')
def member():
    return Member(user_id=123456)


@pytest.fixture(scope='function')
def dummy_am():
    return AttributeManager('dummy', [])


class TestAttributeManager:
    description = 'last_name'

    def test_init(self, member, dummy_am):
        am = AttributeManager(self.description, [dummy_am])
        member.last_name = 'test'
        assert am.description == self.description
        assert am.questionable_attributes == [dummy_am]
        assert am.data == {}
        assert am.get_members_attribute(member) == 'test'

    def test_init_custom_gma(self, member, dummy_am):

        def gma(m: Member):
            return '5'

        am = AttributeManager(self.description, [dummy_am], get_members_attribute=gma)
        member.last_name = 'test'
        assert am.description == self.description
        assert am.questionable_attributes == [dummy_am]
        assert am.data == {}
        assert am.get_members_attribute(member) == '5'

    def test_equality(self, dummy_am):
        am = AttributeManager('abc', [])
        bm = AttributeManager('abc', [dummy_am])
        cm = AttributeManager('def', [])

        assert am == bm
        assert am == 'abc'
        assert am != cm
        assert am in ['abc', 'def']
        assert am != 1

    def test_repr(self):
        am = AttributeManager('desc', [])
        assert repr(am) == 'AttributeManager(desc)'

    def test_members_share_attribute(self):
        am = AttributeManager('first_name', [])
        assert not am.members_share_attribute(Member(1), Member(2))
        assert not am.members_share_attribute(Member(1, first_name='a'), Member(2))
        assert not am.members_share_attribute(Member(1, first_name='a'), Member(2, first_name='b'))
        assert am.members_share_attribute(Member(1, first_name='a'), Member(2, first_name='a'))

        am = AttributeManager('instruments', [])
        assert not am.members_share_attribute(Member(1), Member(2))
        assert not am.members_share_attribute(Member(1, instruments=Tuba()), Member(2))
        assert not am.members_share_attribute(Member(1), Member(
            2, instruments=[Tuba(), Trombone()]))
        assert not am.members_share_attribute(Member(
            1, instruments=Tuba()), Member(2, instruments=[Trumpet(), Trombone()]))
        assert am.members_share_attribute(Member(1, instruments=Tuba()),
                                          Member(2, instruments=Tuba()))
        assert am.members_share_attribute(Member(1, instruments=[Trumpet(), Trombone()]),
                                          Member(2, instruments=[Tuba(), Trombone()]))

    def test_register_member_without_attribute(self, member):
        am = AttributeManager(self.description, [])
        am.register_member(member)
        assert am.data == {}

    def test_register_member_with_attribute(self, member):
        member.last_name = 'test1'
        am = AttributeManager(self.description, [])

        am.register_member(member)
        assert am.data == {'test1': {member}}
        assert all(member is not m for m in am.data['test1'])

        member2 = Member(2, last_name='test2')
        am.register_member(member2)
        assert am.data == {'test1': {member}, 'test2': {member2}}
        assert (member2 is not m for m in am.data['test2'])

        member3 = Member(4, last_name='test1')
        am.register_member(member3)
        assert am.data == {'test1': {member, member3}, 'test2': {member2}}
        assert all(member3 is not m for m in am.data['test1'])

    def test_double_register(self, member):
        member.last_name = 'test'
        am = AttributeManager(self.description, [])

        am.register_member(member)
        with pytest.raises(RuntimeError, match='Member is already registered.'):
            am.register_member(Member(user_id=123456, last_name='test1'))

    def test_kick_member(self, member):
        member.last_name = 'test'
        am = AttributeManager(self.description, [])

        am.register_member(member)
        assert am.data == {'test': {member}}

        am.kick_member(member)
        assert am.data == {}

        am.kick_member(member)
        assert am.data == {}

    def test_update_member(self, member):
        member.last_name = 'test1'
        am = AttributeManager(self.description, [])

        am.register_member(member)
        assert am.data == {'test1': {member}}

        member.last_name = 'test2'
        am.update_member(member)
        assert am.data == {'test2': {member}}

    def test_distinct_values_for_member_no_attr(self, member):
        am = AttributeManager(self.description, [])
        bm = AttributeManager('first_name', [])

        assert am.distinct_values_for_member(bm, Member(1)) == set()

    def test_distinct_values_for_member(self, member):
        am = AttributeManager(self.description, [])
        bm = AttributeManager('first_name', [])

        for i in range(10):
            am.register_member(Member(i, first_name='a', last_name='b'))

        assert am.distinct_values_for_member(bm, Member(100, first_name='a',
                                                        last_name='b')) == set()
        assert am.distinct_values_for_member(bm, Member(100, first_name='c',
                                                        last_name='b')) == set()

        for i in range(5):
            am.register_member(Member(i + 10, first_name=str(i), last_name='b'))

        assert am.distinct_values_for_member(bm, Member(100, first_name='a',
                                                        last_name='b')) == set()
        assert am.distinct_values_for_member(bm, Member(100, first_name='c',
                                                        last_name='b')) == set()

        for i in range(5):
            am.register_member(Member(i + 20, first_name='a', last_name=str(i)))

        assert am.distinct_values_for_member(bm, Member(100, first_name='a',
                                                        last_name='b')) == set()
        assert am.distinct_values_for_member(bm,
                                             Member(100, first_name='c',
                                                    last_name='b')) == {'0', '1', '2', '3', '4'}

    def test_unique_attributes_of(self, member):
        member.instruments = [Tuba(), Trombone()]
        am = AttributeManager('instruments', [])
        am.register_member(member)
        am.register_member(Member(5, instruments=[Tuba()]))
        assert am.unique_attributes_of(member) == [Trombone()]

        bm = AttributeManager('age', [])
        assert bm.unique_attributes_of(member) == []

    def test_available_members(self, member):
        am = AttributeManager(self.description, [])

        for i in range(10):
            am.register_member(Member(user_id=i, last_name=str(i)))

        assert am.available_members == frozenset(Member(i) for i in range(10))

    def test_is_hintable_with_member(self):
        am = AttributeManager(self.description, [])
        bm = AttributeManager('first_name', [])

        for i in range(10):
            am.register_member(Member(i, first_name='a', last_name='b'))

        assert not bm.is_hintable_with_member(am, Member(100, first_name='a', last_name='b'))
        assert not bm.is_hintable_with_member(am, Member(100, first_name='c', last_name='b'))

        for i in range(5):
            am.register_member(Member(i + 10, first_name=str(i), last_name='b'))

        assert not bm.is_hintable_with_member(am, Member(100, first_name='a', last_name='b'))
        assert not bm.is_hintable_with_member(am, Member(100, first_name='c', last_name='b'))

        for i in range(5):
            am.register_member(Member(i + 20, first_name='a', last_name=str(i)))

        assert not bm.is_hintable_with_member(am, Member(100, first_name='a', last_name='b'))
        assert bm.is_hintable_with_member(am, Member(100, first_name='c', last_name='b'))

    def test_is_hintable_with_member_free_text(self):
        am = AttributeManager(self.description, [])
        bm = AttributeManager('first_name', [])

        for i in range(10):
            am.register_member(Member(i, first_name='a', last_name='b'))
            bm.register_member(Member(i, first_name='a', last_name='b'))

        assert not bm.is_hintable_with_member(
            am, Member(100, first_name='a', last_name='b'), multiple_choice=False)

        member = Member(100, first_name='c', last_name='b')
        am.register_member(member)
        bm.register_member(member)
        assert bm.is_hintable_with_member(am, member, multiple_choice=False)

    @pytest.mark.parametrize('multiple_choice', [True, False])
    def test_is_hintable_with(self, dummy_am, multiple_choice):
        am = AttributeManager('last_name', [])
        assert not am.is_hintable_with(dummy_am, multiple_choice=False)

        am = AttributeManager('last_name', ['first_name'])
        bm = AttributeManager('first_name', [])

        member = Member(1, last_name='last_name')
        am.register_member(member)
        bm.register_member(member)
        member = Member(2, first_name='first_name')
        am.register_member(member)
        bm.register_member(member)

        assert not am.is_hintable_with(bm, multiple_choice=multiple_choice)

        for i in range(3, 10):
            member = Member(i, first_name='a', last_name='b')
            am.register_member(member)
            bm.register_member(member)

        assert not am.is_hintable_with(bm, multiple_choice=multiple_choice)

        for i in [42, 43, 44, 45]:
            member = Member(i, first_name=str(i), last_name='b')
            am.register_member(member)
            bm.register_member(member)

        assert not am.is_hintable_with(bm, multiple_choice=multiple_choice)

        member = Member(100, first_name='7', last_name='8')
        am.register_member(member)
        bm.register_member(member)

        assert am.is_hintable_with(bm, multiple_choice=multiple_choice)
        assert not am.is_hintable_with(
            bm, multiple_choice=multiple_choice, exclude_members=[Member(100)])

    def test_draw_hint_member_errors(self, dummy_am):
        am = AttributeManager(self.description, [])
        with pytest.raises(ValueError, match=f'is not a valid question for {self.description}'):
            am.draw_hint_member(dummy_am)

        am = AttributeManager(self.description, [dummy_am])
        with pytest.raises(RuntimeError, match=f'currently not hintable for dummy'):
            am.draw_hint_member(dummy_am)

    @pytest.mark.parametrize('runs', list(range(10)))
    def test_draw_hint_member(self, runs):
        am = AttributeManager(self.description, ['first_name'])
        bm = AttributeManager('first_name', [])

        for i in range(4):
            member = Member(i, first_name=str(i), last_name=str(i))
            am.register_member(member)
            bm.register_member(member)

            member = Member(i + 10, first_name=str(i))
            am.register_member(member)
            bm.register_member(member)

            member = Member(i + 20, last_name=str(i))
            am.register_member(member)
            bm.register_member(member)

        member = am.draw_hint_member(bm, exclude_members=[Member(0)])
        assert member != Member(0)
        assert member.last_name and member.first_name
        assert member in am.available_members
        assert member in bm.available_members
        assert am.is_hintable_with_member(bm, member)
        assert len(bm.distinct_values_for_member(am, member)) >= 3

    def test_draw_hint_member_free_text(self):
        am = AttributeManager(self.description, ['first_name'])
        bm = AttributeManager('first_name', [])

        for i in range(4):
            member = Member(i, first_name=str(i), last_name=str(i))
            am.register_member(member)
            bm.register_member(member)

            member = Member(i + 10, first_name=str(i))
            am.register_member(member)
            bm.register_member(member)

            member = Member(i + 20, last_name=str(i))
            am.register_member(member)
            bm.register_member(member)

        member = Member(100, first_name='A', last_name='B')
        am.register_member(member)
        bm.register_member(member)

        member = am.draw_hint_member(bm, multiple_choice=False)
        assert member.last_name and member.first_name
        assert member in am.available_members
        assert member in bm.available_members
        assert am.is_hintable_with_member(bm, member, multiple_choice=False)
        assert len(am.unique_attributes_of(member)) >= 1

    def test_draw_question_attributes_error(self):
        am = AttributeManager(self.description, [])
        bm = AttributeManager(self.description, [])
        with pytest.raises(RuntimeError,
                           match=f'Given member has no attribute {self.description}'):
            am.draw_question_attributes(bm, Member(1))

    def test_draw_question_attributes(self):
        am = AttributeManager(self.description, [])
        bm = AttributeManager('first_name', [])

        for i in range(100):
            am.register_member(
                Member(i,
                       first_name=random.choice(['1', '2', '3', '4', '5']),
                       last_name=random.choice(['a', 'b', 'c', 'd', 'e'])))

        for i, name in enumerate(['a', 'b', 'c', 'd', 'e']):
            with pytest.raises(RuntimeError, match='is not hintable for attribute'):
                attrs, idx = am.draw_question_attributes(
                    bm, Member(1000, first_name=str(i + 1), last_name=name))
        for i, name in enumerate(['a', 'b', 'c', 'd', 'e']):
            attrs, idx = am.draw_question_attributes(
                bm, Member(1000, first_name=str(i + 10), last_name=name))
            assert len(set(attrs)) == 4
            assert attrs[idx] == name
            for a in attrs:
                assert a in ['a', 'b', 'c', 'd', 'e']

    def test_build_question_with_errors(self, dummy_am):
        am = AttributeManager(self.description, [])
        with pytest.raises(ValueError, match=f'is not a valid question for {self.description}'):
            am.build_question_with(dummy_am)

        am = AttributeManager(self.description, [dummy_am])
        with pytest.raises(RuntimeError, match=f'currently not hintable for dummy'):
            am.build_question_with(dummy_am)

    @pytest.mark.parametrize('runs', list(range(10)))
    def test_build_question(self, runs):
        am = AttributeManager(self.description, ['first_name'])
        bm = AttributeManager('first_name', [])

        for i in range(4):
            member = Member(i, first_name='A', last_name='B')
            am.register_member(member)
            bm.register_member(member)

        with pytest.raises(RuntimeError, match=f'currently not hintable for first_name'):
            am.build_question_with(bm)

        for i in range(250):
            member = Member(i + 10,
                            first_name=random.choice(['1', '2', '3', '4', '5']),
                            last_name=random.choice(['a', 'b', 'c', 'd', 'e']))
            am.register_member(member)
            bm.register_member(member)

        member, attr, opts, idx = am.build_question_with(bm, exclude_members=[Member(0)])
        assert member != Member(0)
        assert attr in am.data
        assert member in am.available_members
        assert member in bm.available_members
        for first_name in set(opts).difference({opts[idx]}):
            assert not any(
                am.get_members_attribute(m) == attr and bm.get_members_attribute(m) == first_name
                for m in bm.available_members)
        assert attr == 'B'
        assert len(set(opts)) == 4

    def test_build_question_free_text(self):
        am = AttributeManager(self.description, ['first_name'])
        bm = AttributeManager('first_name', [])

        for i in range(4):
            member = Member(i, first_name='A', last_name='B')
            am.register_member(member)
            bm.register_member(member)

        with pytest.raises(RuntimeError, match=f'currently not hintable for first_name'):
            am.build_question_with(bm, multiple_choice=False)

        member = Member(100, first_name='100', last_name='200')
        am.register_member(member)
        bm.register_member(member)

        member, attr, correct = am.build_question_with(bm, multiple_choice=False)
        assert attr in am.data
        assert member in am.available_members
        assert member in bm.available_members
        assert len(am.data[attr]) == 1
        assert attr == '200'
        assert correct == bm.get_members_attribute(member)

    def test_build_question_list_as_hint(self):
        am = AttributeManager('instruments', ['first_name'])
        bm = AttributeManager('first_name', [])

        allowed = [Trumpet(), Drums(), Bassoon(), Clarinet(), Horn(), Flute()]

        for i in range(4):
            member = Member(i, first_name='A', instruments=[Tuba(), Trombone()])
            am.register_member(member)
            bm.register_member(member)

        with pytest.raises(RuntimeError, match=f'currently not hintable for first_name'):
            am.build_question_with(bm)

        for i in range(100):
            member = Member(i + 10,
                            first_name=random.choice(['1', '2', '3', '4', '5']),
                            instruments=random.sample(allowed, random.randint(1, 4)))
            am.register_member(member)
            bm.register_member(member)

        member, attr, opts, idx = am.build_question_with(bm)
        assert attr in am.data
        assert attr in [Tuba(), Trombone()]
        assert len(set(opts)) == 4
        assert member in am.available_members
        assert member in bm.available_members
        for first_name in set(opts).difference({opts[idx]}):
            assert not any(
                attr in am.get_members_attribute(m) and bm.get_members_attribute(m) == first_name
                for m in bm.available_members)

    def test_build_question_list_as_question(self):
        am = AttributeManager('first_name', ['instruments'])
        bm = AttributeManager('instruments', [])

        allowed = [Trumpet(), Drums(), Bassoon(), Clarinet(), Horn(), Flute()]

        for i in range(4):
            member = Member(i, first_name='A', instruments=[Tuba(), Trombone()])
            am.register_member(member)
            bm.register_member(member)

        with pytest.raises(RuntimeError, match=f'currently not hintable for instruments'):
            am.build_question_with(bm)

        for i in range(100):
            member = Member(i + 10,
                            first_name=random.choice(['1', '2', '3', '4', '5']),
                            instruments=random.sample(allowed, random.randint(1, 4)))
            am.register_member(member)
            bm.register_member(member)

        member, attr, opts, idx = am.build_question_with(bm)
        assert attr in am.data
        assert attr == 'A'
        assert len(set(opts)) == 4
        assert member in am.available_members
        assert member in bm.available_members
        for instrument in set(opts).difference({opts[idx]}):
            assert not any(
                attr == am.get_members_attribute(m) and instrument in bm.get_members_attribute(m)
                for m in bm.available_members)


class TestNameManager:
    description = 'first_name'

    def test_init(self, member, dummy_am):
        am = NameManager(self.description, [dummy_am])
        member.first_name = 'test'
        assert am.description == self.description
        assert am.questionable_attributes == [dummy_am]
        assert am.male_data == {}
        assert am.female_data == {}
        assert am.get_members_attribute(member) == 'test'
        member.gender = Gender.MALE
        assert am.get_members_attribute(member) == 'test'

    def test_register_member_without_attribute(self, member):
        am = NameManager(self.description, [])
        am.register_member(member)
        assert am.male_data == {}
        assert am.female_data == {}

    def test_register_member_without_gender(self, member):
        member.first_name = 'test'
        am = NameManager(self.description, [])
        am.register_member(member)
        assert am.male_data == {}
        assert am.female_data == {}

    def test_register_female_member(self, member):
        member.first_name = 'test1'
        member.gender = Gender.FEMALE
        am = NameManager(self.description, [])

        am.register_member(member)
        assert am.male_data == {}
        assert am.female_data == {'test1': {member}}
        assert all(member is not m for m in am.female_data['test1'])

        member2 = Member(2, first_name='test2', gender=Gender.FEMALE)
        am.register_member(member2)
        assert am.male_data == {}
        assert am.female_data == {'test1': {member}, 'test2': {member2}}
        assert (member2 is not m for m in am.female_data['test2'])

        member3 = Member(4, first_name='test1', gender=Gender.FEMALE)
        am.register_member(member3)
        assert am.male_data == {}
        assert am.female_data == {'test1': {member, member3}, 'test2': {member2}}
        assert all(member3 is not m for m in am.female_data['test1'])

    def test_register_male_member(self, member):
        member.first_name = 'test1'
        member.gender = Gender.MALE
        am = NameManager(self.description, [])

        am.register_member(member)
        assert am.female_data == {}
        assert am.male_data == {'test1': {member}}
        assert all(member is not m for m in am.male_data['test1'])

        member2 = Member(2, first_name='test2', gender=Gender.MALE)
        am.register_member(member2)
        assert am.female_data == {}
        assert am.male_data == {'test1': {member}, 'test2': {member2}}
        assert (member2 is not m for m in am.male_data['test2'])

        member3 = Member(4, first_name='test1', gender=Gender.MALE)
        am.register_member(member3)
        assert am.female_data == {}
        assert am.male_data == {'test1': {member, member3}, 'test2': {member2}}
        assert all(member3 is not m for m in am.male_data['test1'])

    def test_double_register(self, member):
        member.first_name = 'test'
        member.gender = Gender.MALE
        am = NameManager(self.description, [])

        am.register_member(member)
        with pytest.raises(RuntimeError, match='Member is already registered.'):
            am.register_member(Member(user_id=123456, first_name='test1'))

    @pytest.mark.parametrize('gender', [Gender.MALE, Gender.FEMALE])
    def test_kick_member(self, member, gender):
        member.first_name = 'test'
        member.gender = gender
        am = NameManager(self.description, [])

        am.register_member(member)
        data = am.male_data if gender == Gender.MALE else am.female_data
        assert data == {'test': {member}}

        am.kick_member(member)
        assert data == {}

        am.kick_member(member)
        assert data == {}

    def test_distinct_values_for_member_no_attr(self, member):
        am = NameManager(self.description, [])
        bm = AttributeManager('last_name', [])

        assert am.distinct_values_for_member(bm, Member(1)) == set()

    @pytest.mark.parametrize('gender,other_gender', [(Gender.MALE, Gender.FEMALE),
                                                     (Gender.FEMALE, Gender.MALE)])
    def test_distinct_values_for_member(self, member, gender, other_gender):
        am = NameManager(self.description, [])
        bm = AttributeManager('last_name', [], gendered_questions=True)

        for i in range(10):
            am.register_member(Member(i, last_name='a', first_name='b', gender=gender))

        for g in [None, gender, other_gender]:
            assert am.distinct_values_for_member(
                bm, Member(100, last_name='a', first_name='b', gender=g)) == set()
            assert am.distinct_values_for_member(
                bm, Member(100, last_name='c', first_name='b', gender=g)) == set()

        for i in range(5):
            am.register_member(Member(i + 10, last_name=str(i), first_name='b', gender=gender))

        for g in [None, gender, other_gender]:
            assert am.distinct_values_for_member(
                bm, Member(100, last_name='a', first_name='b', gender=g)) == set()
            assert am.distinct_values_for_member(
                bm, Member(100, last_name='c', first_name='b', gender=g)) == set()

        for i in range(5):
            am.register_member(Member(i + 20, last_name='a', first_name=str(i), gender=gender))

        assert am.distinct_values_for_member(
            bm, Member(100, last_name='a', first_name='b', gender=gender)) == set()
        assert am.distinct_values_for_member(
            bm, Member(100, last_name='c', first_name='b',
                       gender=gender)) == {'0', '1', '2', '3', '4'}
        assert am.distinct_values_for_member(
            bm, Member(100, last_name='a', first_name='b', gender=other_gender)) == set()
        assert am.distinct_values_for_member(
            bm, Member(100, last_name='c', first_name='b', gender=other_gender)) == set()

    @pytest.mark.parametrize('gender,other_gender', [(Gender.MALE, Gender.FEMALE),
                                                     (Gender.FEMALE, Gender.MALE)])
    def test_distinct_values_for_member_full_name(self, member, gender, other_gender):
        am = NameManager('full_name', [])
        bm = AttributeManager('instruments', [], gendered_questions=True)

        for i in range(10):
            am.register_member(Member(i, last_name='a', instruments=[Tuba()]))

        for g in [None, gender, other_gender]:
            assert am.distinct_values_for_member(
                bm, Member(100, last_name='a', instruments=[Tuba()], gender=g)) == set()
            assert am.distinct_values_for_member(
                bm, Member(100, last_name='c', instruments=[Tuba()], gender=g)) == set()

        am.register_member(Member(200, last_name='A', instruments=[Trumpet()]))
        assert am.distinct_values_for_member(
            bm, Member(200, last_name='A', instruments=[Trumpet()], gender=gender)) == set()
        assert am.distinct_values_for_member(bm, Member(200,
                                                        last_name='A',
                                                        instruments=[Trumpet()])) == {'a'}

    def test_unique_attributes_of(self, member):
        member.first_name = 'test'
        member.gender = Gender.MALE

        am = NameManager(self.description, [])
        am.register_member(member)
        am.register_member(Member(1, first_name='test', gender=Gender.MALE))
        assert am.unique_attributes_of(member) == []

        member = Member(2, first_name='test', gender=Gender.FEMALE)
        am.register_member(member)
        assert am.unique_attributes_of(member) == []

        member = Member(3, first_name='test1', gender=Gender.FEMALE)
        am.register_member(member)
        assert am.unique_attributes_of(member) == ['test1']

    @pytest.mark.parametrize('gender', [Gender.MALE, Gender.FEMALE])
    def test_build_question(self, gender):
        bm = NameManager(self.description, ['last_name'])
        am = AttributeManager('last_name', ['first_name'], gendered_questions=True)

        for i in range(4):
            member = Member(i, last_name='A', first_name='B', gender=gender)
            am.register_member(member)
            bm.register_member(member)

        with pytest.raises(RuntimeError, match=f'currently not hintable for first_name'):
            am.build_question_with(bm)

        for i in range(100):
            member = Member(i + 10,
                            first_name=random.choice(['1', '2', '3', '4', '5']),
                            last_name=random.choice(['a', 'b', 'c', 'd', 'e']),
                            gender=Gender.MALE)
            am.register_member(member)
            bm.register_member(member)
        for i in range(100):
            member = Member(i + 120,
                            first_name=random.choice(['6', '7', '8', '9', '10']),
                            last_name=random.choice(['f', 'g', 'h', 'i', 'j']),
                            gender=Gender.FEMALE)
            am.register_member(member)
            bm.register_member(member)

        member, attr, opts, idx = am.build_question_with(bm)
        assert attr in am.data
        assert member in am.available_members
        assert member in bm.available_members
        for last_name in set(opts).difference({opts[idx]}):
            assert not any(
                am.get_members_attribute(m) == attr and bm.get_members_attribute(m) == last_name
                for m in bm.available_members)
        assert attr == 'A'
        assert len(set(opts)) == 4
        for o in opts:
            if gender == Gender.MALE:
                assert o in ['1', '2', '3', '4', '5', 'B']
            else:
                assert o in ['6', '7', '8', '9', '10', 'B']

    @pytest.mark.parametrize('gender', [Gender.MALE, Gender.FEMALE])
    def test_build_question_free_text(self, gender):
        bm = NameManager(self.description, ['last_name'])
        am = AttributeManager('last_name', ['first_name'])

        for i in range(4):
            member = Member(i, last_name='A', first_name='B', gender=gender)
            am.register_member(member)
            bm.register_member(member)

        with pytest.raises(RuntimeError, match=f'currently not hintable for last_name'):
            bm.build_question_with(am, multiple_choice=False)

        member = Member(100, first_name='100', last_name='200', gender=gender)
        am.register_member(member)
        bm.register_member(member)

        member, attr, correct = bm.build_question_with(am, multiple_choice=False)
        data = bm.female_data if member.gender == Gender.FEMALE else bm.male_data
        assert attr in data
        assert member in am.available_members
        assert member in bm.available_members
        assert attr == '100'
        assert correct == am.get_members_attribute(member)


class TestChangingAttributeManager:

    def test_init(self):
        am = ChangingAttributeManager('age', [])
        assert am.data == {}

    def test_register_kick_update(self, member, monkeypatch):
        mock_date = dtm.date(2020, 9, 5)

        class DateTime:

            @classmethod
            def now(cls, *args, **kwargs):
                return mock_date

        monkeypatch.setattr(dtm, 'datetime', DateTime)

        am = ChangingAttributeManager('age', [])
        member.date_of_birth = dtm.date(1996, 10, 8)
        am.register_member(member)

        assert am.data == {23: {member}}

        member.date_of_birth = dtm.date(1996, 3, 16)
        am.update_member(member)

        assert am.data == {24: {member}}

        am.kick_member(member)

        assert am.data == {}

    def test_caching(self, member, monkeypatch):
        mock_date = dtm.date(2020, 9, 5)
        mock_date_2 = dtm.date(2020, 10, 8)
        member.date_of_birth = dtm.date(1996, 10, 8)

        class Date:

            @classmethod
            def today(cls, *args, **kwargs):
                return mock_date

        monkeypatch.setattr(dtm, 'date', Date)

        am = ChangingAttributeManager('age', [])
        am.register_member(member)

        assert am.data == {23: {member}}

        class Date2:

            @classmethod
            def today(cls, *args, **kwargs):
                return mock_date_2

        monkeypatch.setattr(dtm, 'date', Date2)

        assert am.data == {24: {member}}

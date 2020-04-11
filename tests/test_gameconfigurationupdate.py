#!/usr/bin/env python
import pytest

from components import Question, GameConfigurationUpdate


class TestGameConfigurationUpdate:
    chat_id = 1234
    multiple_choice = False
    question_attributes = [Question.AGE, Question.BIRTHDAY]
    hint_attributes = [Question.FIRST_NAME, Question.NICKNAME]
    number_of_questions = 42

    def test_init(self):
        gcu = GameConfigurationUpdate(chat_id=self.chat_id,
                                      multiple_choice=self.multiple_choice,
                                      question_attributes=self.question_attributes,
                                      hint_attributes=self.hint_attributes,
                                      number_of_questions=self.number_of_questions)
        assert gcu.chat_id == self.chat_id
        assert gcu.multiple_choice == self.multiple_choice
        assert gcu.question_attributes == self.question_attributes
        assert gcu.hint_attributes == self.hint_attributes
        assert gcu.number_of_questions == self.number_of_questions

    def test_attributes_error(self):
        with pytest.raises(ValueError, match='interesting game'):
            GameConfigurationUpdate(chat_id=self.chat_id,
                                    multiple_choice=self.multiple_choice,
                                    question_attributes=['abc'],
                                    hint_attributes=['abc'],
                                    number_of_questions=self.number_of_questions)

    def test_unsupported_attributes(self):
        with pytest.raises(ValueError, match='in question_attributes'):
            GameConfigurationUpdate(chat_id=self.chat_id,
                                    multiple_choice=self.multiple_choice,
                                    question_attributes=['abc', 'def'],
                                    hint_attributes=self.hint_attributes,
                                    number_of_questions=self.number_of_questions)
        with pytest.raises(ValueError, match='in hint_attributes'):
            GameConfigurationUpdate(chat_id=self.chat_id,
                                    multiple_choice=self.multiple_choice,
                                    question_attributes=self.question_attributes,
                                    hint_attributes=['abc', 'def'],
                                    number_of_questions=self.number_of_questions)
        with pytest.raises(ValueError, match='full name hints'):
            GameConfigurationUpdate(chat_id=self.chat_id,
                                    multiple_choice=self.multiple_choice,
                                    question_attributes=[Question.ADDRESS],
                                    hint_attributes=[Question.AGE],
                                    number_of_questions=self.number_of_questions)

    def test_simplenamespace_inheritance(self):
        gcu = GameConfigurationUpdate(chat_id=self.chat_id,
                                      multiple_choice=self.multiple_choice,
                                      question_attributes=self.question_attributes,
                                      hint_attributes=self.hint_attributes,
                                      number_of_questions=self.number_of_questions)

        assert gcu.__dict__ == {
            'chat_id': self.chat_id,
            'multiple_choice': self.multiple_choice,
            'question_attributes': self.question_attributes,
            'hint_attributes': self.hint_attributes,
            'number_of_questions': self.number_of_questions
        }
        assert dir(gcu) == sorted([
            'multiple_choice', 'question_attributes', 'hint_attributes', 'number_of_questions',
            'chat_id'
        ])

        gcu.new_attribute = 7
        assert gcu.__dict__ == {
            'chat_id': self.chat_id,
            'multiple_choice': self.multiple_choice,
            'question_attributes': self.question_attributes,
            'hint_attributes': self.hint_attributes,
            'number_of_questions': self.number_of_questions,
            'new_attribute': 7
        }
        assert dir(gcu) == sorted([
            'multiple_choice', 'question_attributes', 'hint_attributes', 'number_of_questions',
            'new_attribute', 'chat_id'
        ])

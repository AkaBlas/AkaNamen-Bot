#!/usr/bin/env python
import pytest
from telegram import InlineKeyboardMarkup
import datetime
from bot import keyboards
from components import Instrument, Tuba, Trombone, LowBrassInstrument, Guitar, Orchestra, Member


class TestKeyboards:

    def test_build_instruments_keyboard(self, bot, chat_id):
        message = bot.send_message(chat_id=chat_id,
                                   text='test_message',
                                   reply_markup=keyboards.build_instruments_keyboard())
        assert isinstance(message.reply_markup, InlineKeyboardMarkup)
        for row in message.reply_markup.inline_keyboard[:-1]:
            for button in row:
                instrument, selection = button.text.split(' ')
                assert isinstance(Instrument.from_string(instrument), Instrument)
                assert selection == keyboards.DESELECTED
                instrument, selection = button.callback_data.split(' ')
                assert isinstance(Instrument.from_string(instrument), Instrument)
                assert selection == keyboards.DESELECTED
        assert len(message.reply_markup.inline_keyboard[-1]) == 1
        button = message.reply_markup.inline_keyboard[-1][0]
        assert button.text == keyboards.NEXT_TEXT
        assert button.callback_data == keyboards.NEXT_DATA

    def test_build_instruments_keyboard_with_arg(self, bot, chat_id):
        selection = {Tuba(): True, Trombone(): False}
        message = bot.send_message(chat_id=chat_id,
                                   text='test_message',
                                   reply_markup=keyboards.build_instruments_keyboard(selection))
        assert isinstance(message.reply_markup, InlineKeyboardMarkup)
        for row in message.reply_markup.inline_keyboard[:-1]:
            for button in row:
                instrument, sel = button.text.split(' ')
                expected = (keyboards.SELECTED if selection.get(Instrument.from_string(instrument))
                            else keyboards.DESELECTED)
                assert isinstance(Instrument.from_string(instrument), Instrument)
                assert sel == expected
                instrument, sel = button.callback_data.split(' ')
                assert isinstance(Instrument.from_string(instrument), Instrument)
                assert sel == expected
        assert len(message.reply_markup.inline_keyboard[-1]) == 1
        button = message.reply_markup.inline_keyboard[-1][0]
        assert button.text == keyboards.NEXT_TEXT
        assert button.callback_data == keyboards.NEXT_DATA

    def test_parse_instruments_keyboard(self, bot, chat_id):
        selection = {
            Tuba(): True,
            Trombone(): True,
            LowBrassInstrument(): True,
            Guitar(): True,
        }
        message = bot.send_message(chat_id=chat_id,
                                   text='test_message',
                                   reply_markup=keyboards.build_instruments_keyboard(selection))
        result = keyboards.parse_instruments_keyboard(message.reply_markup)
        for instrument, sel in result.items():
            assert sel == selection.get(instrument, False)

    def test_build_questions_hints_keyboard_errors(self):
        with pytest.raises(ValueError, match='Exactly one'):
            keyboards.build_questions_hints_keyboard(Orchestra(), True, True)
        with pytest.raises(ValueError, match='Exactly one'):
            keyboards.build_questions_hints_keyboard(Orchestra())
        with pytest.raises(RuntimeError, match='has no questionable attributes'):
            keyboards.build_questions_hints_keyboard(Orchestra(), True)

    @pytest.mark.parametrize('populated_orchestra', [{}], indirect=True)
    def test_build_questions_hints_keyboard(self, bot, chat_id, populated_orchestra):
        message = bot.send_message(chat_id=chat_id,
                                   text='test_message',
                                   reply_markup=keyboards.build_questions_hints_keyboard(
                                       populated_orchestra, True))
        assert isinstance(message.reply_markup, InlineKeyboardMarkup)
        for row in message.reply_markup.inline_keyboard[:-1]:
            for button in row:
                option, selection = button.text.rsplit(' ', 1)
                assert option in Orchestra.DICTS_TO_HR.values()
                assert selection == keyboards.DESELECTED
                option, selection = button.callback_data.split(' ')
                assert option in Orchestra.DICTS_TO_HR.keys()
                assert selection == keyboards.DESELECTED
        assert len(message.reply_markup.inline_keyboard[-1]) == 1
        button = message.reply_markup.inline_keyboard[-1][0]
        assert button.text == keyboards.NEXT_TEXT
        assert button.callback_data == keyboards.NEXT_DATA

    @pytest.mark.parametrize('populated_orchestra', [{}], indirect=True)
    def test_build_questions_hints_keyboard_with_selection(self, bot, chat_id,
                                                           populated_orchestra):
        selection = {'first_name': True, 'age': False}
        message = bot.send_message(chat_id=chat_id,
                                   text='test_message',
                                   reply_markup=keyboards.build_questions_hints_keyboard(
                                       populated_orchestra, True))
        assert isinstance(message.reply_markup, InlineKeyboardMarkup)
        for row in message.reply_markup.inline_keyboard[:-1]:
            for button in row:
                option, sel = button.text.rsplit(' ', 1)
                expected = (keyboards.SELECTED if selection.get(option) else keyboards.DESELECTED)
                assert option in Orchestra.DICTS_TO_HR.values()
                assert sel == expected
                option, sel = button.callback_data.split(' ')
                assert option in Orchestra.DICTS_TO_HR.keys()
                assert sel == expected
        assert len(message.reply_markup.inline_keyboard[-1]) == 1
        button = message.reply_markup.inline_keyboard[-1][0]
        assert button.text == keyboards.NEXT_TEXT
        assert button.callback_data == keyboards.NEXT_DATA

    @pytest.mark.parametrize('populated_orchestra', [{'skip': ['date_of_birth']}], indirect=True)
    def test_build_questions_hints_keyboard_missing_attrs(self, bot, chat_id, populated_orchestra):
        message = bot.send_message(chat_id=chat_id,
                                   text='test_message',
                                   reply_markup=keyboards.build_questions_hints_keyboard(
                                       populated_orchestra, question=True))
        assert 'Alter' not in [
            b.text.rsplit(' ', 1)[0] for row in message.reply_markup.inline_keyboard for b in row
        ]

        message = bot.send_message(chat_id=chat_id,
                                   text='test_message',
                                   reply_markup=keyboards.build_questions_hints_keyboard(
                                       populated_orchestra, hint=True))
        assert 'Alter' not in [
            b.text.rsplit(' ', 1)[0] for row in message.reply_markup.inline_keyboard for b in row
        ]

        populated_orchestra.register_member(
            Member(-15, date_of_birth=datetime.date(1996, 8, 8), first_name='Kyle'))

        message = bot.send_message(chat_id=chat_id,
                                   text='test_message',
                                   reply_markup=keyboards.build_questions_hints_keyboard(
                                       populated_orchestra, question=True))
        assert 'Alter' not in [
            b.text.rsplit(' ', 1)[0] for row in message.reply_markup.inline_keyboard for b in row
        ]

        message = bot.send_message(chat_id=chat_id,
                                   text='test_message',
                                   reply_markup=keyboards.build_questions_hints_keyboard(
                                       populated_orchestra, hint=True))
        assert 'Alter' in [
            b.text.rsplit(' ', 1)[0] for row in message.reply_markup.inline_keyboard for b in row
        ]

    @pytest.mark.parametrize('populated_orchestra', [{'skip': ['date_of_birth']}], indirect=True)
    def test_parse_questions_hints_keyboard(self, bot, chat_id, populated_orchestra):
        selection = {
            'first_names': True,
            'ages': True,
            'nicknames': True,
        }
        message = bot.send_message(
            chat_id=chat_id,
            text='test_message',
            reply_markup=keyboards.build_questions_hints_keyboard(populated_orchestra,
                                                                  hint=True,
                                                                  current_selection=selection))
        result = keyboards.parse_questions_hints_keyboard(message.reply_markup)
        for option, sel in result.items():
            assert sel == selection.get(option, False)

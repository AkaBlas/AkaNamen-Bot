#!/usr/bin/env python
from telegram import InlineKeyboardMarkup

from bot import keyboards
from components import Instrument, Tuba, Trombone, LowBrassInstrument, Guitar


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

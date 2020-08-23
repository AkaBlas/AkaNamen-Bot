#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains classes and functions for playing the game."""
from dataclasses import dataclass, field
from threading import Lock
from typing import Optional, List, cast, Dict, Union

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackContext, Handler, \
    CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from bot import ORCHESTRA_KEY, GAME_KEY, parse_questions_hints_keyboard, \
    build_questions_hints_keyboard, SELECTED, DONE
from components import Questioner, Member

# States of the conversation

HINT_ATTRIBUTES = 'HINT_ATTRIBUTES'
""":obj:`str`: Identifier of the state in which the hint attributes are selected."""
QUESTION_ATTRIBUTES = 'QUESTION_ATTRIBUTES'
""":obj:`str`: Identifier of the state in which the question attributes are selected."""
NUMBER_QUESTIONS = 'NUMBER_QUESTIONS'
""":obj:`str`: Identifier of the state in which the number of question attributes is selected."""
MULTIPLE_CHOICE = 'Multiple Choice'
""":obj:`str`: Identifier of the state in the type of questions is seleted.."""
GAME = 'GAME'
""":obj:`str`: Identifier of the state in which the questions are asked and answered."""

# Texts
TEXTS: Dict[str, str] = {
    HINT_ATTRIBUTES: 'Juhu, ein Spiel! Bitte wähle zunächst aus, welche Eigenschaften eines '
                     'AkaBlasen als Hinweis gegeben werden können. Um die Auswahl zu ändern, '
                     'klicke auf die Felder.\n\nWenn Du fertig bist, klicke unten auf '
                     '<i>Weiter</i>.',
    QUESTION_ATTRIBUTES: 'Alaska. Bitte wähle nun aus, nach welchen Eigenschaften eines '
                         'AkaBlasen Du gefragt wirst. Um die Auswahl zu ändern, klicke auf die '
                         'Felder.\n\nWenn Du fertig bist, klicke unten auf <i>Weiter</i>.',
    NUMBER_QUESTIONS: 'Supidupi. Wie viele Fragen möchtest Du insgesamt erhalten?',
    MULTIPLE_CHOICE: 'Schließlich kannst Du noch aussuchen, ob Du Multiple-Choice- oder '
                     'Freitext-Fragen bekommst.\n\n<i>⚠️ Hinweis:</i> Den Freitext-Modus '
                     'solltest Du nur wählen, wann Du schon ziemlich gut bist. Bedenke außerdem, '
                     'dass der Freitext-Modus ein bisschen experimentell ist. Mehr Informationen '
                     'dazu gibt es in den <a '
                     'href="https://bibo-joshi.github.io/AkaNamen-Bot/faq.html#meine-freitext'
                     '-antwort-wurde-als-falsch-gewertet-obwohl-da-nur-in-tippfehler-drin-war'
                     '-was-ist-da-los">FAQ</a>.',
}
"""Dict[:obj:`str`,:obj:`str`]: Texts for the different states."""

# Keyboards
FREE_TEXT = 'Freitext'
NUMBER_QUESTIONS_KEYBOARD = InlineKeyboardMarkup.from_column(
    [InlineKeyboardButton(text=i, callback_data=str(i)) for i in [10, 25, 50, 100]])
""":class:`telegram.InlineKeyboardMarkup`: Keyboard for selection the number of questions."""
MULTIPLE_CHOICE_KEYBOARD = InlineKeyboardMarkup.from_row([
    InlineKeyboardButton(text=MULTIPLE_CHOICE, callback_data=str(True)),
    InlineKeyboardButton(text=FREE_TEXT, callback_data=str(False)),
])
""":class:`telegram.InlineKeyboardMarkup`: Keyboard for selection the type of questions."""

# ----------------------------------------------------------------------------------------------- #


@dataclass
class GameSettings:
    """
    A simple data class for storing the game settings made by a user.

    Attributes:
        hint_attributes (List[:obj:`str`]): Subset of the keys of
            :attr:`components.Orchestra.DICTS_TO_ATTRS`. These will be given as hints for the
            questions.
        question_attributes (List[:obj:`str`]): Subset of the keys of
            :attr:`components.Orchestra.DICTS_TO_ATTRS`. These will be asked for in the
            questions.
        number_of_questions (:obj:`int`): Number of questions to ask the user.
        multiple_choice (:obj:`bool`): Whether the question to be asked are multiple choice or free
            text.
        score (:class:`components.Score`): The score for this game.

    Args:
        hint_attributes: List of strings, appearing either in
            :attr:`components.Question.SUPPORTED_ATTRIBUTES` or as keys in
            :attr:`components.Orchestra.DICTS_TO_ATTRS`. These will be given as hints for the
            questions. May be empty, in which case all available attributes are allowed. Defaults
            to ``[]``.
        question_attributes: List of strings, appearing either in
            :attr:`components.Question.SUPPORTED_ATTRIBUTES` or as keys in
            :attr:`components.Orchestra.DICTS_TO_ATTRS`. These will be asked for in the
            questions. May be empty, in which case all available attributes are allowed. Defaults
            to ``[]``.
        number_of_questions: Number of questions to ask the user. Defaults to ``0``.
        multiple_choice: Whether the question to be asked are multiple choice or free text.
            Defaults to :obj:`True`.

    """
    number_of_questions: int = 0
    multiple_choice: bool = True
    hint_attributes: List[str] = field(default_factory=list)
    question_attributes: List[str] = field(default_factory=list)


class QuestionHandler(Handler):
    """
    A Handler that manages a collection of :class:`components.Questioner` instances for each user.
    """

    def __init__(self) -> None:
        super().__init__(self.callback)
        self._questioners: Dict[int, Questioner] = dict()
        self._questioners_lock = Lock()

    def set_questioner(self, user_id: int, questioner: Questioner) -> None:
        """
        Sets a new questioner for a user.

        Args:
            user_id: The ID of the user this questioner is associated with.
            questioner: The Questioner instance
        """
        with self._questioners_lock:
            self._questioners[user_id] = questioner

    def pop_questioner(self, user_id: int) -> Optional[Questioner]:
        """
        Pops questioner of a user.

        Args:
            user_id: The ID of the user.
        """
        with self._questioners_lock:
            return self._questioners.pop(user_id)

    def check_update(self, update: Update) -> bool:
        """
        Checks if the update is to be handled.

        Args:
            update: The update

        Returns:
            True: If the update is to be handled
            False: Otherwise.
        """
        user_id = update.effective_user.id
        with self._questioners_lock:
            if user_id in self._questioners and self._questioners[user_id].check_update(update):
                return True
        return False

    def callback(self, update: Update, context: CallbackContext) -> Union[str, int]:
        """
        Handles the update by passing it to the correct :class:`components.Questioner`. Also asks
        the next question or, if there is none, shows the result of the game and updates the users
        score.

        Args:
            update: The update.
            context: The context as provided by the :class:`telegram.ext.Dispatcher`.
        """
        user_id = update.effective_user.id
        with self._questioners_lock:
            questioner = self._questioners[user_id]
            questioner.handle_update(update)

            if questioner.number_of_questions_asked < questioner.number_of_questions:
                questioner.ask_question()
                return GAME
            else:
                correct = questioner.score.correct
                total = questioner.score.answers
                text = f'Das Spiel ist vorbei! {correct} von {total} Antworten waren richtig.'
                update.effective_user.send_message(text=text)

                orchestra = context.bot_data[ORCHESTRA_KEY]
                member = cast(Member, orchestra.members[user_id])
                member.user_score.add_to_score(total, correct)

                return ConversationHandler.END


# ----------------------------------------------------------------------------------------------- #

QUESTION_HANDLER = QuestionHandler()


def hint_attributes(update: Update, context: CallbackContext) -> Union[str, int]:
    """
    Starts the conversation and asks the user to select the hint attributes. Also parses the
    corresponding response.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`HINT_ATTRIBUTES`: If the user is not yet done selecting
        :attr:`QUESTION_ATTRIBUTES`: Else.
    """
    message = update.effective_message
    orchestra = context.bot_data[ORCHESTRA_KEY]

    if update.callback_query:
        data = update.callback_query.data
        update.callback_query.answer()
        if data == DONE:
            current_selection = parse_questions_hints_keyboard(message.reply_markup)
            game_settings = cast(GameSettings, context.user_data[GAME_KEY])
            game_settings.hint_attributes = [attr for attr, sl in current_selection.items() if sl]

            message.edit_text(text=TEXTS[QUESTION_ATTRIBUTES],
                              reply_markup=build_questions_hints_keyboard(orchestra=orchestra,
                                                                          question=True))
            return QUESTION_ATTRIBUTES
        else:
            current_selection = parse_questions_hints_keyboard(message.reply_markup)
            attr, selection = data.split(' ')
            current_selection[attr] = not (selection == SELECTED)

            message.edit_reply_markup(reply_markup=build_questions_hints_keyboard(
                orchestra=orchestra, hint=True, current_selection=current_selection))

            return HINT_ATTRIBUTES
    else:
        try:
            message.reply_text(TEXTS[HINT_ATTRIBUTES],
                               reply_markup=build_questions_hints_keyboard(orchestra=orchestra,
                                                                           hint=True))
            context.user_data[GAME_KEY] = GameSettings()
            return HINT_ATTRIBUTES
        except RuntimeError as e:
            if 'Orchestra currently has no questionable attributes.' == str(e):
                message.reply_text('Es sind leider noch nicht genug AkaBlasen angemeldet, um ein '
                                   'Spiel starten zu können. 😕 Bitte versuche es später erneut.')
                return ConversationHandler.END
            else:
                raise e


def question_attributes(update: Update, context: CallbackContext) -> str:
    """
    Parses the corresponding response for the question attributes.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`QUESTION_ATTRIBUTES`: If the user is not yet done selecting
        :attr:`NUMBER_QUESTIONS`: Else.
    """
    message = update.effective_message
    orchestra = context.bot_data[ORCHESTRA_KEY]
    data = update.callback_query.data
    update.callback_query.answer()

    if data == DONE:
        current_selection = parse_questions_hints_keyboard(message.reply_markup)
        game_settings = cast(GameSettings, context.user_data[GAME_KEY])
        game_settings.question_attributes = [attr for attr, sl in current_selection.items() if sl]

        message.edit_text(text=TEXTS[NUMBER_QUESTIONS], reply_markup=NUMBER_QUESTIONS_KEYBOARD)
        return NUMBER_QUESTIONS
    else:
        current_selection = parse_questions_hints_keyboard(message.reply_markup)
        attr, selection = data.split(' ')
        current_selection[attr] = not (selection == SELECTED)

        message.edit_reply_markup(reply_markup=build_questions_hints_keyboard(
            orchestra=orchestra, question=True, current_selection=current_selection))

        return QUESTION_ATTRIBUTES


def number_questions(update: Update, context: CallbackContext) -> str:
    """
    Parses the corresponding response for the number of questions.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    message = update.effective_message
    data = update.callback_query.data
    update.callback_query.answer()

    game_settings = cast(GameSettings, context.user_data[GAME_KEY])
    game_settings.number_of_questions = int(data)

    message.edit_text(text=TEXTS[MULTIPLE_CHOICE], reply_markup=MULTIPLE_CHOICE_KEYBOARD)
    return MULTIPLE_CHOICE


def multiple_choice(update: Update, context: CallbackContext) -> Union[str, int]:
    """
    Parses the corresponding response for the question mode.
    Also starts the game by initializing the :class:`components.Questioner` and asking the first
    question.
    If the configuration was invalid, ends the conversation.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    message = update.effective_message
    data = update.callback_query.data
    update.callback_query.answer()

    game_settings = cast(GameSettings, context.user_data[GAME_KEY])
    game_settings.multiple_choice = data == 'True'

    user_id = update.effective_user.id
    settings = cast(GameSettings, context.user_data[GAME_KEY])
    try:
        questioner = Questioner(user_id=user_id,
                                orchestra=context.bot_data[ORCHESTRA_KEY],
                                hint_attributes=settings.hint_attributes,
                                question_attributes=settings.question_attributes,
                                number_of_questions=settings.number_of_questions,
                                bot=context.bot,
                                multiple_choice=settings.multiple_choice)
        QUESTION_HANDLER.set_questioner(user_id, questioner)
        message.delete()

        questioner.ask_question()

        return GAME
    except ValueError:
        message.edit_text('Die gewählte Spielkonfiguration ist leider ungültig. Bitte versuche '
                          'es erneut.')
        return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """
    Cancels the game

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    update.effective_message.reply_text('Spiel abgebrochen. Es geht <i>nicht</i> in den '
                                        'Highscore ein.')
    return ConversationHandler.END


def fallback(update: Update, context: CallbackContext) -> None:
    """
    Reminds the user that they are playing a game and other functionality will not work.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    update.effective_message.reply_text('Du spielst gerade ein Spiel. 🧐 Bitte antworte nur auf '
                                        'die Fragen und mach keine anderen Eingaben. Wenn Du das '
                                        'Spiel abbrechen möchtest, nutze den Befehl '
                                        '/spiel_abbrechen.')


GAME_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('spiel_starten', hint_attributes)],
    states={
        HINT_ATTRIBUTES: [CallbackQueryHandler(hint_attributes)],
        QUESTION_ATTRIBUTES: [CallbackQueryHandler(question_attributes)],
        NUMBER_QUESTIONS: [CallbackQueryHandler(number_questions)],
        MULTIPLE_CHOICE: [CallbackQueryHandler(multiple_choice)],
        GAME: [QUESTION_HANDLER]
    },
    fallbacks=[CommandHandler('spiel_abbrechen', cancel),
               MessageHandler(Filters.all, fallback)],
    # We need to set per_chat to False in order to be able to handle PollAnswer updates
    per_chat=False)
""":class:`telegram.ext.ConversationHandler`: Handler for playing games."""

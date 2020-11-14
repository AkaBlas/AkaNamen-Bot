#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for editing user information."""
import datetime as dtm
import warnings
from copy import deepcopy
from typing import Dict, Callable, List, Union

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ChatAction,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.error import BadRequest
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    CallbackQueryHandler,
    Handler,
    InlineQueryHandler,
    BaseFilter,
)
from telegram.constants import MAX_INLINE_QUERY_RESULTS

from bot import (
    ORCHESTRA_KEY,
    build_instruments_keyboard,
    parse_instruments_keyboard,
    EDITING_MESSAGE_KEY,
    EDITING_USER_KEY,
    DONE,
    SELECTED,
    BACK,
    ADMIN_KEY,
    CONVERSATION_KEY,
)
from bot.constants import EDITING_ADMIN_KEY
from components import Member, Gender, Instrument

# Ignore warnings from ConversationHandler
from components.helpers import COORDINATES_PATTERN

warnings.filterwarnings('ignore', message="If", module='telegram.ext.conversationhandler')

# States of the conversation

MENU = 'MENU'
""":obj:`str`: Identifier of the menu state."""
FIRST_NAME = 'first_name'
""":obj:`str`: Identifier of the state in which the first name is changed."""
LAST_NAME = 'last_name'
""":obj:`str`: Identifier of the state in which the last name is changed."""
NICKNAME = 'nickname'
""":obj:`str`: Identifier of the state in which the nickname is changed."""
GENDER = 'gender'
""":obj:`str`: Identifier of the state in which the gender is changed."""
DATE_OF_BIRTH = 'date_of_birth'
""":obj:`str`: Identifier of the state in which the date of birth is changed."""
JOINED = 'joined'
""":obj:`str`: Identifier of the state in which the year of joining AkaBlas is changed."""
FUNCTIONS = 'functions'
""":obj:`str`: Identifier of the state in functions are changed."""
ADDRESS = 'address'
""":obj:`str`: Identifier of the state in which the address is changed."""
ADDRESS_CONFIRMATION = 'ADDRESS_CONFIRMATION'
""":obj:`str`: Identifier of the state in which the address change is confirmed."""
PHOTO = 'PHOTO'
""":obj:`str`: Identifier of the state in which the photo is changed."""
INSTRUMENTS = 'instruments'
""":obj:`str`: Identifier of the state in which the instruments are changed."""
ALLOW_CONTACT_SHARING = 'allow_contact_sharing'
""":obj:`str`: Identifier of the state in which the privacy setting is changed."""
PHONE_NUMBER = 'phone_number'
""":obj:`str`: Identifier of the state in which the phone number is changed."""
CHOOSING_MEMBER = 'choosing_member'
""":obj:`str`: Identifier of the state in which the admin chooses a member to edit."""
CONVERSATION_VALUE = 'editing'
"""
:obj:`str`: The value of ``context.user_data[CONVERSATION_KEY]`` if the user is in a editing
conversation.
"""
CONVERSATION_INTERRUPT_TEXT = (
    'Upsi! Du bearbeitest gerade noch Deine Daten. Bitte schließe das '
    'ab. Danach kannst Du mit mir machen, was Du willst. 😏 '
)
"""
:obj:`str`: Message to send, if the user tries to interrupt this conversation.
"""

# Texts
TEXTS: Dict[str, str] = {
    MENU: 'Dann lass uns mal schauen, ob Deine Daten noch aktuell sind. Bitte achte '
    'darauf, dass Du nur korrekte Angaben machst. Deine Daten lauten aktuell:\n\n{}\n\n'
    'Um eine Angabe zu ändern, klicke unten auf den entsprechenden Knopf.',
    FIRST_NAME: 'Aktuell habe ich gespeichert:\n\nVorname: {}\n\nUm den Namen zu ändern, '
    'schicke mir den neuen Namen. Um den Namen so zu lassen oder zu löschen, '
    'nutze die Knöpfe unten. ',
    LAST_NAME: 'Der Nachname, den ich gespeichert habe lautet:\n\nNachname: {}\n\nUm '
    'den Namen zu ändern, schicke mir den neuen Namen. Um den Namen so zu lassen oder '
    'zu löschen, nutze die Knöpfe unten.',
    NICKNAME: 'Der Spitzname, den ich gespeichert habe lautet:\n\nSpitzname: {}\n\nUm '
    'den Namen zu ändern, schicke mir den neuen Namen. Um den Namen so zu lassen oder '
    'zu löschen, nutze die Knöpfe unten.',
    GENDER: 'Das Geschlecht, das ich gespeichert habe ist:\n\nGeschlecht: {}\n\nUm '
    'Dein Geschlecht zu ändern, es so zu lassen oder zu löschen, nutze die Knöpfe unten.',
    DATE_OF_BIRTH: 'Das Geburtsdatum, das ich gespeichert habe ist:\n\nGeburtsdatum: '
    '{}\n\nUm das Datum zu ändern, schicke mir das neue Datum im Format '
    '<i>DD.MM.JJJJ</i>. Um das Datum so zu lassen oder zu löschen, nutze die Knöpfe'
    ' unten.',
    JOINED: 'Das Beitrittsjahr, das ich gespeichert habe ist:\n\n{}\n\nUm das Beitrittsjahr zu '
    'ändern, schicke mir das neue Jahr im Format <i>JJJJ</i>. Um das Jahr so zu lassen oder zu '
    'löschen, nutze die Knöpfe unten.',
    ADDRESS: 'Die Adresse, die ich gespeichert habe lautet:\n\nAdresse: {}\n\nUm '
    'die Adresse zu ändern, schicke mir entweder die Adresse als Text oder schicke mir '
    'einen Standort. Um die Adresse so zu lassen oder zu löschen, nutze die Knöpfe '
    'unten.',
    ADDRESS_CONFIRMATION: 'Okay, ich habe die folgende Adresse erkannt:\n\n{}\n\nWenn das '
    'richtig war, klicke bitte auf <i>Richtig</i>. Wenn das nicht richtig '
    'war, versuch bitte, die Adresse genauer aufzuschreiben oder den '
    'Standort genauer zu wählen. Du kannst mir auch direkt die richtigen '
    'Koordinaten schicken. Mehr Infos dazu stehen in den <a '
    'href="https://bibo-joshi.github.io/AkaNamen-Bot/faq.html#der-bot'
    '-nimmt-meine-adresse-nicht-an-ist-der-blod">FAQ</a>. 🤓',
    PHOTO: {  # type: ignore
        True: 'Dies ist das Foto, das ich aktuell gespeichert habe. Um Dein Foto '
        'zu ändern, schicke mir das neue Foto. Bitte achte darauf, dass man Dich darauf '
        'gut erkennen kann. Um das Foto so zu lassen oder zu löschen, nutze die Knöpfe '
        'unten. Du kannst auch Dein aktuellen Telegram-Profilbild übernehmen.',
        False: 'Aktuell habe ich kein Foto von Dir. Um ein Foto zu hinterlegen, '
        'schicke mir das Foto. Bitte achte darauf, dass man Dich darauf gut erkennen '
        'kann. Um das Foto so zu lassen oder zu löschen, nutze die Knöpfe unten. Du '
        'kannst auch Dein aktuellen Telegram-Profilbild übernehmen.',
    },
    INSTRUMENTS: 'Die Instrumente, die Du aktuell spielst, sind unten markiert. Um '
    'die Auswahl zu ändern, klicke auf die Instrumente.\n\nDu kannst auch mehrere '
    'Instrumente auswählen. Bitte mach das nur, wenn Du sie auch alle regelmäßig '
    'bei AkaBlas spielst. 😉\n\nWenn Du fertig bist, klicke unten auf <i>Weiter</i>.',
    ALLOW_CONTACT_SHARING: 'Du kannst entscheiden, '
    'ob andere AkaBlasen, die auch den AkaNamen-Bot nutzen, Deine Daten '
    'über diesen abrufen dürfen. Deine aktuelle Einstellung ist: {}. '
    'Bitte nutze die Knöpfe unten für die Antwort.',
    PHONE_NUMBER: 'Die Handynummer, die ich gespeichert habe lautet:\n\nHandynummer: {}\n\nUm '
    'die Nummer zu ändern, so zu lassen oder zu löschen, nutze die Knöpfe unten.',
    FUNCTIONS: 'Die Ämter, die ich gespeichert habe lauten:\n\nÄmter: {}\n\nUm die Ämter zu '
    'ändern, schicke sie mir als Komma-getrennte Liste. Um die Ämter so zu lassen '
    'oder zu löschen, nutze die Knöpfe unten.',
}
"""Dict[:obj:`str`,:obj:`str`]: Texts for the different states."""

# Keyboards
DELETE = 'DELETE'
"""obj:`str`: Callback data for deleting a setting."""
YES = 'Ja'
"""obj:`str`: Callback data for "yes"."""
NO = 'Nein'
"""obj:`str`: Callback data for "no"."""
CORRECT = 'Richtig'
"""obj:`str`: Callback data for "correct"."""
TG_PROFILE_PICTURE = 'TG_PROFILE_PICTURE'
"""obj:`str`: Callback data indicating that the profile picture of a user should be used as
 picture. """
BACK_OR_DELETE_KEYBOARD = InlineKeyboardMarkup.from_row(
    [
        InlineKeyboardButton(text=BACK, callback_data=BACK),
        InlineKeyboardButton(text='Löschen', callback_data=DELETE),
    ]
)
""":class:`telegram.InlineKeyboardMarkup`: Keyboard for either leaving the setting as is or
deleting its current value."""
YES_NO_KEYBOARD = InlineKeyboardMarkup.from_row(
    [
        InlineKeyboardButton(text=YES, callback_data=YES),
        InlineKeyboardButton(text=NO, callback_data=NO),
    ]
)
""":class:`telegram.InlineKeyboardMarkup`: Keyboard for a yes or no choice."""
GENDER_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text=Gender.MALE, callback_data=Gender.MALE),
            InlineKeyboardButton(text=Gender.FEMALE, callback_data=Gender.FEMALE),
        ],
        [
            InlineKeyboardButton(text=BACK, callback_data=BACK),
            InlineKeyboardButton(text='Löschen', callback_data=DELETE),
        ],
    ]
)
""":class:`telegram.InlineKeyboardMarkup`: Keyboard for selecting a gender."""
PHONE_NUMBER_KEYBOARD = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton(text='Nummer ändern', callback_data=PHONE_NUMBER)],
        [
            InlineKeyboardButton(text=BACK, callback_data=BACK),
            InlineKeyboardButton(text='Löschen', callback_data=DELETE),
        ],
    ]
)
""":class:`telegram.InlineKeyboardMarkup`: Keyboard for selecting a gender."""
ADDRESS_CONFIRMATION_KEYBOARD = InlineKeyboardMarkup.from_row(
    [
        InlineKeyboardButton(text=CORRECT, callback_data=CORRECT),
        InlineKeyboardButton(text='Löschen', callback_data=DELETE),
    ]
)
""":class:`telegram.InlineKeyboardMarkup`: Keyboard for confirming the address."""
SELECTION_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('Vorname', callback_data=FIRST_NAME),
            InlineKeyboardButton('Nachname', callback_data=LAST_NAME),
        ],
        [
            InlineKeyboardButton('Spitzname', callback_data=NICKNAME),
            InlineKeyboardButton('Geschlecht', callback_data=GENDER),
        ],
        [
            InlineKeyboardButton('Geburtsdatum', callback_data=DATE_OF_BIRTH),
            InlineKeyboardButton('Adresse', callback_data=ADDRESS),
        ],
        [
            InlineKeyboardButton('Bild', callback_data=PHOTO),
            InlineKeyboardButton('Instrumente', callback_data=INSTRUMENTS),
        ],
        [
            InlineKeyboardButton('Handynummer', callback_data=PHONE_NUMBER),
            InlineKeyboardButton('Beitrittsjahr', callback_data=JOINED),
        ],
        [
            InlineKeyboardButton('Datennutzung', callback_data=ALLOW_CONTACT_SHARING),
        ],
        [InlineKeyboardButton(DONE, callback_data=DONE)],
    ]
)


def selection_keyboard(context: CallbackContext) -> InlineKeyboardMarkup:
    """
    Function building the selection keyboard.

    Args:
        admin: Whether it's the admin changing the user or not.

    Returns: The keyboard.

    """
    admin = context.user_data.get(EDITING_ADMIN_KEY, False)

    if not admin:
        return SELECTION_KEYBOARD

    keyboard = deepcopy(SELECTION_KEYBOARD)
    keyboard.inline_keyboard[-2].append(InlineKeyboardButton('Ämter', callback_data=FUNCTIONS))
    return keyboard


def get_member(update: Update, context: CallbackContext) -> Member:
    """
    Returns the member to be edited. Takes into account the the admin may be editing one of the
    orchestras members

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    orchestra = context.bot_data[ORCHESTRA_KEY]
    admin_id = context.bot_data[ADMIN_KEY]
    user_id = update.effective_user.id

    if user_id == admin_id:
        edit_id = context.user_data.get(EDITING_USER_KEY, admin_id)
        return orchestra.members[edit_id]
    return orchestra.members[user_id]


def delete_keyboard(context: CallbackContext) -> None:
    """
    Tries to delete the inline keyboard from the last message. If a
    :class:`telegram.error.BadRequest` exception occurs this is most likely due to the message
    having no keyboard and hence it will be ignored.

    Args:
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    try:
        message = context.user_data.get(EDITING_MESSAGE_KEY)
        if message:
            message.edit_reply_markup()
    except BadRequest:
        pass


def reply_photo_state(update: Update, member: Member) -> Message:
    """
    Deletes the message of a ``CallbackQuery`` and sends the text needed for requesting user input
    for the photo state. If currently a photo is set, it is send.

    Args:
        update: The update.
        member: The current member object.

    Returns:
        Message: The newly sent message.
    """
    text = TEXTS[PHOTO][bool(member.photo_file_id)]
    profile_photos = update.effective_user.get_profile_photos()
    keyboard = deepcopy(BACK_OR_DELETE_KEYBOARD)

    if profile_photos.total_count >= 1:
        keyboard.inline_keyboard.insert(
            0, [InlineKeyboardButton('Profilbild übernehmen', callback_data=TG_PROFILE_PICTURE)]
        )

    update.callback_query.answer()

    if member.photo_file_id:
        update.effective_message.delete()
        message = update.effective_message.reply_photo(
            caption=text, photo=member.photo_file_id, reply_markup=keyboard
        )
    else:
        message = update.effective_message.edit_text(text=text, reply_markup=keyboard)

    return message


def start_admin_editing(update: Update, context: CallbackContext) -> str:
    """
    Starts the editing conversation for the admin by redirecting to inline mode.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`CHOOSING_MEMBER`
    """
    context.user_data[CONVERSATION_KEY] = CONVERSATION_VALUE
    update.effective_message.reply_text(
        'Okay, such Dir jemanden aus',
        reply_markup=InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(text='Klick', switch_inline_query_current_chat='')
        ),
    )
    return CHOOSING_MEMBER


def choose_member(update: Update, context: CallbackContext) -> str:
    """
    Provides the admin with a list of members to choose from.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`CHOOSING_MEMBER`
    """
    inline_query = update.inline_query
    orchestra = context.bot_data[ORCHESTRA_KEY]

    if inline_query.offset:
        offset = int(inline_query.offset)
    else:
        offset = 0
    next_offset: Union[str, int] = ''

    members = sorted(list(orchestra.members.values()), key=lambda member: member.full_name)

    # Telegram only likes up to 50 results
    if len(members) > (offset + 1) * MAX_INLINE_QUERY_RESULTS:
        next_offset = offset + 1
        members = members[
            offset * MAX_INLINE_QUERY_RESULTS : offset * MAX_INLINE_QUERY_RESULTS  # noqa: E203
            + MAX_INLINE_QUERY_RESULTS
        ]
    else:
        members = members[offset * MAX_INLINE_QUERY_RESULTS :]  # noqa: E203

    results = [
        InlineQueryResultArticle(
            id=m.user_id,
            title=m.full_name,
            input_message_content=InputTextMessageContent(m.user_id),
        )
        for m in members
    ]

    inline_query.answer(results=results, next_offset=next_offset)

    return CHOOSING_MEMBER


def admin_menu(update: Update, context: CallbackContext) -> str:
    """
    Starts the conversation for the admin and displays the menu.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`MENU`
    """
    user_id = int(update.message.text)
    context.user_data[EDITING_USER_KEY] = user_id
    context.user_data[EDITING_ADMIN_KEY] = True
    member = get_member(update, context)
    text = TEXTS[MENU].format(member.to_str())

    msg = update.effective_message.reply_text(text=text, reply_markup=selection_keyboard(context))
    context.user_data[EDITING_MESSAGE_KEY] = msg

    return MENU


def menu(update: Update, context: CallbackContext) -> str:
    """
    Starts the conversation and displays the menu.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`MENU`
    """
    context.user_data[CONVERSATION_KEY] = CONVERSATION_VALUE
    context.user_data[EDITING_ADMIN_KEY] = False
    member = get_member(update, context)
    text = TEXTS[MENU].format(member.to_str())

    msg = update.effective_message.reply_text(text=text, reply_markup=selection_keyboard(context))
    context.user_data[EDITING_MESSAGE_KEY] = msg

    return MENU


def parse_selection(update: Update, context: CallbackContext) -> str:
    """
    Parses the selection from the menu and updates the message accordingly.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        The next state depending on the selection or
        :attr:`telegram.ext.ConversationHandler.END`
    """
    update.callback_query.answer()

    data = update.callback_query.data
    message = update.effective_message

    member = get_member(update, context)

    if data == DONE:
        text = (
            f'Hervorragend 🙆‍♂️. Deine Daten lauten nun wie folgt:\n\n{member.to_str()}'
            f'\n\n<b>Übrigens:</b> Der Vorstand freut sich '
            f'sicherlich auch über Deine neuen Daten 😉. Schreib ihm doch eine Mail an '
            f'vorstand@akablas.de. ✉️ '
        )
        message.edit_text(text=text)

        # Only relevant for admin
        context.user_data.pop(EDITING_USER_KEY, None)
        context.user_data.pop(EDITING_ADMIN_KEY, None)

        context.user_data[CONVERSATION_KEY] = False
        return ConversationHandler.END

    if data == PHOTO:
        msg = reply_photo_state(update, member)
    else:
        reply_markup = BACK_OR_DELETE_KEYBOARD
        text = TEXTS[data].format(member[data] or "-")

        if data == INSTRUMENTS:
            current_selection = {i: True for i in member.instruments} if member.instruments else {}
            reply_markup = build_instruments_keyboard(current_selection=current_selection)
            text = TEXTS[data].format(member.instruments_str or '-')
        elif data == DATE_OF_BIRTH:
            text = TEXTS[DATE_OF_BIRTH].format(
                member.date_of_birth.strftime('%d.%m.%Y') if member.date_of_birth else "-"
            )
        elif data == FUNCTIONS:
            text = TEXTS[FUNCTIONS].format(member.functions_str or '-')
        elif data == GENDER:
            reply_markup = GENDER_KEYBOARD
        elif data == PHONE_NUMBER:
            reply_markup = PHONE_NUMBER_KEYBOARD
        elif data == ALLOW_CONTACT_SHARING:
            reply_markup = YES_NO_KEYBOARD
            text = TEXTS[data].format(
                'Erlaubt' if member.allow_contact_sharing else 'Nicht erlaubt'
            )

        msg = message.edit_text(text=text, reply_markup=reply_markup)

    context.user_data[EDITING_MESSAGE_KEY] = msg
    return data


def simple_callback_factory(attr: str) -> Callable[[Update, CallbackContext], str]:
    """
    Creates callbacks for the simple to handle attributes. The returned callback takes the
    arguments ``update, context`` as usual and returns :attr:`MENU`.

    Args:
        attr: The attribute to be parsed.
    """

    def callback(update: Update, context: CallbackContext) -> str:
        orchestra = context.bot_data[ORCHESTRA_KEY]
        member = get_member(update, context)
        reply_markup = selection_keyboard(context)

        if update.message:
            delete_keyboard(context)
            member[attr] = update.message.text

            text = TEXTS[MENU].format(member.to_str())
            msg = update.message.reply_text(text=text, reply_markup=reply_markup)
        else:
            data = update.callback_query.data
            if data in [Gender.MALE, Gender.FEMALE]:
                member.gender = data
            if data == DELETE:
                member[attr] = None
            update.callback_query.answer()

            text = TEXTS[MENU].format(member.to_str())
            msg = update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

        orchestra.update_member(member)
        context.user_data[EDITING_MESSAGE_KEY] = msg

        return MENU

    return callback


def simple_handler_factory(
    attr: str,
    message_handler: bool = True,
    filters: BaseFilter = None,
) -> List[Handler]:
    """
    Creates handlers for the simple to handle attributes. The returned list consists of

    * ``MessageHandler(Filters.text & ~Filters.command, simple_callback_factory(attr))``, if
      requested
    * ``CallbackQueryHandler(simple_callback_factory(attr))``

    Args:
        attr: The attribute to :meth:`simple_callback_factory`
        message_handler: Whether to include a :class:`telegram.ext.MessageHandler`. Defaults
            :obj:`True`
        filters: Optional additional filters for the message handler. Will be used as
            ``(Filters.text & ~Filters.command) & filters``
    """
    callback = simple_callback_factory(attr)
    if filters:
        filters = (Filters.text & ~Filters.command) & filters
    else:
        filters = Filters.text & ~Filters.command

    if message_handler:
        return [
            MessageHandler(filters, callback),
            CallbackQueryHandler(callback),
        ]
    return [CallbackQueryHandler(callback)]


def date_of_birth(update: Update, context: CallbackContext) -> str:
    """
    Parses the reply for the date of birth

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`MENU`: If input was not parsable
        :attr:`ADDRESS`: Else.
    """
    orchestra = context.bot_data[ORCHESTRA_KEY]
    member = get_member(update, context)

    if update.message:
        delete_keyboard(context)
        date_str = update.message.text
        try:
            datetime_of_birth = dtm.datetime.strptime(date_str, '%d.%m.%Y')
            dt_of_birth = datetime_of_birth.date()
            member.date_of_birth = dt_of_birth
            msg = update.effective_message.reply_text(
                text=TEXTS[MENU].format(member.to_str()), reply_markup=selection_keyboard(context)
            )
        except ValueError:
            update.message.reply_text(
                'Das habe ich nicht verstanden. Bitte gib das Datum im '
                'Format <i>DD.MM.JJJJ</i> ein.'
            )
            return DATE_OF_BIRTH
    else:
        if update.callback_query.data == DELETE:
            member.date_of_birth = None
        update.callback_query.answer()
        msg = update.callback_query.edit_message_text(
            text=TEXTS[MENU].format(member.to_str()), reply_markup=selection_keyboard(context)
        )

    context.user_data[EDITING_MESSAGE_KEY] = msg
    orchestra.update_member(member)

    return MENU


def address(update: Update, context: CallbackContext) -> str:
    """
    Parses the reply and asks the user for confirmation of the extracted address.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`MENU`: If an address/location was given
        :attr:`PHOTO`: Else.
    """
    orchestra = context.bot_data[ORCHESTRA_KEY]
    member = get_member(update, context)

    if update.message:
        delete_keyboard(context)
        message = update.message
        if context.match:
            addr = None
            latitude = float(context.match.group(1))
            longitude = float(context.match.group(2))
            coordinates = (latitude, longitude)
        elif message.text:
            addr = update.message.text
            coordinates = None  # type: ignore
        else:
            addr = None
            location = message.location
            coordinates = (location.latitude, location.longitude)

        context.bot.send_chat_action(update.effective_user.id, action=ChatAction.TYPING)

        found_address = member.set_address(address=addr, coordinates=coordinates)
        text = TEXTS[ADDRESS_CONFIRMATION].format(found_address or "-")
        msg = update.message.reply_text(text=text, reply_markup=ADDRESS_CONFIRMATION_KEYBOARD)

        context.user_data[EDITING_MESSAGE_KEY] = msg
        orchestra.update_member(member)

        return ADDRESS_CONFIRMATION

    update.callback_query.answer()

    if update.callback_query.data == DELETE:
        member.clear_address()

    msg = update.effective_message.edit_text(
        text=TEXTS[MENU].format(member.to_str()), reply_markup=selection_keyboard(context)
    )

    context.user_data[EDITING_MESSAGE_KEY] = msg
    orchestra.update_member(member)

    return MENU


def photo(update: Update, context: CallbackContext) -> str:
    """
    Parses the reply for the photo.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`MENU`
    """
    orchestra = context.bot_data[ORCHESTRA_KEY]
    member = get_member(update, context)
    message = update.effective_message

    if update.message:
        delete_keyboard(context)

        if update.message.photo:
            photo_size = update.message.photo[-1]

            if photo_size.width > photo_size.height:
                msg = message.reply_text(
                    'Ich kann leider keine Fotos im Querformat annehmen. 😕 '
                    'Bitte  schick mir ein anderes Foto.',
                    reply_markup=BACK_OR_DELETE_KEYBOARD,
                )
                context.user_data[EDITING_MESSAGE_KEY] = msg
                return PHOTO

            file_id = photo_size.file_id
            member.photo_file_id = file_id

            msg = message.reply_text(
                text=TEXTS[MENU].format(member.to_str()), reply_markup=selection_keyboard(context)
            )
            context.user_data[EDITING_MESSAGE_KEY] = msg
        else:
            msg = message.reply_text(
                text=(
                    'Bitte sende mir das Bild als Foto anstatt als Datei, '
                    'd.h. <i>nicht</i> über die Büroklammer.'
                ),
                reply_markup=BACK_OR_DELETE_KEYBOARD,
            )
            context.user_data[EDITING_MESSAGE_KEY] = msg
            return PHOTO
    else:
        update.callback_query.answer()
        callback_data = update.callback_query.data

        if callback_data == DELETE:
            member.photo_file_id = None
        elif callback_data == TG_PROFILE_PICTURE:
            profile_photos = update.effective_user.get_profile_photos()
            member.photo_file_id = profile_photos.photos[0][-1].file_id

        if message.photo:
            message.delete()

            msg = message.reply_text(
                text=TEXTS[MENU].format(member.to_str()), reply_markup=selection_keyboard(context)
            )
            context.user_data[EDITING_MESSAGE_KEY] = msg
        else:
            message.edit_text(
                text=TEXTS[MENU].format(member.to_str()), reply_markup=selection_keyboard(context)
            )

    orchestra.update_member(member)

    return MENU


def instruments(update: Update, context: CallbackContext) -> str:
    """
    Parses the reply and for the instruments.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`MENU`: If the user is not yet done selecting
        :attr:`ALLOW_CONTACT_SHARING`: Else.
    """
    message = update.effective_message
    data = update.callback_query.data
    orchestra = context.bot_data[ORCHESTRA_KEY]
    member = get_member(update, context)

    update.callback_query.answer()

    if data == DONE:
        message.edit_text(
            text=TEXTS[MENU].format(member.to_str()), reply_markup=selection_keyboard(context)
        )
        return MENU

    current_selection = parse_instruments_keyboard(message.reply_markup)
    instrument, selection = data.split(' ')
    key = Instrument.from_string(instrument, allowed=Member.ALLOWED_INSTRUMENTS)
    if key is not None:
        current_selection[key] = not selection == SELECTED
    member.instruments = [i for i, s in current_selection.items() if s]

    orchestra.update_member(member)

    message.edit_reply_markup(reply_markup=build_instruments_keyboard(current_selection))

    return INSTRUMENTS


def phone_number(update: Update, context: CallbackContext) -> str:
    """
    Parses the reply for the privacy settings.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`PHONE_NUMBER`: If the processing of the phone number is not yet finished.
        :attr:`MENU`: Else
    """
    orchestra = context.bot_data[ORCHESTRA_KEY]
    member = get_member(update, context)
    message = update.effective_message

    if update.message:
        number = update.message.contact.phone_number
        if number.startswith('49'):
            number = f'+{number}'
        member.phone_number = number
        orchestra.update_member(member)

        msg = message.reply_text('Danke!', reply_markup=ReplyKeyboardRemove())
        msg.delete()
        message.reply_text(
            text=TEXTS[MENU].format(member.to_str()), reply_markup=selection_keyboard(context)
        )

        return MENU

    update.callback_query.answer()
    data = update.callback_query.data

    if data == DELETE:
        member.phone_number = None
        orchestra.update_member(member)
        message.edit_text(
            text=TEXTS[MENU].format(member.to_str()), reply_markup=selection_keyboard(context)
        )

        return MENU

    if data == BACK:
        message.edit_text(
            text=TEXTS[MENU].format(member.to_str()), reply_markup=selection_keyboard(context)
        )

        return MENU

    delete_keyboard(context)
    text = 'Bitte nutze den Knopf unten, um mir Deine Nummer als Kontakt zu senden.'
    markup = ReplyKeyboardMarkup.from_button(
        KeyboardButton('Kontakt senden', request_contact=True)
    )
    message.reply_text(text=text, reply_markup=markup)

    return PHONE_NUMBER


def allow_contact_sharing(update: Update, context: CallbackContext) -> str:
    """
    Parses the reply for the privacy settings.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`MENU`
    """
    update.callback_query.answer()
    message = update.effective_message
    data = update.callback_query.data

    orchestra = context.bot_data[ORCHESTRA_KEY]
    member = get_member(update, context)

    member.allow_contact_sharing = data == YES
    orchestra.update_member(member)

    message.edit_text(
        text=TEXTS[MENU].format(member.to_str()), reply_markup=selection_keyboard(context)
    )

    return MENU


def functions(update: Update, context: CallbackContext) -> str:
    """
    Parses the reply for the functions.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Returns:
        :attr:`MENU`
    """
    orchestra = context.bot_data[ORCHESTRA_KEY]
    member = get_member(update, context)
    reply_markup = selection_keyboard(context)

    if update.message:
        delete_keyboard(context)
        member.functions = update.message.text.replace(' ', '').split(',')

        text = TEXTS[MENU].format(member.to_str())
        msg = update.message.reply_text(text=text, reply_markup=reply_markup)
    else:
        data = update.callback_query.data
        if data == DELETE:
            member.functions = None  # type: ignore
        update.callback_query.answer()

        text = TEXTS[MENU].format(member.to_str())
        msg = update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)

    orchestra.update_member(member)
    context.user_data[EDITING_MESSAGE_KEY] = msg

    return MENU


ADDRESS_FILTER = (
    (Filters.regex(COORDINATES_PATTERN) | Filters.text) & ~Filters.command
) | Filters.location


def build_editing_handler(admin: int) -> ConversationHandler:
    """
    Returns a handler used to edit members, with a special menu only available for the admin.

    Args:
        admin: The admins ID
    """
    return ConversationHandler(
        entry_points=[
            CommandHandler('daten_bearbeiten', menu),
            CommandHandler('edit_member', start_admin_editing, filters=Filters.user(admin)),
        ],
        states={
            CHOOSING_MEMBER: [
                InlineQueryHandler(choose_member),
                MessageHandler(Filters.text & ~Filters.command, admin_menu),
            ],
            MENU: [CallbackQueryHandler(parse_selection)],
            FIRST_NAME: simple_handler_factory(FIRST_NAME),
            LAST_NAME: simple_handler_factory(LAST_NAME),
            NICKNAME: simple_handler_factory(NICKNAME),
            JOINED: simple_handler_factory(JOINED, filters=Filters.regex(r'^\d{4}$')),
            FUNCTIONS: [
                MessageHandler((Filters.text & ~Filters.command), functions),
                CallbackQueryHandler(functions),
            ],
            GENDER: simple_handler_factory(GENDER, message_handler=False),
            DATE_OF_BIRTH: [
                MessageHandler((Filters.text & ~Filters.command), date_of_birth),
                CallbackQueryHandler(date_of_birth),
            ],
            ADDRESS: [MessageHandler(ADDRESS_FILTER, address), CallbackQueryHandler(address)],
            ADDRESS_CONFIRMATION: [
                MessageHandler(ADDRESS_FILTER, address),
                CallbackQueryHandler(address),
            ],
            PHOTO: [
                MessageHandler(Filters.photo | Filters.document.image, photo),
                CallbackQueryHandler(photo),
            ],
            INSTRUMENTS: [CallbackQueryHandler(instruments)],
            PHONE_NUMBER: [
                MessageHandler(Filters.contact, phone_number),
                CallbackQueryHandler(phone_number),
            ],
            ALLOW_CONTACT_SHARING: [CallbackQueryHandler(allow_contact_sharing)],
        },
        fallbacks=[],
        per_chat=False,
    )

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for registering users."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, DispatcherHandlerStop, CallbackQueryHandler
from bot import (PENDING_REGISTRATIONS_KEY, ORCHESTRA_KEY, DENIED_USERS_KEY, REGISTRATION_KEYBOARD,
                 DOCS_KEYBOARD, ADMIN_KEY, CHANNEL_KEYBOARD)
from components import Member

ACCEPT_REGISTRATION = 'accept_registration {} {}'
""":obj:`str`: Callback data for accepting a registration request with a suggested members data.
Use as ``ACCEPT_REGISTRATION_MEMBER.format(chat_id, data_index)``. Use ``''`` for data_index, if no
given data is to be accepted."""
ACCEPT_REGISTRATION_PATTERN = r'accept_registration (\d*)(?: (\d*))?'
""":obj:`str`: Callback data  pattern for accepting a registration request with a suggested members
data. ``context.match.group(1)`` will be users id and ``context.match.group(2)`` the index of the
accepted member date or :obj:`None`."""
DENY_REGISTRATION = 'deny_registration {}'
""":obj:`str`: Callback data for denying a registration request.
Use as ``DENY_REGISTRATION.format(chat_id)``."""
DENY_REGISTRATION_PATTERN = r'deny_registration (\d*)'
""":obj:`str`: Callback data  pattern for accepting a registration request with a suggested members
data. ``context.match.group(1)`` will be users id."""


def check_registration_status(update: Update, context: CallbackContext) -> None:
    """
    Checks the registration of the user. This can have four outcomes:

    1. The user is not yet registered. In this case only the ``/start`` command is accepted. Other
       updates will be answered with a note that the user needs to register.
    2. The user has sent a registration request, which is pending. In this case, updates will be
       answered with a note asking to be patient.
    3. The user has successfully bee registered. Nothing happens in this case.
    4. The user has been denied registration. In this case the update will not be processed any
       further.

    If the update has no effective user, it won't be handled in any case.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.

    Raises:
        :class:`telegram.ext.DispatcherHandlerStop`: In case the update is not to be handled by any
            other handlers.
    """
    if not update.effective_user:
        raise DispatcherHandlerStop()
    user_id = update.effective_user.id
    bot_data = context.bot_data

    # User is registered
    if user_id in bot_data[ORCHESTRA_KEY].members:
        return

    # Admins can do anything
    if user_id == bot_data[ADMIN_KEY]:
        return

    if user_id in bot_data[PENDING_REGISTRATIONS_KEY]:
        if update.effective_message:
            update.effective_message.reply_text(
                'Du wirst benachrichtigt, sobald Deine Anmeldungs-Anfrage bearbeitet wurde. 📬 '
                'Bitte habe noch ein bisschen Geduld. Der nächste freie Hirsch ist für Dich '
                'reserviert. 🦌 In der Zwischenzeit kannst Du ja schon mal in die FAQ schauen. '
                '😉',
                reply_markup=DOCS_KEYBOARD)
        raise DispatcherHandlerStop()

    if user_id in bot_data[DENIED_USERS_KEY]:
        raise DispatcherHandlerStop()

    if update.message:
        if update.message.text != '/start':
            update.message.reply_text(
                'Bevor Du los raten kannst, musst Du Dich erst anmelden. '
                'Bitte klick dafür hier ⬇️',
                reply_markup=REGISTRATION_KEYBOARD)
            raise DispatcherHandlerStop()


def start(update: Update, context: CallbackContext) -> None:
    """
    Greets the new user and asks them to register.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    text = 'Moin! 🙂 Schön, dass Du mitspielen möchtest. Bevor es losgehen kann, muss zuerst ' \
           'sichergestellt werden, dass Du auch wirklich bei AkaBlas bist. Falls Du in den ' \
           'AkaDressen zu finden bist, sollte das schnell gehen. Falls nicht, wird Hirsch Dich ' \
           'ggf. noch einmal direkt anschreiben. Klicke bitte einfach auf das Feld unten. Du ' \
           'bekommst eine Nachricht, sobald Deine Anfrage bearbeitet wurde.'

    orchestra = context.bot_data[ORCHESTRA_KEY]
    if update.effective_user.id in orchestra.members:
        update.effective_message.reply_text('Du bist bereits angemeldet.')
    else:
        update.effective_message.reply_text(text, reply_markup=REGISTRATION_KEYBOARD)


def request_registration(update: Update, context: CallbackContext) -> None:
    """
    Triggers the registration process by sending the admin a message.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    update.callback_query.answer()
    update.effective_message.edit_text(
        'Anfrage gesendet! Bis sie bearbeitet wurde, kannst Du ja schon mal in die FAQ schauen. 😉',
        reply_markup=DOCS_KEYBOARD)

    user = update.effective_user
    guessed_members = Member.guess_member(user)

    user_link = f'@{user.username}' if user.username else user.mention_html()
    header = f'Der Telegram-Nutzer {user_link} möchte den AkaNamen-Bot nutzen.'

    if not guessed_members:
        results = 'In den AkaDressen konnte kein passendes Mitglied gefunden werden.'
        buttons = [[
            InlineKeyboardButton(text='Akzeptieren',
                                 callback_data=ACCEPT_REGISTRATION.format(user.id, ''))
        ]]
    else:
        results = 'In den AkaDressen wurden folgende passende Mitglieder gefunden:'
        buttons = []
        for i, member in enumerate(guessed_members):
            results += f'\n\n<b>{i+1}.</b>\n{member.to_str()}'
            buttons.append([
                InlineKeyboardButton(text=f'Akzeptiere als Mitglied {i+1}',
                                     callback_data=ACCEPT_REGISTRATION.format(user.id, i))
            ])

        buttons.append([
            InlineKeyboardButton(text='Akzeptieren ohne AkaDressen-Daten',
                                 callback_data=ACCEPT_REGISTRATION.format(user.id, ''))
        ])

    buttons.append(
        [InlineKeyboardButton(text='Ablehnen', callback_data=DENY_REGISTRATION.format(user.id))])
    text = '\n\n'.join([header, results])
    reply_markup = InlineKeyboardMarkup(buttons)

    context.bot.send_message(chat_id=context.bot_data[ADMIN_KEY],
                             text=text,
                             reply_markup=reply_markup)

    context.bot_data[PENDING_REGISTRATIONS_KEY][user.id] = guessed_members or []


def accept_registration_request(update: Update, context: CallbackContext) -> None:
    """
    Parses the admins response to a registration request and answers the user correspondingly.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    bot_data = context.bot_data
    user_id = int(context.match.group(1))
    user = context.bot.get_chat_member(user_id, user_id).user
    profile_photos = user.get_profile_photos()

    if profile_photos.total_count >= 1:
        profile_ile_id = profile_photos.photos[0][-1].file_id
    else:
        profile_ile_id = None

    idx = context.match.group(2)
    if not idx:
        new_member = Member(user_id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            photo_file_id=profile_ile_id)
    else:
        idx = int(idx)
        new_member = bot_data[PENDING_REGISTRATIONS_KEY][user_id][idx]
        new_member.photo_file_id = profile_ile_id

    bot_data[ORCHESTRA_KEY].register_member(new_member)
    bot_data[PENDING_REGISTRATIONS_KEY].pop(user_id, None)

    text = f'Du bis jetzt mit den folgenden Daten angemeldet: 🥳\n\n{new_member.to_str()}\n\n'
    if profile_ile_id:
        text += 'Als Photo wurde Dein Telegram-Profilbild gesetzt. '
    text += 'Um die Daten zu bearbeiten, sende den Befehl /daten_bearbeiten. Wofür die Daten ' \
            'genutzt werden, kannst Du im Benutzerhandbuch nachlesen.\n\nBitte tritt ' \
            'außerdem dem Info-Kanal bei. Dort werden ggf. Informationen zu Neuerungen am Bot ' \
            'oder Wartungsarbeiten bekanntgegeben.\n\nWenn Du Hilfe brauchst, tippe einfach ' \
            '/hilfe ein.'

    context.bot.send_message(chat_id=user_id, text=text, reply_markup=CHANNEL_KEYBOARD)
    update.effective_message.edit_text('Nutzer erfolgreich angemeldet.')


def deny_registration_request(update: Update, context: CallbackContext) -> None:
    """
    Parses the admins response to a registration request and answers the user correspondingly.

    Args:
        update: The update.
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    bot_data = context.bot_data
    user_id = int(context.match.group(1))
    bot_data[PENDING_REGISTRATIONS_KEY].pop(user_id, None)
    bot_data[DENIED_USERS_KEY].append(user_id)

    context.bot.send_message(chat_id=user_id,
                             text='Deine Anfrage wurde abgelehnt. Ich werde von jetzt an nicht '
                             'mehr auf Dich reagieren. 💁🏼‍♂️')
    update.effective_message.edit_text('Nutzer wurde abgelehnt und wird jetzt ignoriert.')


ACCEPT_REGISTRATION_HANDLER = CallbackQueryHandler(accept_registration_request,
                                                   pattern=ACCEPT_REGISTRATION_PATTERN)
""":class:`telegram.ext.CallbackQueryHandler`: Handler used to parse the acceptance of a
registration request."""
DENY_REGISTRATION_HANDLER = CallbackQueryHandler(deny_registration_request,
                                                 pattern=DENY_REGISTRATION_PATTERN)
""":class:`telegram.ext.CallbackQueryHandler`: Handler used to parse the denial of a
registration request."""

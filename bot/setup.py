#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for setting up to bot at start up."""
import re
from typing import List, Union, Dict

from telegram import BotCommand, Update
from telegram.ext import (
    Dispatcher,
    TypeHandler,
    CommandHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    Filters,
    CallbackContext,
    DispatcherHandlerStop,
    ConversationHandler,
)
from ptbstats import set_dispatcher, register_stats, SimpleStats

from bot import (
    ORCHESTRA_KEY,
    PENDING_REGISTRATIONS_KEY,
    DENIED_USERS_KEY,
    ADMIN_KEY,
    REGISTRATION_PATTERN,
    INLINE_HELP,
    CONVERSATION_KEY,
)
import bot.editing as editing
import bot.cancel_membership as cancel_membership
import bot.backup as backup
import bot.ban as ban
import bot.check_user_status as check_user_status
import bot.registration as registration
import bot.commands as commands
import bot.inline as inline
import bot.highscore as highscore
import bot.error as error
import bot.game as game
import bot.admin

from components import Orchestra, Member

BOT_COMMANDS: List[BotCommand] = [
    BotCommand('spiel_starten', 'Startet ein neues Spiel'),
    BotCommand('spiel_abbrechen', 'Bricht das aktuelle Spiel ab'),
    BotCommand('daten_anzeigen', 'Zeigt Deine gespeicherten Daten an'),
    BotCommand('daten_bearbeiten', 'Daten wie Adresse und Foto ändern'),
    BotCommand('highscore', 'Zeigt den aktuellen Highscore an'),
    BotCommand('hilfe', 'Zeigt ein paar generelle Hinweise zum Bot'),
    BotCommand('kontakt_abrufen', 'Kontaktdaten anderer AkaBlasen abrufen'),
    BotCommand('start', 'Startet den Bot'),
    BotCommand('abmelden', 'Vom Bot abmelden und alle Daten löschen'),
]
"""List[:class:`telegram.BotCommand`]: A list of commands of the bot."""


def setup(  # pylint: disable=R0913,R0914,R0915
    dispatcher: Dispatcher,
    admin: Union[int, str],
    oc_url: str,
    oc_username: str,
    oc_password: str,
    oc_path: str,
    ad_url: str,
    ad_url_active: str,
    ad_username: str,
    ad_password: str,
) -> None:
    """
    * Adds handlers. Convenience method to avoid doing that all in the main script.
    * Sets the bot commands and makes sure ``dispatcher.bot_data`` is set up correctly.
    * Registers a :class:`telegram.ext.TypeHandler` that makes sure that conversations are not
      interrupted
    * Sets up statistics

    Args:
        dispatcher: The :class:`telegram.ext.Dispatcher`.
        admin: The admins chat id.
        oc_url: URL of the OwnCloud Instance.
        oc_username: Username for the OwnCloud Instance.
        oc_password: Password of the OwnCloud Instance.
        oc_path: Remote path on the OwnCloud Instance.
        ad_url: URL of the AkaDressen file.
        ad_url_active: URL of the AkaDressen file containing only the active members.
        ad_username: Username for the AkaDressen.
        ad_password: Password for the AkaDressen.
    """

    def check_conversation_status(update: Update, context: CallbackContext) -> None:
        """
        Checks if the user is currently in a conversation. If they are and the corresponding
        conversation does *not* handle the incoming update, the user will get a corresponding
        message and the update will be discarded.

        Args:
            update: The update.
            context: The context as provided by the :class:`telegram.ext.Dispatcher`.
        """
        if not update.effective_user:
            return

        conversation = context.user_data.get(CONVERSATION_KEY, None)
        if not conversation:
            return

        conversation_check = not bool(conversations[conversation].check_update(update))
        # Make sure that the callback queries for vcard requests are not processed
        if update.callback_query:
            contact_request_check = bool(
                re.match(inline.REQUEST_CONTACT_PATTERN, update.callback_query.data)
            )
            highscore_check = 'highscore' in update.callback_query.data
        else:
            contact_request_check = False
            highscore_check = False

        if conversation_check or contact_request_check or highscore_check:
            text = interrupt_replies[conversation]
            if update.callback_query:
                update.callback_query.answer(text=text, show_alert=True)
            elif update.effective_message:
                update.effective_message.reply_text(text)
            raise DispatcherHandlerStop()

    def clear_conversation_status(update: Update, context: CallbackContext) -> None:
        """
        Clears the conversation status of a user in case of an error. Just to be sure.

        Args:
            update: The update.
            context: The context as provided by the :class:`telegram.ext.Dispatcher`.
        """
        if update.effective_user:
            context.user_data.pop(CONVERSATION_KEY)

    # ------------------------------------------------------------------------------------------- #

    # Set up statistics
    set_dispatcher(dispatcher)
    # Count total number of updates
    register_stats(SimpleStats('stats', lambda u: bool(u.effective_user)), admin_id=int(admin))
    # Count number of started games
    register_stats(
        SimpleStats('game_stats', lambda u: bool(u.message) and Filters.text('/spiel_starten')(u)),
        admin_id=int(admin),
    )
    # Count number of requested contacts
    register_stats(
        admin_id=int(admin),
        stats=SimpleStats(
            'contact_stats',
            lambda u: bool(u.callback_query and 'contact_request' in u.callback_query.data),
        ),
    )

    # Handlers

    # Prepare conversations
    game_handler = game.GAME_HANDLER
    editing_conversation = editing.build_editing_handler(int(admin))
    canceling_conversation = cancel_membership.CANCEL_MEMBERSHIP_HANDLER
    banning_conversation = ban.build_banning_handler(int(admin))
    conversations: Dict[str, ConversationHandler] = {
        game.CONVERSATION_VALUE: game_handler,
        editing.CONVERSATION_VALUE: editing_conversation,
        cancel_membership.CONVERSATION_VALUE: canceling_conversation,
        ban.CONVERSATION_VALUE: banning_conversation,
    }
    interrupt_replies: Dict[str, str] = {
        game.CONVERSATION_VALUE: game.CONVERSATION_INTERRUPT_TEXT,
        editing.CONVERSATION_VALUE: editing.CONVERSATION_INTERRUPT_TEXT,
        cancel_membership.CONVERSATION_VALUE: cancel_membership.CONVERSATION_INTERRUPT_TEXT,
        ban.CONVERSATION_VALUE: ban.CONVERSATION_INTERRUPT_TEXT,
    }

    # Registration status
    dispatcher.add_handler(TypeHandler(Update, registration.check_registration_status), group=-2)

    # Conversation Interruption behaviour
    dispatcher.add_handler(TypeHandler(Update, check_conversation_status), group=-1)

    # Game Conversation
    # Must be first so that the fallback can catch unrelated messages
    dispatcher.add_handler(game_handler)

    # Registration process
    # We need the filter here in order to not catch /start with deep linking parameter used for
    # inline help
    dispatcher.add_handler(
        CommandHandler('start', registration.start, filters=Filters.text('/start'))
    )
    dispatcher.add_handler(
        CallbackQueryHandler(registration.request_registration, pattern=REGISTRATION_PATTERN)
    )
    dispatcher.add_handler(registration.ACCEPT_REGISTRATION_HANDLER)
    dispatcher.add_handler(registration.DENY_REGISTRATION_HANDLER)

    # Edit user data
    dispatcher.add_handler(editing_conversation)

    # Cancel membership
    dispatcher.add_handler(canceling_conversation)

    # Banning members
    dispatcher.add_handler(banning_conversation)

    # Simple commands
    dispatcher.add_handler(CommandHandler(['hilfe', 'help'], commands.help_message))
    dispatcher.add_handler(CommandHandler('daten_anzeigen', commands.show_data))
    dispatcher.add_handler(CommandHandler('kontakt_abrufen', commands.start_inline))
    dispatcher.add_handler(
        CommandHandler(
            'start', commands.start_inline, filters=Filters.text(f'/start {INLINE_HELP}')
        )
    )

    # Inline Mode
    dispatcher.add_handler(InlineQueryHandler(inline.search_users))
    dispatcher.add_handler(inline.SEND_VCARD_HANDLER)

    # Highscores
    dispatcher.add_handler(CommandHandler('highscore', highscore.show_highscore))
    dispatcher.add_handler(highscore.HIGHSCORE_HANDLER)

    # Set commands
    dispatcher.bot.set_my_commands(BOT_COMMANDS)

    # Admin stuff
    dispatcher.add_handler(
        CommandHandler('rebuild', bot.admin.rebuild_orchestra, filters=Filters.user(int(admin)))
    )

    # Error Handler
    dispatcher.add_error_handler(error.handle_error)
    dispatcher.add_error_handler(clear_conversation_status)

    # Schedule jobs
    check_user_status.schedule_daily_job(dispatcher)
    backup.PATH = oc_path
    backup.URL = oc_url
    backup.USERNAME = oc_username
    backup.PASSWORD = oc_password
    backup.schedule_daily_job(dispatcher)

    # Set up AkaDressen credentials
    Member.set_akadressen_credentials(ad_url, ad_url_active, ad_username, ad_password)

    # Set up bot_data
    bot_data = dispatcher.bot_data
    if not bot_data.get(ORCHESTRA_KEY):
        bot_data[ORCHESTRA_KEY] = Orchestra()
    if not bot_data.get(PENDING_REGISTRATIONS_KEY):
        bot_data[PENDING_REGISTRATIONS_KEY] = dict()
    if not bot_data.get(DENIED_USERS_KEY):
        bot_data[DENIED_USERS_KEY] = list()
    bot_data[ADMIN_KEY] = int(admin)

    # Clear conversation key
    user_data = dispatcher.user_data
    for user_id in user_data:
        user_data[user_id].pop(CONVERSATION_KEY, None)

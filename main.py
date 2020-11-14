#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The script that runs the bot."""
import logging
from configparser import ConfigParser
from telegram import ParseMode
from telegram.ext import Updater, PicklePersistence, Defaults

from bot.setup import setup

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='akanamen.log')

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    # Read configuration values from bot.ini
    config = ConfigParser()
    config.read('bot.ini')
    token = config['akanamen-bot']['token']
    admin = config['akanamen-bot']['admins_chat_id']
    oc_url = config['owncloud']['url']
    oc_username = config['owncloud']['username']
    oc_password = config['owncloud']['password']
    oc_path = config['owncloud']['path']
    ad_url = config['akadressen']['url']
    ad_url_active = config['akadressen']['url_active']
    ad_username = config['akadressen']['username']
    ad_password = config['akadressen']['password']
    yourls_url = config['yourls']['url']
    yourls_signature = config['yourls']['signature']

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    defaults = Defaults(parse_mode=ParseMode.HTML, disable_notification=True)
    persistence = PicklePersistence('akanamen_db', single_file=False)
    updater = Updater(token, use_context=True, persistence=persistence, defaults=defaults)

    setup(
        updater.dispatcher,
        admin=admin,
        oc_url=oc_url,
        oc_username=oc_username,
        oc_password=oc_password,
        oc_path=oc_path,
        ad_url=ad_url,
        ad_url_active=ad_url_active,
        ad_username=ad_username,
        ad_password=ad_password,
        yourls_url=yourls_url,
        yourls_signature=yourls_signature,
    )

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

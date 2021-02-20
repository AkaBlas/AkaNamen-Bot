#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains functions for backing up the pickle files."""
import datetime as dtm

from telegram.ext import CallbackContext, Dispatcher

import owncloud

URL = ''
USERNAME = ''
PASSWORD = ''
PATH = ''


def back_up(context: CallbackContext) -> None:
    """
    Flushes the data to pickle file and uploads them to the OwnCloud/NextCloud instance as
    specified in the config file.

    Args:
        context: The context as provided by the :class:`telegram.ext.Dispatcher`.
    """
    context.dispatcher.update_persistence()
    context.dispatcher.persistence.flush()

    client = owncloud.Client(URL)
    client.login(USERNAME, PASSWORD)
    try:
        client.mkdir(PATH)
    except owncloud.HTTPResponseError:
        pass

    base = 'akanamen_db_{}_data'
    for extension in ['bot', 'chat', 'user']:
        file_name = base.format(extension)
        client.put_file(f'{PATH}/{dtm.datetime.now().isoformat()}_{file_name}', file_name)

    client.logout()


def schedule_daily_job(dispatcher: Dispatcher) -> None:
    """
    Schedules a job running daily at 2AM which runs :meth:`back_up`.

    Args:
        dispatcher: The :class:`telegram.ext.Dispatcher`.
    """
    dispatcher.job_queue.run_daily(back_up, dtm.time(2, 0))

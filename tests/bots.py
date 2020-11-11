#!/usr/bin/env python
"""Provide a bot to tests"""
import random
import time

import pytest
from telegram.error import RetryAfter
from telegram.utils.request import Request

BOTS = [
    {
        'token': '1076068896:AAFdpos7qs7aaZfaGMsSydrqY063NFV4cXM',
        'chat_id': '1145108092',
        'super_group_id': '-1001420760595',
        'bot_name': 'AkaNamen tests [1]',
        'bot_username': '@akanamen_1_bot',
    },
    {
        'token': '755604868:AAEWXBULDISurkw2qGkPOQ4B-8tNxbCCAdM',
        'chat_id': '1145108092',
        'super_group_id': '-1001287464815',
        'bot_name': 'AkaNamen tests [2]',
        'bot_username': '@akanamen_2_bot',
    },
    {
        'token': '1127008229:AAFl7_GQGroMmAvvdzjifiQIRIuqyh4J8Uk',
        'chat_id': '1145108092',
        'super_group_id': '-1001464027540',
        'bot_name': 'AkaNamen tests [3]',
        'bot_username': '@akanamen_3_bot',
    },
    {
        'token': '1074956120:AAF2ke_uy6yglYp4YGtzjXR777upTt4TO14',
        'chat_id': '1145108092',
        'super_group_id': '-1001439996750',
        'bot_name': 'AkaNamen tests [4]',
        'bot_username': '@akanamen_4_bot',
    },
]


def get_bot():
    return random.choice(BOTS)


# Patch request to xfail on flood control errors
original_request_wrapper = Request._request_wrapper


def patient_request_wrapper(*args, **kwargs):
    try:
        return original_request_wrapper(*args, **kwargs)
    except RetryAfter as e:
        time.sleep(e.retry_after + 2)
        try:
            return original_request_wrapper(*args, **kwargs)
        except RetryAfter as f:
            pytest.xfail('Not waiting for flood control: {}'.format(f))


Request._request_wrapper = patient_request_wrapper

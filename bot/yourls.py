#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module contains a custom YOURLS client."""
import urllib
from yourls import YOURLSClientBase, YOURLSAPIMixin
from yourls.extensions import YOURLSEditUrlMixin, YOURLSKeywordExistsError  # pylint: disable=E0611

from components import Member


class YOURLSClient(YOURLSClientBase, YOURLSAPIMixin, YOURLSEditUrlMixin):
    """
    A custom YOURLS client with edit functionality.
    """


def generate_mail_link(member: Member, client: YOURLSClient) -> str:
    """
    Given a member, generates a short link that allows the member to send a pre filled mail to the
    board informing them that their details changed.

    Args:
        member: The member.
        client: The YOURLS client.

    Returns: The link.
    """
    subject = f'Neue Kontaktdaten | {member.full_name}'
    info = (
        f'Name: {member.full_name or "-"}\n'
        f'Adresse: {member.address or "-"}\n'
        f'Mobil: {member.phone_number or "-"}'
    )
    body = (
        f'Lieber Vorstand,\n\nmeine Kontaktdaten haben sich geändert. Sie lauten nun\n\n'
        f'{info}\n\nIch würde mich freuen, wenn Ihr sie in den AkaDressen '
        f'aktualisieren könntet.\n\nVielen Dank und herzliche Grüße,\n{member.full_name}\n\n'
        f'-----------------------------------------------------------------------------\n'
        f'Diese Mail wurde automisch vom AkaNamenBot generiert.'
    )
    params = {'subject': subject, 'body': body}
    payload = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)  # type: ignore
    url = f'mailto:vorstand@akablas.de?{payload}'
    keyword = f'AkaNamenBot{member.user_id}'

    try:
        short_url = client.shorten(url, keyword=keyword)
        return short_url.shorturl
    except YOURLSKeywordExistsError:
        client.update(keyword, url)
        base_url = client.apiurl
        if base_url.endswith('/yourls-api.php'):
            base_url = base_url[:-15]
        return f'{base_url}/{keyword}'

import urllib

from django.conf import settings

from amo.urlresolvers import get_url_prefix, reverse


def remora_url(url, lang=None, app=None, prefix=''):
    """
    Builds a remora-style URL, independent from Zamboni's prefixer logic.
    If app and/or lang are None, the current Zamboni values will be used.
    To omit them from the URL, set them to ''.
    """
    prefixer = get_url_prefix()
    if lang is None:
        try:
            lang = prefixer.locale
        except AttributeError:
            lang = settings.LANGUAGE_CODE
    if app is None:
        try:
            app = prefixer.app
        except AttributeError:
            app = settings.DEFAULT_APP

    url_parts = [prefix, lang, app, url]
    url_parts = [p.strip('/') for p in url_parts if p]

    full_path = '/'+'/'.join(url_parts)
    return urllib.quote(full_path.encode('utf-8'))

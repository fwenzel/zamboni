from django import http
from django.conf import settings
from django.db.models import Min

import jingo
import product_details

import amo.utils

from . import L10N_CATEGORIES
from .models import L10nEventlog, L10nSettings


def dashboard(request):
    """global L10n dashboard"""

    # compile locale stats
    stats = []
    for lang in (settings.AMO_LANGUAGES + settings.HIDDEN_LANGUAGES):
        # en-US is "translated" by default
        if lang == 'en-US':
            stats.append((lang, 100))
            continue

        lang_stats = []
        for category in iter(L10N_CATEGORIES):
            stats_event = L10nEventlog.objects.filter(
                type='stats', action=category, locale=lang).order_by(
                '-created').only('notes')[:1]
            if stats_event:
                lang_stats.append(float(stats_event[0].notes))

        try:
            percentage = sum(lang_stats) / len(lang_stats)
        except ZeroDivisionError:
            percentage = 0

        stats.append((lang, percentage))

    data = {
        'stats': {'high': [ l for l, p in stats if p >= 95 ],
                  'medium': [ l for l, p in stats if 70 <= p < 95 ],
                  'low': [ l for l, p in stats if p < 70 ]},
        'languages': product_details.languages,
        'hidden_langs': settings.HIDDEN_LANGUAGES
    }

    # recent activity
    q = L10nEventlog.objects.exclude(type='stats').values(
        'type', 'action', 'changed_id').distinct().order_by('-created').values(
        'type', 'action', 'changed_id', 'notes', 'created')
    activity = amo.utils.paginate(request, q, 5)
    data['activity'] = activity

    return jingo.render(request, 'localizers/summary.html', data)


def locale_dashboard(request, locale_code):
    """per-locale dashboard"""
    return http.HttpResponse(
        'this is the l10n dashboard for %s' % locale_code)


def gettext(request, locale_code):
    return http.HttpResponse(
        'this is the gettext dashboard for %s' % locale_code)


def categories(request, locale_code):
    return http.HttpResponse(
        'this is the categories dashboard for %s' % locale_code)


def collection_features(request, locale_code):
    return http.HttpResponse(
        'this is the collection feat. dashboard for %s' % locale_code)


def pages(request, locale_code):
    return http.HttpResponse(
        'this is the pages dashboard for %s' % locale_code)

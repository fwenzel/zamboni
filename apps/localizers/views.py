import json
import os.path
import re

from django import http
from django.conf import settings
from django.db.models import Min
from django.utils import translation
from django.views.decorators.http import require_POST

import jingo
from tower import ugettext as _
import product_details

from access import acl
from access.models import Group
import amo.utils
from amo.urlresolvers import reverse
from zadmin.models import Config

from . import L10N_CATEGORIES
from .models import L10nEventlog, L10nSettings


def summary(request):
    """global L10n dashboard"""

    # compile locale stats
    stats = []
    for lang in (settings.AMO_LANGUAGES + settings.HIDDEN_LANGUAGES):
        # en-US is "translated" by default
        if lang == 'en-US':
            stats.append((lang, 100))
            continue

        lang_stats = []
        for category, _ in L10N_CATEGORIES:
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


@require_POST
def set_motd(request):
    """AJAX: Set announcements for either global or per-locale dashboards."""
    lang = request.POST.get('lang', None)
    msg = request.POST.get('msg', None)

    if (lang != '' and lang not in settings.AMO_LANGUAGES and
        lang not in settings.HIDDEN_LANGUAGES or
        msg is None):
        return _json_error(_('An error occurred saving this message.'))

    if (not acl.action_allowed(request, 'Admin', 'EditAnyLocale') and
        not acl.action_allowed(request, 'Localizers', lang)):
        return _json_error(_('Access Denied'))

    try:
        l10n_set = L10nSettings.objects.get(locale=lang)
    except L10nSettings.DoesNotExist:
        l10n_set = L10nSettings.objects.create(locale=lang)
        l10n_set.save()

    # MOTDs are monolingual, so always store them in the default fallback
    # locale (probably en-US)
    l10n_set.motd = {settings.LANGUAGE_CODE: msg}
    l10n_set.save(force_update=True)

    data = {
        'msg': l10n_set.motd.localized_string,
        'msg_purified': unicode(l10n_set.motd)
    }

    return _json_response(data)


def _json_response(content):
    """Send an HttpResponse with json content."""
    # XXX should this be part of jingo?
    return http.HttpResponse(
        json.dumps(content), mimetype='application/json')


def _json_error(msg):
    """Send a JSON-encoded error message."""
    return _json_response({
        'error': True,
        'error_message': msg,
    })


def locale_switcher(f):
    """Decorator redirecting clicks on the locale switcher dropdown."""
    def decorated(request, *args, **kwargs):
        new_userlang = request.GET.get('userlang')
        if (new_userlang and new_userlang in settings.AMO_LANGUAGES or
            new_userlang in settings.HIDDEN_LANGUAGES):
            kwargs['locale_code'] = new_userlang
            return http.HttpResponsePermanentRedirect(reverse(
                decorated, args=args, kwargs=kwargs))
        else:
            return f(request, *args, **kwargs)
    return decorated


def valid_locale(f):
    """Decorator validating locale code for per-language pages."""
    def decorated(request, locale_code, *args, **kwargs):
        if locale_code not in (settings.AMO_LANGUAGES +
                               settings.HIDDEN_LANGUAGES):
            raise http.Http404
        return f(request, locale_code, *args, **kwargs)
    return decorated


@locale_switcher
@valid_locale
def locale_dashboard(request, locale_code):
    """per-locale dashboard"""
    data = {
        'locale_code': locale_code,
        'userlang': product_details.languages[locale_code],
    }

    # recent activity
    q = L10nEventlog.objects.exclude(type='stats').filter(
        locale=locale_code).order_by('-created')
    activity = amo.utils.paginate(request, q, 8)
    data['activity'] = activity

    # group members
    try:
        group = Group.objects.get(
            rules__startswith=('Localizers:%s' % locale_code))
        members = group.users.all()
    except Group.DoesNotExist:
        members = None
    data['members'] = members

    # team homepage
    try:
        l10n_set = L10nSettings.objects.get(locale=locale_code)
        team_homepage = l10n_set.team_homepage
    except L10nSettings.DoesNotExist:
        team_homepage = None
    data['team_homepage'] = team_homepage

    return jingo.render(request, 'localizers/dashboard.html', data)


def _build_gettext_string_dict(locale_code):
    """Build a string dictionary from a .po file."""
    locale_code = locale_code.replace('-', '_')
    po_path = lambda lang: os.path.join(
        settings.ROOT, 'locale', lang, 'LC_MESSAGES',
        '%s.po' % settings.TEXT_DOMAIN)
    with open(po_path(locale_code)) as f:
        locale_raw = f.read()

    # Remove header.
    try:
        post_header_idx = locale_raw.index("\n\n")
        locale_raw = locale_raw[post_header_idx:]
    except ValueError:
        pass

    locale_regex = re.compile(
        r'msgid\s+"(.+?)"\s*(?:msgid_plural\s+"(?:.+?)"\s*)?'
        '(?:msgstr(?:\[\d+\])? "(.+?)"\s*)+(?:#|msg)',
        re.IGNORECASE | re.DOTALL)

    locale_matches = locale_regex.findall(locale_raw)
    locale_strings = dict(locale_matches)

    return locale_strings


@locale_switcher
@valid_locale
def gettext(request, locale_code):
    """Overview of untranslated Gettext strings."""
    default_locale = settings.LANGUAGE_CODE
    data = {
        'default_locale': default_locale,
        'locale_code': locale_code,
        'userlang': product_details.languages[locale_code],
    }

    # Read en-US and localized .po file
    locale_strings = _build_gettext_string_dict(locale_code)
    default_strings = _build_gettext_string_dict(default_locale)

    # Compare
    untranslated = [ s for s in default_strings if
                     s not in locale_strings or not locale_strings[s] ]
    untranslated.sort()
    data['untranslated'] = untranslated

    # Stats
    total = len(default_strings)
    translated_count = total - len(untranslated)
    translated_percent = float(translated_count) / float(total) * 100
    data.update({
        'total': total,
        'translated_count': translated_count,
        'translated_percent': translated_percent,
    })

    return jingo.render(request, 'localizers/gettext.html', data)


@locale_switcher
@valid_locale
def categories(request, locale_code):
    return http.HttpResponse(
        'this is the categories dashboard for %s' % locale_code)


@locale_switcher
@valid_locale
def collection_features(request, locale_code):
    return http.HttpResponse(
        'this is the collection feat. dashboard for %s' % locale_code)


@require_POST
@valid_locale
def xenophobia(request, locale_code):
    if not acl.action_allowed(request, 'Admin', 'EditAnyLocale'):
        return http.HttpResponseForbidden()

    try:
        conf = Config.objects.get(pk='xenophobia')
    except Config.DoesNotExist:
        conf = Config.objects.create(key='xenophobia', value='')

    new_xeno = conf.json or {}
    new_xeno[locale_code] = 'xenophobia' in request.POST

    conf.value = json.dumps(new_xeno)
    conf.save()

    # TODO use a 303 redirect here eventually (Django ticket #13277)
    return http.HttpResponseRedirect(reverse(
        'localizers.locale_dashboard', kwargs={'locale_code': locale_code}))

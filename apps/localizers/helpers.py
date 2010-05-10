from django.conf import settings
from django.utils import translation

import jinja2
from jingo import register, env
import product_details

from access import acl
from zadmin.models import Config

from . import L10N_CATEGORIES
from .models import L10nSettings, L10nEventlog


@register.inclusion_tag('localizers/summary_sidebar.html')
@jinja2.contextfunction
def localizers_summary_sidebar(context):
    """Sidebar on the global localizer summary page."""
    ctx = dict(context.items())
    show_edit = acl.action_allowed(context['request'], 'Admin',
                                   'EditAnyLocale')
    ctx['show_edit'] = show_edit
    return ctx


@register.inclusion_tag('localizers/dashboard_sidebar.html')
@jinja2.contextfunction
def localizers_dashboard_sidebar(context, locale_code):
    """Sidebar on the per-locale localizer dashboard page."""
    ctx = dict(context.items())
    request = context['request']
    show_global_edit = acl.action_allowed(request, 'Admin', 'EditAnyLocale')
    show_local_edit = (show_global_edit or
                       acl.action_allowed(request, 'Localizers', locale_code))

    lang_stats = []
    for category, cat_name in L10N_CATEGORIES:
        stats_event = L10nEventlog.objects.filter(
            type='stats', action=category, locale=locale_code).order_by(
            '-created').only('notes')[:1]
        if stats_event:
            percentage = float(stats_event[0].notes)
            upwidth = max(0, percentage-1)
            downwidth = max(0, 100-percentage-1)
            lang_stats.append({
                'category': category,
                'name': cat_name,
                'percentage': percentage,
                'upwidth': upwidth,
                'downwidth': downwidth
            })

    # Xenophobia
    conf = Config.objects.get(pk='xenophobia')
    xenophobia = conf.json.get(locale_code, False)

    ctx.update({
        'show_global_edit': show_global_edit,
        'show_local_edit': show_local_edit,
        'locale_code': locale_code,
        'lang_stats': lang_stats,
        'xenophobia': xenophobia,
    })
    return ctx


@register.inclusion_tag('localizers/sidebar_motd.html')
@jinja2.contextfunction
def localizers_sidebar_motd(context, lang='', show_edit=False, extraclass=None):
    """Message of the Day on localizer dashboards."""
    try:
        l10n_set = L10nSettings.objects.get(locale=lang)
        motd = l10n_set.motd
    except L10nSettings.DoesNotExist:
        motd = None

    ctx = dict(context.items())
    ctx.update({
        'show_edit': show_edit,
        'motd_lang': lang,
        'motd': motd,
        'extraclass': extraclass
    })
    return ctx


@register.inclusion_tag('localizers/locale_switcher.html')
def locale_switcher(current_locale=None):
    """Locale dropdown to switch user locale on localizer pages."""
    return {
        'current_locale': current_locale,
        'locales': settings.AMO_LANGUAGES + settings.HIDDEN_LANGUAGES,
        'languages': product_details.languages,
    }

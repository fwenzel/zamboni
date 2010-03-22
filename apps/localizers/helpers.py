from django.utils import translation

import jinja2
from jingo import register, env

from access import acl
from . import L10N_CATEGORIES
from .models import L10nSettings, L10nEventlog


@register.function
@jinja2.contextfunction
def localizers_summary_sidebar(context):
    """Sidebar on the global localizer summary page."""
    request = context['request']
    show_edit = acl.action_allowed(request, 'Admin', 'EditAnyLocale')
    ctx = {
        'request': request,
        'show_edit': show_edit
    }
    t = env.get_template('localizers/summary_sidebar.html')
    return jinja2.Markup(t.render(**ctx))


@register.function
@jinja2.contextfunction
def localizers_dashboard_sidebar(context, locale_code):
    """Sidebar on the per-locale localizer dashboard page."""
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

    ctx = {
        'show_global_edit': show_global_edit,
        'show_local_edit': show_local_edit,
        'locale_code': locale_code,
        'lang_stats': lang_stats,
        'members': context['members'],
        'request': request,
        'LANG': context['LANG'],
    }

    t = env.get_template('localizers/dashboard_sidebar.html')
    return jinja2.Markup(t.render(**ctx))


@register.function
@jinja2.contextfunction
def localizers_sidebar_motd(context, lang='', show_edit=False, extraclass=None):
    """Message of the Day on localizer dashboards."""
    try:
        l10n_set = L10nSettings.objects.get(locale=lang)
        motd = l10n_set.motd
    except L10nSettings.DoesNotExist:
        motd = None

    ctx = {
        'show_edit': show_edit,
        'motd_lang': lang,
        'motd': motd,
        'extraclass': extraclass
    }

    t = env.get_template('localizers/sidebar_motd.html')
    return jinja2.Markup(t.render(**ctx))

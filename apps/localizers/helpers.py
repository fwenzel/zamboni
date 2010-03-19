import jinja2
from jingo import register, env

from .models import L10nSettings


@register.function
@jinja2.contextfunction
def l10n_summary_sidebar(context):
    """Sidebar on the global localizer summary page."""
    t = env.get_template('localizers/summary_sidebar.html')
    return jinja2.Markup(t.render(**context))


@register.function
@jinja2.contextfunction
def l10n_sidebar_motd(context, lang='', show_edit=False):
    """Message of the Day on localizer dashboards."""
    try:
        l10n_set = L10nSettings.objects.get(locale=lang)
        motd = l10n_set.motd
    except L10nSettings.DoesNotExist:
        motd = None

    t = env.get_template('localizers/sidebar_motd.html')
    return jinja2.Markup(t.render(show_edit=show_edit, motd_lang=lang,
                                  motd=motd, **context))

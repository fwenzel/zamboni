from django.conf.urls.defaults import patterns, url, include

from . import views

# These will all start with /localizers/<locale_code>/
detail_patterns = patterns('',
    url('^$', views.locale_dashboard, name='l10n.locale_dashboard'),
    url('^gettext/$', views.gettext, name='l10n.gettext'),
    url('^categories/$', views.gettext, name='l10n.categories'),
    url('^collection_features/$', views.gettext,
        name='l10n.collection_features'),
    url('^pages/$', views.gettext, name='l10n.pages'),
)


urlpatterns = patterns('',
    # URLs for a single user.
    ('^localizers/(?P<locale_code>[\w-]+)/', include(detail_patterns)),

    url('^localizers/set_motd$', views.set_motd, name='l10n.set_motd'),
    url('^localizers/$', views.summary, name='l10n.dashboard'),
)

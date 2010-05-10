from django.conf.urls.defaults import patterns, url, include

from . import views

# These will all start with /localizers/<locale_code>/
detail_patterns = patterns('',
    url('^$', views.locale_dashboard, name='localizers.locale_dashboard'),
    url('^gettext/$', views.gettext, name='localizers.gettext'),
    url('^categories/$', views.categories, name='localizers.categories'),
    url('^collection_features/$', views.collection_features,
        name='localizers.collection_features'),
    url('^xenophobia/$', views.xenophobia, name='localizers.xenophobia'),
)

urlpatterns = patterns('',
    # URLs for a single user.
    ('^localizers/(?P<locale_code>[\w-]+)/', include(detail_patterns)),

    url('^localizers/set_motd$', views.set_motd, name='localizers.set_motd'),
    url('^localizers/$', views.summary, name='localizers.dashboard'),
)

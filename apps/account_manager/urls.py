from django.conf.urls.defaults import patterns, url

import jingo

from . import views


urlpatterns = patterns('',
    url('^.well-known/host-meta$', views.host_meta, name='host-meta'),
    url('^account-manager/amcd.json$', views.amcd, name='am.amcd'),
    url('^account-manager/sessionstatus$', views.session_status,
        name='am.sessionstatus'),
)

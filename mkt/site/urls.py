from urlparse import urlparse

from django.conf import settings
from django.conf.urls import patterns, url

import jingo

from mkt.account.views import feedback
from . import views


def template_plus_xframe(request, template, **kwargs):
    res = jingo.render(request, template, kwargs)
    referrer = request.META.get('HTTP_REFERER')
    if referrer:
        referrer = urlparse(referrer).netloc
        if referrer in settings.LEGAL_XFRAME_ALLOW_FROM:
            res['x-frame-options'] = 'allow-from %s' % referrer
    return res


urlpatterns = patterns('',
    url('^mozmarket.js$', views.mozmarket_js, name='site.mozmarket_js'),
    url('^privacy-policy$', template_plus_xframe,
        {'template': 'site/privacy-policy.html'}, name='site.privacy'),
    url('^terms-of-use$', template_plus_xframe,
        {'template': 'site/terms-of-use.html'}, name='site.terms'),
    url('^robots.txt$', views.robots, name='robots.txt'),
    url('^manifest.webapp$', views.manifest, name='manifest.webapp'),
    url('^timing/record$', views.record, name='mkt.timing.record'),
    url('^feedback$', feedback, name='site.feedback'),
)

from django.contrib.auth import views as auth_views
from django.conf.urls.defaults import patterns, url, include

import jingo
from jingo.views import direct_to_template

from zadmin import jinja_for_django

from . import forms, views

# So we can use the contrib logic for password resets, etc.
auth_views.render_to_response = jinja_for_django


# These will all start with /user/<user_id>/
detail_patterns = patterns('',
    url('^$', views.profile, name='users.profile'),
    url('^confirm/resend$', views.confirm_resend, name='users.confirm.resend'),
    url('^confirm/(?P<token>[-\w]+)$', views.confirm, name='users.confirm'),
    url(r'^emailchange/(?P<token>[-\w]+={0,3})/(?P<hash>[\w]+)$',
                        views.emailchange, name="users.emailchange"),
)

users_patterns = patterns('',
    url('^delete$', views.delete, name='users.delete'),
    url('^edit$', views.edit, name='users.edit'),
    url('^login', views.login, name='users.login'),
    url('^logout', views.logout, name='users.logout'),
    url('^register$', views.register, name='users.register'),
    url(r'^pwreset/?$', auth_views.password_reset,
                        {'template_name': 'users/pwreset_request.html',
                         'email_template_name': 'users/email/pwreset.ltxt',
                         'password_reset_form': forms.PasswordResetForm,
                        }, name="users.pwreset"),
    url(r'^pwresetsent$', auth_views.password_reset_done,
                        {'template_name': 'users/pwreset_sent.html'},
                        name="users.pwreset_sent"),
    url(r'^pwreset/(?P<uidb36>[-\w]+)/(?P<token>[-\w]+)$',
                        auth_views.password_reset_confirm,
                        {'template_name': 'users/pwreset_confirm.html',
                         'set_password_form': forms.SetPasswordForm,
                        }, name="users.pwreset_confirm"),
    url(r'^pwresetcomplete$', auth_views.password_reset_complete,
                        {'template_name': 'users/pwreset_complete.html'},
                        name="users.pwreset_complete"),
)

urlpatterns = patterns('',
    # URLs for a single user.
    ('^user/(?P<user_id>\d+)/', include(detail_patterns)),
    ('^users/', include(users_patterns)),

    # Account Manager
    url('^.well-known/host-meta$', jingo.render, {
        'template': 'account-manager/host-meta.xml',
        'mimetype': 'text/xml'}, name='host-meta'),
    url('^account-manager/amcd.json$', jingo.render, {
        'template': 'account-manager/amcd.json',
        'mimetype': 'application/json'}, name='am.amcd'),
    url('^account-manager/sessionstatus$', views.session_status,
        name='am.sessionstatus'),
)

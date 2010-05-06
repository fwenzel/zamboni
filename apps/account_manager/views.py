"""
Weave Account Manager.
Specs: https://wiki.mozilla.org/Labs/Weave/Identity/Account_Manager/Spec/Latest
"""

import json
from xml.dom import minidom

from django import http
from django.views.decorators.cache import never_cache

from amo.urlresolvers import reverse

from .decorators import account_management_status


def host_meta(request):
    """
    Site-wide metadata discovery document.
    cf. http://tools.ietf.org/html/draft-hammer-hostmeta-06
    """
    # Create an xml doc pointing to the AMCD.
    doc = minidom.Document()

    xrd = doc.createElement('XRD')
    xrd.setAttribute('xmlns', 'http://docs.oasis-open.org/ns/xri/xrd-1.0')
    doc.appendChild(xrd)

    link = doc.createElement('Link')
    link.setAttribute('rel', 'http://services.mozilla.com/amcd/0.1')
    link.setAttribute('href', reverse('am.amcd'))
    xrd.appendChild(link)

    return http.HttpResponse(doc.toxml(), mimetype='text/xml')


def amcd(request):
    """Account Manager Control Document"""
    amcd_data = {
        'methods': {
            'username-password-form': {
                'connect': {
                    'method': 'POST',
                    'path': reverse('users.login'),
                    'params': {
                        'username': 'username',
                        'password': 'password',
                        'token': 'csrfmiddlewaretoken'
                    }
                },
                'disconnect': {
                    'method': 'GET',
                    'path': reverse('users.logout')
                },
                'changepassword': {
                    'method': 'POST',
                    'path': reverse('users.edit'),
                    'params': {
                        'username': 'email',
                        'old_password': 'oldpassword',
                        'password': 'password',
                        'password_verify': 'password2'
                    }
                },
                'sessionstatus': {
                    'method': 'GET',
                    'path': reverse('am.sessionstatus')
                },
            }
        }
    }

    return http.HttpResponse(json.dumps(amcd_data), mimetype='application/json')


@account_management_status
@never_cache
def session_status(request):
    """Account Manager sessionstatus method"""
    # An empty response will do: The magic is in the headers.
    return http.HttpResponse()

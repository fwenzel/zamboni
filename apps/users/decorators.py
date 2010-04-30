from django.core.context_processors import csrf
from django.views.decorators.vary import vary_on_cookie


def account_management_status(f):
    """
    View decorator adding an X-Account-Management-Status header.
    """
    @vary_on_cookie
    def decorated(request, *args, **kwargs):
        resp = f(request, *args, **kwargs)
        if request.user.is_authenticated():
            resp['X-Account-Management-Status'] = 'active; name="%s"' % (
                request.user.get_profile().name)
        else:
            token = csrf(request)['csrf_token']
            resp['X-Account-Management-Status'] = 'none; token="%s"' % token
        return resp

    return decorated

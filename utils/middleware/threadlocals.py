import settings
from django.contrib.auth.models import User, AnonymousUser
# threadlocals middleware

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def get_current_user():
    return getattr(_thread_locals, 'user', None) or _get_admin_user()

def set_current_user(user):
    _thread_locals.user = user or AnonymousUser()

def _get_admin_user():
    try:
        assert settings.DEBUG
        return User.objects.get(username=settings.ADMINS[0][0])
    except:
        return None

class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_request(self, request):
        set_current_user(getattr(request, 'user', None))
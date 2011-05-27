from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model

class CustomUserInterface(object):
    def get_user(self, user_id):
        try:
            return self.user_class.objects.get(pk=user_id)
        except self.user_class.DoesNotExist:
            return None

    @property
    def user_class(self):
        if not hasattr(self, '_user_class'):
            if hasattr(settings, 'CUSTOM_USER_MODEL'):
                self._user_class = get_model(*settings.CUSTOM_USER_MODEL.split('.', 2))
                if not self._user_class:
                    raise ImproperlyConfigured('Could not get custom user model')
            else:
                self._user_class = User
        return self._user_class

class CustomUserModelBackend(ModelBackend, CustomUserInterface):
    '''
    Extending django.auth.ModelBackend to allow use custom user model
    '''
    def authenticate(self, username=None, password=None):
        try:
            user = self.user_class.objects.get(username=username)
            if user.check_password(password):
                return user
        except self.user_class.DoesNotExist:
            return None

if 'netauth' in settings.INSTALLED_APPS:
    '''
    Extending netauth.auth.NetBackend to allow use custom user model
    '''
    from netauth.auth import NetBackend
    class CustomUserNetBackend(NetBackend, CustomUserInterface):
        pass


from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
try:
    ''' after django 1.2 alfa release '''
    from django.core.validators import email_re
except:
    from django.forms.fields import email_re

class EmailBackend(CustomUserModelBackend):
    def authenticate(self, username=None, password=None):
        if email_re.search(username):
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}

        try:
            user = self.user_class.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except self.user_class.DoesNotExist:
            return None
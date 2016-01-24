from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CustomUserInterface(object):
    def get_user(self, user_id):
        try:
            return self.user_class.objects.get(pk=user_id)
        except self.user_class.DoesNotExist:
            return None

    @property
    def user_class(self):
        return get_user_model()

class CustomUserModelBackend(CustomUserInterface, ModelBackend):
    '''
    Extending django.auth.ModelBackend to allow use custom user model
    '''
    supports_inactive_user = False
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
    class CustomUserNetBackend(CustomUserInterface, NetBackend):
        supports_inactive_user = False


from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class EmailBackend(CustomUserModelBackend):
    supports_inactive_user = False
    def authenticate(self, username=None, password=None):
        try:
            validate_email(username)
            kwargs = {'email': username}
        except ValidationError:
            kwargs = {'username': username}
        try:
            user = self.user_class.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except self.user_class.DoesNotExist:
            return None

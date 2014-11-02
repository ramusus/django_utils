from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.http import HttpResponseRedirect,HttpResponse
from django.middleware.locale import LocaleMiddleware
from django.conf import settings
import re

if not hasattr(settings, 'LANGUAGES_BY_DOMAIN'):
    raise ImportError('You must specified LANGUAGES_BY_DOMAIN in settings.py')

class LocaleBySubdomainMiddleware(LocaleMiddleware):

    def process_request(self, request):

        language = settings.LANGUAGES_BY_DOMAIN.get('')

        if request.META.get('SERVER_NAME', None) != 'testserver':
            subdomain = re.sub(r'%s(:\d+)?$' % getattr(settings, 'ACCOUNT_DOMAIN', ''), '', request.META.get('HTTP_HOST', ''))
            if subdomain in settings.LANGUAGES_BY_DOMAIN.keys():
                language = settings.LANGUAGES_BY_DOMAIN.get(subdomain)

        if isinstance(language, tuple) and len(language) == 2:
            language, settings.SITE_ID = language

        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
        settings.LANGUAGE_CODE = request.LANGUAGE_CODE
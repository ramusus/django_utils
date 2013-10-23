# -*- coding: utf-8 -*-
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.utils import translation

try:
    import json
except ImportError:
    from django.utils import simplejson as json

from decorators import render_to, ajax_required, json_success_error

def is_language(code):
    return translation.get_language().find(code) > -1

def dict_with_keys(dictionary, keys=None, **kwargs):
    return dict([(k,v) for k,v in dictionary.items() if k in (keys or [])], **kwargs)

from pytils.numeral import get_plural as pytils_get_plural, choose_plural as pytils_choose_plural
from django.utils.functional import Promise
def get_plural(amount, variants, absence=None):
    '''
    Wrapper for pytils.numeral.get_plural for accepting Django Translating Proxy instances in arguments
    Use simple algorithm if LANGUAGE_CODE is not 'ru'
    '''
    if amount or absence is None:
        return u"%d %s" % (amount, choose_plural(amount, variants))
    else:
        if isinstance(absence, Promise):
            absence = unicode(absence)
        return absence

def choose_plural(amount, variants):
    '''
    Wrapper for pytils.numeral.choose_plural for accepting Django Translating Proxy instances in arguments
    Use simple algorithm if LANGUAGE_CODE is not 'ru'
    '''
    if isinstance(variants, Promise):
        variants = unicode(variants)
    if is_language('ru'):
        return pytils_choose_plural(amount, variants)
    else:
        if not isinstance(variants, (list,tuple)):
            variants = variants.split(',')
        return variants[0] if amount == 1 else variants[1]

from django.utils.functional import Promise
class JsonResponse(HttpResponse):
    def __init__(self, object, content_type='application/json'):
        if isinstance(object, QuerySet):
            content = serialize('json', object)
        else:
            # convert all Django Translating Proxy instances to unicode strings
            if isinstance(object, dict):
                for key, val in object.items():
                    if isinstance(val, Promise):
                        object[key] = unicode(val)
            content = json.dumps(
                object, indent=2, cls=DjangoJSONEncoder,
                ensure_ascii=False)
        super(JsonResponse, self).__init__(content, content_type=content_type)

import urllib
import os
def download(url, filepath=False):
    """
    Copy the contents of a file from a given URL to a local file.
    """
    webFile = urllib.urlopen(url)

    dir = '/'.join(filepath.split('/')[:-1])
    if not os.path.isdir(dir):
        os.makedirs(dir)

    localFile = open(filepath or url.split('/')[-1], 'w')
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()

import logging
def log(message, file=False):
    '''
    Log message into specified file
    '''
    from settings import ROOT
    file = ROOT + '/logs/' + str(file or 'default.log')
    handler = logging.FileHandler(file)
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logger = logging.getLogger(file)
    logger.addHandler(handler)
    logger.info(message)
    logger.removeHandler(handler)

def pdb():
    import pdb, sys
    sys.__stdout__.write('\a')
    sys.__stdout__.flush()
    debugger = pdb.Pdb(stdin=sys.__stdin__, stdout=sys.__stdout__)
    debugger.set_trace(sys._getframe().f_back)

def load_templatetags():
    from django.conf import settings
    from django.template import add_to_builtins
    # This is important: If the function is called early, and some of the custom
    # template tags use superclasses of django template tags, or otherwise cause
    # the following situation to happen, it is possible that circular imports
    # cause problems:
    # If any of those superclasses import django.template.loader (for example,
    # django.template.loader_tags does this), it will immediately try to register
    # some builtins, possibly including some of the superclasses the custom template
    # uses. This will then fail because the importing of the modules that contain
    # those classes is already in progress (but not yet complete), which means that
    # usually the module's register object does not yet exist.
    # In other words:
    #       {custom-templatetag-module} ->
    #       {django-templatetag-module} ->
    #       django.template.loader ->
    #           add_to_builtins(django-templatetag-module)
    #           <-- django-templatetag-module.register does not yet exist
    # It is therefor imperative that django.template.loader gets imported *before*
    # any of the templatetags it registers.
    import django.template.loader

    try:
        for lib in settings.TEMPLATE_TAGS:
            add_to_builtins(lib)
    except AttributeError:
        pass

class DynamicAdminInlines:
    '''
    Интерфейс, делающий динамическое кол-во инлайн форм в админке
    '''
    class Media:
        js = ['js/dynamic_inlines_with_sort.js',]
        css = { 'all' : ['css/dynamic_inlines_with_sort.css'], }

from django.core.mail import EmailMessage
import settings
def send_mail_with_bcc(subject, message, recipients, bcc_callback=lambda:[]):
    '''
    Like send_mail(), only with bcc header
    '''
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, recipients, bcc_callback())
    email.send(fail_silently=True)
# -*- coding: utf-8 -*-
from django.core.serializers import json, serialize
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.utils import simplejson

from decorators import render_to, ajax_required

def dict_with_keys(dictionary, keys=[], **kwargs):
    return dict([(k,v) for k,v in dictionary.items() if k in keys], **kwargs)

class JsonResponse(HttpResponse):
    def __init__(self, object):
        if isinstance(object, QuerySet):
            content = serialize('json', object)
        else:
            content = simplejson.dumps(
                object, indent=2, cls=json.DjangoJSONEncoder,
                ensure_ascii=False)
        # if content_type='text/json' or content_type='application/json'
        # jquery-ajax-form-plugin does'n work with file upload:
        # window for download json file instead of success = function(json) {}
        super(JsonResponse, self).__init__(content, content_type='text/html')

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
from settings import ROOT
def log(message, file=False):
    '''
    Log message into specified file
    '''
    file = ROOT + '/logs/' + str(file or 'default.log')
    handler = logging.FileHandler(file)
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logger = logging.getLogger(file)
    logger.addHandler(handler)
    logger.info(message)
    logger.removeHandler(handler)

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
def send_mail_with_bcc(subject, message, emails_list, bcc_callback=lambda:[]):
    '''
    Like send_mail(), only with bcc feature
    '''
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, emails_list, bcc_callback())
    email.send(fail_silently=True)
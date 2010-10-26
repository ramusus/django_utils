# -*- coding: utf-8 -*-
from django.http import HttpResponseBadRequest
from django.utils.functional import wraps

def ajax_required(f):
    """
    AJAX request required decorator
    use it in your views:

    @ajax_required
    def my_view(request):
        ....

    """
    def wrap(request, *args, **kwargs):
        if not request.is_ajax() and not request.user.is_superuser and request.META.get('SERVER_NAME') != 'testserver':
            return HttpResponseBadRequest('Wrong type of request')
        return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

def json_success_error(func):
    '''
    Decorator for returning json string with success or error if exception in view raised
    '''
    def wrapper(*args, **kwargs):
        from utils import JsonResponse
        try:
            return JsonResponse({'success': func(*args, **kwargs)})
        except Exception, e:
            try:
                e = str(e)
            except:
                e = unicode(e)
            return JsonResponse({'error': e})

    return wraps(func)(wrapper)

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
#try:
#    from jinja import render_to_response
#except:
#    pass

def render_to(template):
    """
    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request))
            return output
        return wrapper
    return renderer

'''
from http://www.djangosnippets.org/snippets/1849/
'''
from django.http import HttpResponseRedirect

def anonymous_required( view_function, redirect_to = None ):
    return AnonymousRequired( view_function, redirect_to )

class AnonymousRequired( object ):
    def __init__( self, view_function, redirect_to ):
        if redirect_to is None:
            from django.conf import settings
            redirect_to = settings.LOGIN_REDIRECT_URL
        self.view_function = view_function
        self.redirect_to = redirect_to

    def __call__( self, request, *args, **kwargs ):
        if request.user is not None or request.user.is_authenticated():
            return HttpResponseRedirect( self.redirect_to )
        return self.view_function( request, *args, **kwargs )

from django.utils import translation
from celery.decorators import task
def task_respect_to_language(func):
    '''
    Decorator for
    '''
    def wrapper(*args, **kwargs):
        language = kwargs.pop('language', None)
        print language
        prev_language = translation.get_language()
        language and translation.activate(language)
        try:
            return func(*args, **kwargs)
        finally:
            translation.activate(prev_language)
    return wraps(func)(task(wrapper))
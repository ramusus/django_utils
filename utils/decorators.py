# -*- coding: utf-8 -*-
from django.http import HttpResponseBadRequest
from django.utils.functional import wraps

def opt_arguments(func):
    '''
    Meta-decorator for ablity use decorators with optional arguments
    from here http://www.ellipsix.net/blog/2010/08/more-python-voodoo-optional-argument-decorators.html
    '''
    def meta_wrapper(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            # No arguments, this is the decorator
            # Set default values for the arguments
            return func(args[0])
        else:
            def meta_func(inner_func):
                return func(inner_func, *args, **kwargs)
            return meta_func
    return meta_wrapper

def ajax_required(func):
    """
    AJAX request required decorator
    use it in your views:

    @ajax_required
    def my_view(request):
        ....

    """
    def wrapper(request, *args, **kwargs):
        if not request.is_ajax() and not request.user.is_superuser and request.META.get('SERVER_NAME') != 'testserver':
            return HttpResponseBadRequest('Wrong type of request')
        return func(request, *args, **kwargs)
    return wraps(func)(wrapper)

@opt_arguments
def json_success_error(func, content_type=None):
    '''
    Decorator for returning json string with success or error if exception in view raised
    '''
    json_kwargs = {'content_type': content_type} if content_type else {}
    def wrapper(*args, **kwargs):
        from utils import JsonResponse
        try:
            return JsonResponse({'success': func(*args, **kwargs)}, **json_kwargs)
        except Exception, e:
            try:
                e = str(e)
            except:
                e = unicode(e)
            return JsonResponse({'error': e}, **json_kwargs)
    return wraps(func)(wrapper)

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
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
        return wraps(func)(wrapper)
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
from django.utils.functional import wraps
def task_with_respect_to_language(func):
    '''
    Decorator for tasks with respect to site's current language.
    You can use in tasks.py this decorator @task_respect_to_language instead of default @task
    Be sure that task method have kwargs argument:

        @task_respect_to_language
        def my_task(...., **kwargs):
            pass

    You can call this task this way:

        from django.utils import translation
        tasks.my_task.delay(...., language=translation.get_language())
    '''
    def wrapper(*args, **kwargs):
        language = kwargs.pop('language', None)
        prev_language = translation.get_language()
        language and translation.activate(language)
        try:
            return func(*args, **kwargs)
        finally:
            translation.activate(prev_language)

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    return wraps(func)(task(wrapper))
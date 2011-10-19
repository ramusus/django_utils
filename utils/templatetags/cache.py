from django.template import Library, TemplateSyntaxError
from django.templatetags.cache import CacheNode
from django.utils.translation import get_language
from django.conf import settings

register = Library()

@register.tag('cache')
def do_cache(parser, token):
    """
    This is wrapper for default cache templatetag with transparent respect
    to the active language if USE_I18N is set to True.
    Usage the same
    """
    nodelist = parser.parse(('endcache',))
    parser.delete_first_token()
    tokens = token.contents.split()
    if len(tokens) < 3:
        raise TemplateSyntaxError(u"'%r' tag requires at least 2 arguments." % tokens[0])

    vars = tokens[3:]
    if settings.USE_I18N:
        lang = get_language()
        if lang not in vars:
            vars += [lang]

    return CacheNode(nodelist, tokens[1], tokens[2], vars)

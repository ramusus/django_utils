import hashlib
from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist, resolve_variable
from django.utils.translation import get_language
from django.core.cache import cache
from django.conf import settings
from django.utils.http import urlquote

register = Library()

class CacheNode(Node):
    def __init__(self, nodelist, expire_time_var, fragment_name, vary_on):
        self.nodelist = nodelist
        self.expire_time_var = Variable(expire_time_var)
        self.fragment_name = fragment_name
        self.vary_on = vary_on

    def render(self, context):
        try:
            expire_time = self.expire_time_var.resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError('"cache" tag got an unknown variable: %r' % self.expire_time_var.var)
        try:
            expire_time = int(expire_time)
        except (ValueError, TypeError):
            raise TemplateSyntaxError('"cache" tag got a non-integer timeout value: %r' % expire_time)

        vars = [urlquote(resolve_variable(var, context)) for var in self.vary_on]
        # add lang variable to vars if it is not inside
        if settings.USE_I18N:
            lang = get_language()
            if lang not in vars:
                vars += [lang]

        # Build a unicode key for this fragment and all vary-on's.
        args = hashlib.md5(u':'.join(vars))

        cache_key = 'template.cache.%s.%s' % (self.fragment_name, args.hexdigest())
        value = cache.get(cache_key)
        if value is None:
            value = self.nodelist.render(context)
            cache.set(cache_key, value, expire_time)
        return value

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
    return CacheNode(nodelist, tokens[1], tokens[2], tokens[3:])
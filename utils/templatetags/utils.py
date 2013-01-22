# -*- coding: utf-8 -*-
from django import template
from django.db.models.query import QuerySet
from django.template.defaultfilters import stringfilter
from django.conf import settings

register = template.Library()

@register.simple_tag
def url_obj(object):
    '''
    В отличие от тега {% url %}, работает не с view, а  возвращает относительный путь к передаваемому объекту
    '''
    try:
        return getattr(object, 'url', object.get_absolute_url())
    except:
        return '#'

@register.simple_tag
def abs_url_obj(object):
    '''
    В отличие от тега {% url %}, работает не с view, а  возвращает абсолютный путь к передаваемому объекту
    '''
    try:
        return object.get_absolute_url()
    except:
        return '#'

'''
Absolute URL Templatetag
from here http://djangosnippets.org/snippets/1518/
'''
import urlparse
from django.template.defaulttags import URLNode, url
from django.contrib.sites.models import Site

class AbsoluteURLNode(URLNode):
    def render(self, context):
        path = super(AbsoluteURLNode, self).render(context)
        domain = "http://%s" % Site.objects.get_current().domain
        return urlparse.urljoin(domain, path)

def abs_url(parser, token, node_cls=AbsoluteURLNode):
    """Just like {% url %} but ads the domain of the current site."""
    node_instance = url(parser, token)
    return node_cls(view_name=node_instance.view_name,
        args=node_instance.args,
        kwargs=node_instance.kwargs,
        asvar=node_instance.asvar)
abs_url = register.tag(abs_url)

@register.simple_tag
def join(objects, delimeter=', ', url=True, lower=False):
    '''
    Джойнит все объекты list с разделителем delimeter
    '''
    list = []
    if not objects:
        return ''
    for object in objects:
        name = object.__unicode__()
        if lower:
            name = name.lower()

        import re
        from django.utils.safestring import SafeUnicode
        if isinstance(url, SafeUnicode) and re.search('%s', url):
            list += ['<a href="%s">%s</a>' % (url % object.id, name)]
        elif isinstance(url, bool) and url:
            list += ['<a href="%s">%s</a>' % (object.get_absolute_url(), name)]
        else:
            list += [name]

    return delimeter.join(list)

@register.simple_tag
def select(objects, name, class_name='', null_sign=False):
    '''
    Output <select> tag with options from queryset objects or 2-tuple ((id, value),)
    '''
    str = ''
    option_tag = '<option value="%s">%s</option>'

    if null_sign:
        str += option_tag % ('', null_sign)

    if isinstance(objects, QuerySet):
        for object in objects:
           str += option_tag % (object.id, object.__unicode__())
    else:
        for id, value in objects:
           str += option_tag % (id, value)

    str = '<select %s name="%s">%s</select>' % (class_name and 'class="%s"' % class_name or '', name, str);
    return str

'''
from http://www.djangosnippets.org/snippets/1702/
'''

@register.filter(name='indent')
@stringfilter
def indent(value, arg=1):
    """
    Template filter to add the given number of tabs to the beginning of
    each line. Useful for keeping markup pretty, plays well with Markdown.

    Usage:
    {{ content|indent:"2" }}
    {{ content|markdown|indent:"2" }}
    """
    import re
    regex = re.compile("^", re.M)
    return re.sub(regex, "\t"*int(arg), value)

'''
from http://github.com/sku/python-twitter-ircbot/blob/321d94e0e40d0acc92f5bf57d126b57369da70de/html_decode.py
'''

from htmlentitydefs import name2codepoint as n2cp
import re

@register.filter(name='decode_entities')
@stringfilter
def decode_htmlentities(string):
    """
Decode HTML entities–hex, decimal, or named–in a string
@see http://snippets.dzone.com/posts/show/4569
>>> u = u'E tu vivrai nel terrore - L&#x27;aldil&#xE0; (1981)'
>>> print decode_htmlentities(u).encode('UTF-8')
E tu vivrai nel terrore - L'aldilà (1981)
>>> print decode_htmlentities("l&#39;eau")
l'eau
>>> print decode_htmlentities("foo &lt; bar")
foo < bar
"""
    def substitute_entity(match):
        ent = match.group(3)
        if match.group(1) == "#":
            # decoding by number
            if match.group(2) == '':
                # number is in decimal
                return unichr(int(ent))
            elif match.group(2) == 'x':
                # number is in hex
                return unichr(int('0x'+ent, 16))
        else:
            # they were using a name
            cp = n2cp.get(ent)
            if cp: return unichr(cp)
            else: return match.group()

    entity_re = re.compile(r'&(#?)(x?)(\w+);')
    return entity_re.subn(substitute_entity, string)[0]

from pytils.templatetags.pytils_dt import ru_strftime, distance_of_time
from django.utils.datetime_safe import strftime
from django.utils.translation import ugettext as _
import datetime
from .. import is_language
@register.filter
def smart_time(date):
    """
    Cover for ru_strftime from pytils. Don't show needless part of time string
    """
    now = datetime.datetime.now(date.tzinfo)
    today = now.replace(hour=0, minute=0, second=0)
    if date > now - datetime.timedelta(hours=2) and is_language('ru'):
        # from 2 hours ago to now
        return distance_of_time(date)
    elif date > today:
        # from start of today to 2 hours ago
        format = u'%H:%M'
    elif date > today - datetime.timedelta(days=1):
        # yesterday
        format = _('yesterday') + u', %H:%M'
    elif date > today - datetime.timedelta(days=2):
        # the day before yesterday
        format = _('day before yesterday') + u', %H:%M'
    elif date > today.replace(day=1, month=1):
        # this year
        format = u'%d %B, %H:%M'
    else:
        format = u'%d %B %Y, %H:%M'

    if is_language('ru'):
        return ru_strftime(date, format)
    else:
        return strftime(date, format)

from django import template, conf
from pytils import dt
from pytils.templatetags import pseudo_str, pseudo_unicode
encoding = conf.settings.DEFAULT_CHARSET  #: Current charset (sets in Django project's settings)
@register.filter
def ru_strftime_month(date, format="%B", inflected_day=False, preposition=False):
    """
    Cover for ru_strftime from pytils. Differences: inflected=False and another format by default
    """
    try:
        uformat = pseudo_unicode(format, encoding, u"%d.%m.%Y")
        ures = dt.ru_strftime(uformat,
                              date,
                              inflected=False,
                              inflected_day=inflected_day,
                              preposition=preposition)
        res = pseudo_str(ures, encoding)
    except Exception, err:
        # because filter must die silently
        try:
            default_distance = "%s seconds" % str(int(time.time() - from_time))
        except Exception:
            default_distance = ""
        res = default_value % {'error': err, 'value': default_distance}
    return res

@register.filter(name='int')
def to_integer(value):
    '''
    Convert value to integer
    '''
    return int(value)

@register.filter(name='str')
def to_string(value):
    '''
    Convert value to string
    '''
    return str(value)

@register.filter(name='plus')
def plus(value, argument):
    '''
    Plus argument to value
    '''
    return value + int(argument)

#@register.filter
#def dev(value):
#    '''
#    Convert value to decimal
#    '''
#    return dec(value)

'''
from here http://stackoverflow.com/questions/1259219/django-datefield-to-unix-timestamp
'''
import time
@register.filter
def epoch(value):
    try:
        return int(time.mktime(value.timetuple())*1000)
    except AttributeError:
        return ''

'''
from here http://www.jongales.com/blog/2009/10/19/percentage-django-template-tag/
'''
@register.filter(name='percentage')
def percentage(fraction, population):
    try:
        return "%.0f%%" % ((float(fraction) / float(population)) * 100) if population else 0
    except ValueError:
        return ''

'''
from here http://stackoverflow.com/questions/346467/format-numbers-in-django-templates
'''
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
import re
@register.filter('intspace')
def intspace(value):
    """
    Converts an integer to a string containing spaces every three digits.
    For example, 3000 becomes '3 000' and 45000 becomes '45 000'.
    See django.contrib.humanize app
    """
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1> \g<2>', orig)
    if orig == new:
        return mark_safe(new)
    else:
        return mark_safe(intspace(new))


from django.contrib.markup.templatetags.markup import textile
from django.utils.safestring import mark_safe

@register.filter
@stringfilter
def textile_fix_dashes(value):
    '''
    >>> from utils.templatetags.utils import textile_fix_dashes
    >>> textile_fix_dashes('2000-2009 2000--2009 first - second first -- second first-second :-)')
    u'<p>2000&ndash;2009 2000&ndash;2009 first &mdash; second first &mdash; second first-second :-)</p>'
    '''
    for match, before, dash, after in re.findall(r'((.)(\-{1,2})(.))', value):
        if before == after == ' ':
            symbol = '&mdash;'
        else:
            try:
                assert isinstance(int(before), int)
                assert isinstance(int(after), int)
                symbol = '&ndash;'
            except:
                symbol = 'shortdash;'

        value = value.replace(match, '%s%s%s' % (before, symbol, after))
    value = textile(value).replace('shortdash;','-')
    return mark_safe(value)

'''
From here http://djangosnippets.org/snippets/620/
'''
@register.tag
def smartspaceless(parser, token):
    nodelist = parser.parse(('endsmartspaceless',))
    parser.delete_first_token()
    return SmartSpacelessNode(nodelist)

class SmartSpacelessNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        s = self.nodelist.render(context).strip()
        inline_tags = 'a|b|i|u|em|strong|sup|sub|tt|font|small|big'
        inlines_with_spaces = r'</(%s)>\s+<(%s)\b' % (inline_tags, inline_tags)
        s = re.sub(inlines_with_spaces, r'</\1>&#preservespace;<\2', s)
        s = re.sub(r'>\s+<', '><', s)
        s = s.replace('&#preservespace;', ' ')
        return s


@register.filter
def add_finish_link(value, arg):
    """
    Add link to the end of text

    Receives a parameter separated by spaces where each field means:
    - number: number of words which necessary to wrap into link
    - url: url for link
    """
    try:
        args = arg.split(' ')
        assert len(args) == 2
        number = int(args[0])
        url = args[1]
    except ValueError: # Invalid literal for int().
        return value
    except AssertionError: # More than 2 arguments
        return value

    words = value.split(' ')
    return '%s <a href="%s">%s</a>' % (' '.join(words[:-number]), url, ' '.join(words[-number:]))

'''
Unescape filter from https://code.djangoproject.com/attachment/ticket/4555/django-unescape.patch
'''
from django.utils.safestring import mark_for_escaping

def unescape(html):
    "Returns the given HTML with ampersands, quotes and carets decoded"
    html = unicode(html)
    return html.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;',"'")

@register.filter(name='unescape')
@stringfilter
def unescape_filter(value):
    "Unescapes a string's HTML"
    return unescape(value)
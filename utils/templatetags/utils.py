# -*- coding: utf-8 -*-
from django import template
from django.db.models.query import QuerySet
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.simple_tag
def url_obj(object):
    '''
    В отличие от тега {% url %}, работает не с view, а  возвращает абсолютный путь к передаваемому объекту
    '''
    try:
        return object.get_absolute_url()
    except:
        return '#'

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
import datetime
@register.filter
def smart_time(date):
    """
    Cover for ru_strftime from pytils. Don't show needless part of time string
    """
    if date.tzinfo:
        now = datetime.datetime.now(date.tzinfo)
    else:
        now = datetime.datetime.now()

    today = now.replace(hour=0, minute=0, second=0)
    if date > now - datetime.timedelta(hours=2):
        ''' from 2 hours ago to now '''
        return distance_of_time(date)
    elif date > today:
        ''' from start of today to 2 hours ago '''
        format = '%H:%M'
    elif date > today - datetime.timedelta(days=1):
        ''' yesterday '''
        format = u'вчера, %H:%M'
    elif date > today - datetime.timedelta(days=2):
        ''' the day before yesterday '''
        format = u'позавчера, %H:%M'
    elif date > today.replace(day=1, month=1):
        ''' this year '''
        format = '%d %B, %H:%M'
    else:
        format = '%d %B %Y, %H:%M'
    return ru_strftime(date, format)

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
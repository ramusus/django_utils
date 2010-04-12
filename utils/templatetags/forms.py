# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='class')
def className(value, className):
    value = re.sub(r'>$', ' class="%s">' % str(className), str(value))
    return mark_safe(value)
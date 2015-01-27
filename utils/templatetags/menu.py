# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse
from django.utils.functional import wraps
from ..__init__ import dict_with_keys
import re

register = template.Library()

def prepare_menu_item(func):
    '''Decorator for menu item with 3 states: link, active, active with link'''
    def wrapper(context, title, url, pattern=False):
        additional = func(context, title, url, pattern)
        try:
            url = reverse(url, args=additional.get('reverse_args'))
        except:
            pass

        active = context['request'].path == url
        active_url = pattern and re.match(pattern, context['request'].path)
        return dict_with_keys(locals(), ['active','active_url','url','title'])

    return wraps(func)(wrapper)

'''
Template tags for generating menu item with 3 potential states: link, active, active with link
'''

@register.inclusion_tag('menu_item.html', takes_context=True)
@prepare_menu_item
def menu_item(context, title, url, pattern=False):
    return {}

@register.inclusion_tag('tab_item.html', takes_context=True)
@prepare_menu_item
def tab_item(context, title, url, pattern=False):
    return {
        'reverse_args': (context.get('object').id,),
    }
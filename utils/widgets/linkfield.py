# -*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
import re

'''
LinkFieldWidget - A TextField widget with previewing link, generated from field's value with special url mask
'''

class LinkFieldWidget(Widget):
    def __init__(self, text, url='%s', *args, **kwargs):
        self.url = url
        self.text = text
        if not re.search('%', self.url):
            raise forms.ValidationError, u'Invalid URL mask'
        super(LinkFieldWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        output = []
        replace_pattern = self.url.replace('?', '\?').replace('%s', '(.+)').replace('http://','(?:http://)?').replace('www','(?:www)?').replace('/', '\/')
        output.append('''<input type="text" name="%s" value="%s" onkeyup="this.value = this.value.replace(/^%s/i, '$1'); $('a#%s-link').attr('href', '%s'.replace('%s', this.value)).css({'display': (this.value ? 'inline' : 'none')})" />''' % (name, value or '', replace_pattern, name, self.url, '%s'))
        if self.url and self.text:
            output.append('<a href="%s" id="%s-link" class="url" target="blank" style="display: %s;">%s</a>' % (value and self.url % value or '#', name, value and 'inline' or 'none', self.text))

        return mark_safe(u' '.join(output))
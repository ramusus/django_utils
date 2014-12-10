# -*- coding: utf-8 -*-
'''
Before Django 1.4. Start from 1.4 use filters
From here http://www.djangosnippets.org/snippets/1051/
'''

# Authors: Marinho Brandao <marinho at gmail.com>
#          Guilherme M. Gondim (semente) <semente at taurinus.org>
# File: <your project>/admin/filterspecs.py

from django.db import models
from django.contrib.admin.filterspecs import FilterSpec, ChoicesFilterSpec
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _

class AlphabeticFilterSpec(ChoicesFilterSpec):
    """
    Adds filtering by first char (alphabetic style) of values in the admin
    filter sidebar. Set the alphabetic filter in the model field attribute
    'alphabetic_filter'.

    my_model_field.alphabetic_filter = True
    """

    def __init__(self, f, request, params, model, model_admin, *args, **kwargs):
        super(AlphabeticFilterSpec, self).__init__(f, request, params, model,
                                                   model_admin, *args, **kwargs)
        self.lookup_kwarg = '%s__istartswith' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        values_list = model.objects.values_list(f.name, flat=True)
        # getting the first char of values
        self.lookup_choices = list(set(val[0] for val in values_list if val))
        self.lookup_choices.sort()

    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
                'display': _('All')}
        for val in self.lookup_choices:
            yield {'selected': smart_unicode(val) == self.lookup_val,
                    'query_string': cl.get_query_string({self.lookup_kwarg: val}),
                    'display': val.upper()}
    def title(self):
        return _('%(field_name)s that starts with') % \
            {'field_name': self.field.verbose_name}

# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'alphabetic_filter', False),
                                   AlphabeticFilterSpec))

'''
From here: http://www.djangosnippets.org/snippets/1270/
edited
'''

class NullFilterSpec(FilterSpec):
    def __init__(self, f, request, *args, **kwargs):
        super(NullFilterSpec, self).__init__(f, request, *args, **kwargs)
        self.lookup_kwarg = '%s__isnull' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)

    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
               'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
               'display': _('All')}
        for k, v in (('True',_('Without value')),('',_('With value'))):
            yield {'selected': k == self.lookup_val,
                    'query_string': cl.get_query_string({self.lookup_kwarg: k}),
                    'display': v}

FilterSpec.register(lambda f: f.null, NullFilterSpec)

'''
Фильтр кол-ва связанных объектов
'''
class CountRelatedFilterSpec(FilterSpec):
    def __init__(self, f, request, *args, **kwargs):
        super(CountRelatedFilterSpec, self).__init__(f, request, *args, **kwargs)
        self.lookup_kwarg = '%s__exact' % f.name
        self.lookup_kwarg2 = '%s__gte' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_val2 = request.GET.get(self.lookup_kwarg2, None)

    def choices(self, cl):
        yield {'selected': self.lookup_val is None and self.lookup_val2 is None,
               'query_string': cl.get_query_string({}, [self.lookup_kwarg, self.lookup_kwarg2]),
               'display': _('All')}
        for k, v in ((0,_('0 related')),(1,_('1 related')),(2,_('More than 1 related'))):
            if k == 2:
                lookup_kwarg = self.lookup_kwarg2
                lookup_kwarg2 = self.lookup_kwarg
            else:
                lookup_kwarg = self.lookup_kwarg
                lookup_kwarg2 = self.lookup_kwarg2
            yield {'selected': self.lookup_val and k == int(self.lookup_val) or self.lookup_val2 and k == int(self.lookup_val2),
                   'query_string': cl.get_query_string({lookup_kwarg: k}, [lookup_kwarg2]),
                   'display': v}
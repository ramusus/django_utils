# -*- coding: utf-8 -*-

# use https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
# https://code.djangoproject.com/browser/django/trunk/django/contrib/admin/filters.py

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
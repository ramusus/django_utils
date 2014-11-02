# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class ConvertGenericMixin():
    def convert_generic(self, args, kwargs):
        for field in self.model._meta.virtual_fields:
            if isinstance(field, generic.GenericForeignKey):
                if field.name in kwargs:
                    content_object = kwargs.pop(field.name)
                    kwargs[field.ct_field] = ContentType.objects.get_for_model(content_object)
                    kwargs[field.fk_field] = content_object.pk
                if field.name in args:
                    args = list(args)
                    args.remove(field.name)
                    args += [field.ct_field, field.fk_field]
                    args = tuple(args)
        return args, kwargs

class GenericFieldsManager(models.Manager, ConvertGenericMixin):
    '''
    Subclass for filter by GenericForeignKey field in filter, exclude requests
    '''
    def filter(self, *args, **kwargs):
        args, kwargs = self.convert_generic(args, kwargs)
        return super(GenericFieldsManager, self).filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        args, kwargs = self.convert_generic(args, kwargs)
        return super(GenericFieldsManager, self).exclude(*args, **kwargs)

    def get_or_create(self, *args, **kwargs):
        args, kwargs = self.convert_generic(args, kwargs)
        return super(GenericFieldsManager, self).get_or_create(*args, **kwargs)

    def get(self, *args, **kwargs):
        args, kwargs = self.convert_generic(args, kwargs)
        return super(GenericFieldsManager, self).get(*args, **kwargs)

    def only(self, *args, **kwargs):
        # TODO: it seems doesn't work
        args, kwargs = self.convert_generic(args, kwargs)
        return super(GenericFieldsManager, self).only(*args, **kwargs)

    def distinct(self, *args, **kwargs):
        args, kwargs = self.convert_generic(args, kwargs)
        return super(GenericFieldsManager, self).distinct(*args, **kwargs)

class GenericFieldsQuerySet(QuerySet, ConvertGenericMixin):
    '''
    Subclass for filter by GenericForeignKey field in filter, exclude requests
    '''
    def filter(self, *args, **kwargs):
        args, kwargs = self.convert_generic(args, kwargs)
        return super(GenericFieldsQuerySet, self).filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        args, kwargs = self.convert_generic(args, kwargs)
        return super(GenericFieldsQuerySet, self).exclude(*args, **kwargs)

    def get_or_create(self, *args, **kwargs):
        args, kwargs = self.convert_generic(args, kwargs)
        return super(GenericFieldsQuerySet, self).get_or_create(*args, **kwargs)

    def get(self, *args, **kwargs):
        args, kwargs = self.convert_generic(args, kwargs)
        return super(GenericFieldsQuerySet, self).get(*args, **kwargs)

    def only(self, *args, **kwargs):
        # TODO: it seems doesn't work
        args, kwargs = self.convert_generic(args, kwargs)
        return super(GenericFieldsQuerySet, self).only(*args, **kwargs)

    def distinct(self, *args, **kwargs):
        args, kwargs = self.convert_generic(args, kwargs)
        return super(GenericFieldsQuerySet, self).distinct(*args, **kwargs)

def ModelQuerySetManager(ManagerBase=models.Manager):
    '''
    Function that return Manager for using QuerySet class inside the model definition
    @param ManagerBase - parent class Manager
    '''
    if not issubclass(ManagerBase, models.Manager):
        raise ValueError("Parent class for ModelQuerySetManager must be models.Manager or it's child")

    class Manager(ManagerBase):
        '''
        Manager based on QuerySet class inside the model definition
        '''
        def get_query_set(self):
            return self.model.QuerySet(self.model)

        # this method cause memory overfull in admin
#        def __getattr__(self, name):
#            return getattr(self.get_query_set(), name)

    return Manager()

class ModelNameFormCases(object):
    '''
    Parent class for all models with custom verbose names. Incapsulate classmethod verbose_name_form() for accessing to current name
    '''
    @classmethod
    def verbose_name_form(cls, case):
        '''
        Method returns verbose name in special form defined as attributes of VerboseNameFormCases class.
            case - case of verbose_name
        '''
        name = getattr(cls.VerboseNameFormCases, case, False) or cls._get_russian_formcase(case) or cls._meta.verbose_name
        return unicode(name)

    @classmethod
    def _get_russian_formcase(cls, case):
        '''
        Returns case of verbose name in VerboseNameFormCases.case attribute
        There is 6 special predefined cases for Russian Languages:
        '''
        names = (
            ('nominative', u'кто,что'),
            ('genitive', u'кого,чего'),
            ('dative', u'кому,чему'),
            ('accusative', u'кого,что'),
            ('instrumentative', u'кем,чем'),
            ('preposition', u'о ком,о чем', 'about',),
        )
        cases = getattr(cls.VerboseNameFormCases, 'cases').split(',')
        if len(cases) == len(names):
            for i, name_list in enumerate(names):
                if case in name_list:
                    return cases[i]
        return False



'''
From here https://djangosnippets.org/snippets/1079/
my updates:
    renamed field `id`->`pk`
    added `field_names` attribute
    added `select_related` attribute

'''

from django.db.models.query import QuerySet
from django.db.models import Manager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey


class GFKManager(Manager):
    """
    A manager that returns a GFKQuerySet instead of a regular QuerySet.

    """
    def get_query_set(self):
        return GFKQuerySet(self.model)


class GFKQuerySet(QuerySet):
    """
    A QuerySet with a fetch_generic_relations() method to bulk fetch
    all generic related items.  Similar to select_related(), but for
    generic foreign keys.

    Based on http://www.djangosnippets.org/snippets/984/
    """
    def select_generic_related(self, field_names=None, select_related=None):
        qs = self._clone()

        gfk_fields = [g for g in self.model._meta.virtual_fields
                      if isinstance(g, GenericForeignKey) and (field_names is None or g.name in field_names)]

        if not select_related:
            select_related = tuple()
        elif not field_names:
            raise Exception("You should define attribute `field_names` in case of defined attribute `select_related`")

        ct_map = {}
        item_map = {}

        for item in qs:
            for gfk in gfk_fields:
                ct_id_field = self.model._meta.get_field(gfk.ct_field).column
                ct_map.setdefault((ct_id_field, getattr(item, ct_id_field)), {})[getattr(item, gfk.fk_field)] = (gfk.name, item.pk)
            item_map[item.pk] = item

        for (ct_id_field, ct_id), items_ in ct_map.items():
            ct = ContentType.objects.get_for_id(ct_id)
            for o in ct.model_class().objects.select_related(*select_related).filter(pk__in=items_.keys()).all():
                (gfk_name, item_id) = items_[o.pk]
                setattr(item_map[item_id], gfk_name, o)

        return qs
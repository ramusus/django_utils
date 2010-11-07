# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class GenericFieldsManager(models.Manager):
    '''
    Subclass for filter by GenericForeignKey field in filter, exclude requests
    '''
    def convert_generic(self, kwargs):
        for field in self.model._meta.virtual_fields:
            if isinstance(field, generic.GenericForeignKey) and field.name in kwargs:
                content_object = kwargs.pop(field.name)
                kwargs[field.ct_field] = ContentType.objects.get_for_model(content_object)
                kwargs[field.fk_field] = content_object.pk
        return kwargs

    def filter(self, *args, **kwargs):
        kwargs = self.convert_generic(kwargs)
        return super(GenericFieldsManager, self).filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        kwargs = self.convert_generic(kwargs)
        return super(GenericFieldsManager, self).exclude(*args, **kwargs)

    def get_or_create(self, *args, **kwargs):
        kwargs = self.convert_generic(kwargs)
        return super(GenericFieldsManager, self).get_or_create(*args, **kwargs)

    def get(self, *args, **kwargs):
        kwargs = self.convert_generic(kwargs)
        return super(GenericFieldsManager, self).get(*args, **kwargs)

class ModelQuerySetManager(GenericFieldsManager):
    '''
    Manager based on QuerySet class inside the model definition
    '''
    def get_query_set(self):
        return self.model.QuerySet(self.model)

    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)

class ModelNameFormCases(object):
    '''
    Parent class for all models with custom verbose names. Incapsulate classmethod for accessing to current name
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
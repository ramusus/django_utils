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
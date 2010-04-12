# -*- coding: utf-8 -*-
from django.db import models

class ModelQuerySetManager(models.Manager):
    '''Manager based on QuerySet class inside the model definition'''
    def get_query_set(self):
        return self.model.QuerySet(self.model)

    def __getattr__(self, name):
        return getattr(self.get_query_set(), name)
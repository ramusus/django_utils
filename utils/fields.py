from composition.base import CompositionField
from django.db import models

class ForeignCountField(CompositionField):

    signal_default = (models.signals.post_save, models.signals.post_delete)

    def __init__(self, model, link_back_name, link_to_foreign_name, filter=None, native=None, signal=None, verbose_name=None, distinct=False):
        self.rel_model = model
        self.link_back_name = link_back_name
        self.link_to_foreign_name = link_to_foreign_name
        self.filter = filter or {}
        self.distinct = distinct
        self.native = native or models.PositiveIntegerField(default=0, db_index=True, verbose_name=verbose_name)
        self.signal = signal or self.signal_default

        self.internal_init(
            native = self.native,
            trigger = dict(
                on = self.signal,
                sender_model = self.rel_model,
                do = self.do,
                field_holder_getter = self.instance_getter
            )
        )

    def do(self, object, foreign, signal):
        queryset = getattr(object, self.link_to_foreign_name).filter(**self.filter)
        if self.distinct:
            queryset = queryset.distinct()
        return queryset.count()

    def instance_getter(self, foreign):
        ''' Return instance getter with special check for generic relation '''
        instance = getattr(foreign, self.link_back_name)
        if not instance:
            # check generic fields
            for field in foreign._meta.virtual_fields:
                if field.name == self.link_back_name:
                    content_type = getattr(foreign, field.ct_field)
                    object_id = getattr(foreign, field.fk_field)
                    instance = content_type.get_object_for_this_type(id=object_id)
                    break
        return instance

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = self._c_native.__class__.__module__ + "." + self._c_native.__class__.__name__
        args, kwargs = introspector(self._c_native)
        # That's our definition!
        return (field_class, args, kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(ForeignCountField, self).deconstruct()
        del kwargs['default']
        del kwargs['db_index']

        kwargs['model'] = self.rel_model
        kwargs['link_back_name'] = self.link_back_name
        kwargs['link_to_foreign_name'] = self.link_back_name
        kwargs['filter'] = self.filter
        kwargs['distinct'] = self.distinct
        kwargs['native'] = self.native
        if self.signal != self.signal_default:
            kwargs['signal'] = self.signal

        return name, 'utils.fields.ForeignCountField', args, kwargs

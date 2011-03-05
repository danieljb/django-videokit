
import os
from django.conf import settings


class EncodingOptions(object):

    save_count_as = None
    specs_module = []
    input_file = 'input_filefield'

    def __init__(self, opts):
        if opts:
            for key, value in opts.__dict__.iteritems():
                setattr(self, key, value)


class Specification(object):

    increment_count = False


class SpecAccessor(object):

    def __init__(self, instance, spec, field):
        self._instance = instance
        self._field = getattr(instance, field)
        self._spec = spec
        self._opts = instance.encoding_options

    @property
    def file(self):
        return getattr(self._field, 'file')

    @property
    def url(self):
        if self._spec is not None and self._spec.increment_count:
            count_field = self._opts.save_count_as
            if count_field is not None:
                current_count = getattr(self._instance, count_field)
                setattr(self._instance, count_field, current_count +1)
                self._instance.save()
        return self._field.url

    @property
    def status(self):
        state = self._instance.status.filter(
            specification=self._spec.identifier).order_by('-creation_date')[0]
        return state.status


class SpecDescriptor(object):

    def __init__(self, spec, fieldname):
        self._spec = spec
        self._field = fieldname

    def __get__(self, instance, type=None):
        return SpecAccessor(instance, self._spec, self._field)

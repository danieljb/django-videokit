
from django.core import serializers

from django.db.models.base import ModelBase
from django.db import models

from django.utils.translation import ugettext_lazy as _

from django.conf import settings

from videokit.conf import settings as video_settings


class EncodingSpecificationBase(models.Model):

    def __init__(self, *args, **kwargs):
        super(EncodingSpecificationBase, self).__init__(*args, **kwargs)
        if hasattr(self, '__subclasses__') and not hasattr(self, 'output_file'):
            raise AttributeError("Instance of %s has to implement output_file property." % self.__class__)

    registered_filters = list()

    name = models.CharField(
        _('name'),
        max_length=250,
        null=False,
        blank=False,
    )

    identifier = models.SlugField(
        _('identifier'),
        max_length=50,
        null=False,
        blank=False,
        unique=True,
        help_text=_('Use this slug to reference this specification in Encoding Model'),
    )

    creation_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    def as_dict(self):
        spec = {
            'identifier': self.identifier,
            'output_file': 'output_file',
            'filters': {},
        }
        for filter_name in self.registered_filters:
            filter = getattr(self, filter_name).all()[0]
            spec.get('filters')[filter.name] = serializers.serialize('python', [filter])[0]['fields']
        return spec

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        app_label = 'videokit'


class EncodingFilterBase(ModelBase):

    def __new__(cls, name, bases, attrs):
        model = super(EncodingFilterBase, cls).__new__(cls, name, bases, attrs)
        if bases[0] is not models.Model:
            model.specs_class.registered_filters.append("%s_set" % name.lower())

        return model


class EncodingFilter(models.Model):

    __metaclass__ = EncodingFilterBase

    specs_class = EncodingSpecificationBase

    specifications = models.ForeignKey(
        EncodingSpecificationBase,
        null=False,
        unique=True,
        blank=False,
    )

    def __init__(self, *args, **kwargs):
        super(EncodingFilter, self).__init__(*args, **kwargs)
        if not hasattr(self, 'name'):
            raise AttributeError("Instance of %s has to implement name property." % self.__class__)

    def __unicode__(self):
        return u"%s filter" % self.specifications.name

    class Meta:
        app_label = 'videokit'
        abstract = True


class EncodingFilterScaling(EncodingFilter):

    name = 'scaling'

    width = models.IntegerField(
        _('width'),
        null=True,
        blank=True,
        help_text=_('Width in pixels'),
    )

    height = models.IntegerField(
        _('height'),
        null=True,
        blank=True,
        help_text=_('Height in pixels'),
    )


class EncodingFilterCropping(EncodingFilter):

    name = 'cropping'

    left = models.IntegerField(
        _('left'),
        null=True,
        blank=True,
        help_text=_('Left pixel'),
    )

    right = models.IntegerField(
        _('right'),
        null=True,
        blank=True,
        help_text=_('Right pixel'),
    )

    top = models.IntegerField(
        _('top'),
        null=True,
        blank=True,
        help_text=_('Top pixel'),
    )

    bottom = models.IntegerField(
        _('bottom'),
        null=True,
        blank=True,
        help_text=_('Bottom pixel'),
    )


from django.db.models.base import ModelBase
from django.db import models

from django.utils.translation import ugettext_lazy as _

from django.conf import settings

from videokit.conf import settings as video_settings


class EncodingSpecificationBase(models.Model):
    
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
    
    # TODO: Add Encoder-Choices
    
    def get_path(self):
        pass
    
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
        blank=False,
        unique=True,
    )
    
    def __unicode__(self):
        return u"%s filter" % self.preset.title
    
    class Meta: 
        app_label = 'videokit'
        abstract = True
    

class EncodingFilterScaling(EncodingFilter):
    
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
    


import os 

from django.db.models.base import ModelBase
from django.db import models

from django.utils.translation import ugettext_lazy as _

from django.conf import settings

from hybrid_filefield.fields import FileSelectOrUpload

from videokit.conf import settings as video_settings
from videokit.options import EncodingOptions


VIDEO_PATH          = getattr(video_settings, 'VIDEO_PATH', os.path.join(settings.MEDIA_ROOT, 'videos', 'encodings'))
VIDEO_SEARCH_PATH   = getattr(video_settings, 'VIDEO_SEARCH_PATH', os.path.join(VIDEO_PATH, 'ftp_uploads'))
VIDEO_PATH_FILTER   = getattr(video_settings, 'VIDEO_PATH_FILTER', None)


# Create your models here.

class EncodingModelBase(ModelBase):
    
    def __new__(cls, name, bases, attrs):
        model = super(EncodingModelBase, cls).__new__(cls, name, bases, attrs)
        
        user_options = getattr(model, 'EncodingOptions', None)
        options = EncodingOptions(user_options)
        
        setattr(model, 'encoding_options', options)
        
        return model
    

class EncodingModel(models.Model):
    
    __metaclass__ = EncodingModelBase
    
    def __init__(self, *args, **kwargs):
        super(EncodingModel, self).__init__(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        super(EncodingModel, self).save(*args, **kwargs)
    
    def process(self, presets=[], force_process=False):
        for preset in self.encoding_options.presets:
            print "process preset %s" % preset
    
    class Meta:
        abstract = True
    

class EncodingPresetBase(models.Model):
    
    title = models.CharField(
        _('title'), 
        max_length=250, 
        null=False, 
        blank=False, 
    )
    
    slug = models.SlugField(
        _('Preset Identifier'),
        max_length=50,
        null=False,
        blank=False,
        unique=False,
        help_text=_('Use this slug to reference this preset in Encoding Model'),
    )
    
    creation_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    
    def __unicode__(self):
        return u"%s" % self.title
    
    class Meta: 
        abstract = True
    

class EncodingPreset(EncodingPresetBase):
    
    registered_filters = list()
    
    output_file = FileSelectOrUpload(
        verbose_name=_('Video File'), 
        path=VIDEO_SEARCH_PATH, 
        upload_to=VIDEO_PATH, 
        match=VIDEO_PATH_FILTER, 
        null=True, blank=True, 
        help_text=_( 
            'Select a video file which was uploaded to %(video_search_path)s on the server or upload one via http.' % 
                {'video_search_path': os.path.relpath(os.path.realpath(VIDEO_SEARCH_PATH), settings.MEDIA_ROOT),}
        ),
    )
    

class EncodingFilterBase(ModelBase):
    
    def __new__(cls, name, bases, attrs):
        model = super(EncodingFilterBase, cls).__new__(cls, name, bases, attrs)
        if bases[0] is not models.Model:
            model.preset_class.registered_filters.append("%s_set" % name.lower())
        
        return model
    

class EncodingFilter(models.Model):
    
    __metaclass__ = EncodingFilterBase
    
    preset_class = EncodingPreset
    
    preset = models.ForeignKey(
        EncodingPreset,
        null=False,
        blank=False,
        unique=True,
    )
    
    def __unicode__(self):
        return u"%s filter" % self.preset.title
    
    class Meta: 
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
    

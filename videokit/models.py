# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.db.models.base import ModelBase
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from hybrid_filefield.fields import FileSelectOrUpload

from videokit.conf import settings as video_settings
from videokit.meta import EncodingOptions, Specification, SpecDescriptor
from videokit.tasks import ProcessVideo

import logging
logger = logging.getLogger(__name__)


VIDEO_PATH = getattr(
    video_settings,
    'VIDEO_PATH',
    os.path.join(settings.MEDIA_ROOT, 'videos', 'encodings'))
VIDEO_SEARCH_PATH = getattr(
    video_settings,
    'VIDEO_SEARCH_PATH',
    os.path.join(VIDEO_PATH, 'ftp_uploads'))
VIDEO_PATH_FILTER = getattr(
    video_settings,
    'VIDEO_PATH_FILTER',
    None)


# Create your models here.

class EncodingStatus(models.Model):

    task_id = models.CharField(
        _('task id'),
        max_length=36,
        editable=False,
        help_text=_('The corresponding celery task'),
    )

    specification = models.CharField(
        _('specification identifier'),
        max_length=50,
        editable=False,
        help_text=_('Use this slug to reference this specification'
                    ' in Encoding Model'),
    )

    creation_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    status = models.CharField(
        _('status'),
        max_length=50,
        help_text=_('Task\'s status'),
    )

    protocoll = models.TextField(
        _('encoding protocoll'),
        null=True, blank=True,
        help_text=_('Further encoding information.'),
    )

    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_('encoding model content type'),
    )
    object_id = models.PositiveIntegerField(
        _('encoding model primary key'),
    )
    content_object = generic.GenericForeignKey(
        'content_type',
        'object_id',
    )

    def __unicode__(self):
        return "Status for %s (%s)" % (self.content_object, self.status)


class EncodingModelBase(ModelBase):

    def __new__(cls, name, bases, attrs):
        model = super(EncodingModelBase, cls).__new__(cls, name, bases, attrs)

        options = EncodingOptions(getattr(model, 'EncodingOptions', None))

        if options.specs_module:
            try:
                specs_module = __import__(options.specs_module, {}, {}, [''])
            except ImportError:
                raise ImportError('Unable to load video config module: %s' %
                                  options.specs_module)

            # Adding an output file field for every defined spec
            # in referenced specification file. Saving specs in
            # dictionary for later use in process method.
            specs = []
            for spec in [spec for spec in specs_module.__dict__.values()
                    if isinstance(spec, type)
                    and issubclass(spec, Specification)
                    and spec is not Specification]:

                specials = {'identifier': spec.identifier,}

                output_filefield = FileSelectOrUpload(
                    verbose_name=getattr(spec, 'verbose_name',
                                         '%(identifier)s file') % specials,
                    path=getattr(spec, 'search_path', VIDEO_SEARCH_PATH) %
                         specials,
                    upload_to=getattr(spec, 'upload_to', VIDEO_PATH) %
                              specials,
                    match=getattr(spec, 'match', '') % specials,
                    help_text=getattr(spec, 'help_text', '') % specials,
                    null=True, blank=True,)

                fieldname = getattr(spec, 'output_file',
                                    '%(identifier)s_file') % specials
                model.add_to_class(
                    fieldname,
                    output_filefield,
                )
                setattr(model,
                        '{0}'.format(spec.identifier),
                        SpecDescriptor(spec, fieldname))

                specs.append({
                    'identifier': spec.identifier,
                    'extensions': getattr(spec, 'extensions', ['mov',]),
                    'output_file': fieldname,
                    'filters': getattr(spec, 'filters', {}),
                })

            setattr(options, 'specifications', specs)
        setattr(model, 'encoding_options', options)
        return model


class EncodingModel(models.Model):

    __metaclass__ = EncodingModelBase

    status = generic.GenericRelation(EncodingStatus)

    # TODO Decide what a return value for this method could be useful!
    def process(self, specification=None, force_process=False):
        specs = []
        if hasattr(self.encoding_options, 'specifications'):
            for spec in self.encoding_options.specifications:
                specs.append(spec)
        if hasattr(self.encoding_options, 'specs_field'):
            for spec in getattr(self, getattr(self.encoding_options,
                                              'specs_field')).all():
                specs.append(spec.as_dict())

        try:
            input_file = getattr(self,
                                 self.encoding_options.input_file).path
        except ValueError:
            raise ValueError('input_file of {0} has no file'
                             ' associated with it.'.format(self))

        for spec in specs:
            logger.debug("Process spec: %s" % spec)

            # TODO Protocoll and logging are pretty verbose right now ...

            status = EncodingStatus.objects.create(
                specification=spec['identifier'],
                content_object=self,
            )
            protocoll = getattr(status, 'protocoll', '')

            # Omit encoding if output file is already specified
            if getattr(self, spec['output_file']):
                info = ('Omitting further processing of {identifier}'
                        ' on {model}, output_file already available.'.format(
                            identifier=spec['identifier'],
                            model=self,))

                logger.info(info)
                protocoll = '{protocoll}\n\r{info}'.format(protocoll=protocoll,
                                                           info=info)
                status.protocoll = protocoll

                status.save()
                continue

            # Extracts file name from input_field and constructs
            # output_file name regarding specs extension definition
            # and output_file upload_to path.
            in_name, ext = os.path.splitext(os.path.basename(input_file))
            output_file = os.path.join(
                os.path.abspath(getattr(
                    self,
                    spec['output_file']).field.upload_to),
                '{in_name}_{spec}.{ext}'.format(
                    in_name=in_name,
                    spec=spec['identifier'],
                    ext=spec['extensions'][0]))

            info = 'Encode {identifier} for {model} to {output_file}'.format(
                        identifier=spec['identifier'],
                        model=self,
                        output_file=output_file,)

            logger.info(info)
            protocoll = '{protocoll}\n\r{info}'.format(protocoll=protocoll,
                                                       info=info)
            status.protocoll = protocoll

            status.save()
            # For debug purposes dry run is activated!
            task = ProcessVideo.apply_sync(args=(self.pk,
                                                 input_file,
                                                 output_file,
                                                 status.pk),
                                           kwargs={'filters': spec['filters'],
                                                   'dry': True,})

            setattr(self, spec['output_file'], output_file)
            self.save()

            status.status = task.state
            status.task_id = task.task_id
            status.save()

            logger.debug("Started process: %s" % task)
        return True

    class Meta:
        abstract = True

    class EncodingOptions:
        pass

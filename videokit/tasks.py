
from django.conf import settings

from celery.task import Task
from celery.registry import tasks

import videotool
import videokit.models


class ProcessVideo(Task):
    def run(self, video_pk, input_file, output_file, status_pk, filters=None):
        logger = self.get_logger()

        status = videokit.models.EncodingStatus.objects.get(pk=status_pk)
        logger.info("Run encoding for %s" % input_file)

        videotool.encode(input_file, output_file)

        status.status = 'Done'
        status.save()
        return True

tasks.register(ProcessVideo)

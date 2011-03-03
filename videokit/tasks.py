
from django.conf import settings

from celery.task import Task
from celery.registry import tasks

import videotool
import videokit.models


class ProcessVideo(Task):

    encode_status = {}
    status = None

    def run(self, video_pk, input_file, output_file, status_pk,
            filters=None, dry=False):

        self.logger = self.get_logger()

        self.status = videokit.models.EncodingStatus.objects.get(pk=status_pk)
        self.logger.info("Run encoding for %s" % input_file)

        def status_callback(format, info):
            self.logger.info("Current Status: %s" % info)
            self.encode_status.info = info

        option = videotool.OptionsBase()
        option.status = status_callback

        if not dry:
            videotool.encode_h264(
                input_file,
                output_file,
                encode_options=option
            )

        return True

    def update_state(self, task_id=None, state=None, meta=None):
        super(ProcessVideo, self).update_state(task_id, state, meta)

        self.logger.info("Update Status %s (%s)" % (task_id, state))

        self.status.protocoll = self.encode_status.info
        self.status.status = state

        print self.status.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo=None):
        self.status.protocoll = str(exc)
        self.status.save()

    def on_success(self, retval, task_id, args, kwargs):
        protocoll = self.status.protocoll
        report = "\n\rReturned {0}".format(retval)
        if protocoll:
            report = str(protocoll) + str(report)
        
        self.status.protocoll = str(report)
        r = self.status.save()

        self.logger.info("Success %s, report: %s, r: %s" % (task_id, report, r))

    def after_return(self, state, retval, task_id, args,
            kwargs, einfo=None):
        self.status.status = state
        self.status.save()

        self.logger.info("Finalized task {0} with status {1}".format(
            task_id, self.status
        ))


tasks.register(ProcessVideo)

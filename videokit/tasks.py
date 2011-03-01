
from celery.task import Task
from celery.registry import tasks

import videotool

class ProcessVideo(Task):
    def run(self, video_pk, input_file, output_file, filters):
        videotool.encode(input_file, output_file)
        return True

tasks.register(ProcessVideo)

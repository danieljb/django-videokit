
from celery.task import Task
from celery.registry import tasks

class ProcessVideo(Task):
    def run(self, video_pk, input_file):
        logger = self.get_logger()
        logger.info("Processed video %s for %s." % (input_file, video_pk))
        return True

tasks.register(ProcessVideo)
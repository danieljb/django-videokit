
from celery.task import Task
from celery.registry import tasks

class ProcessVideo(Task):
    def run(self, video_pk):
        logger = self.get_logger()
        logger.info("Processed video for %s." % video_pk)
        return True

tasks.register(ProcessVideo)
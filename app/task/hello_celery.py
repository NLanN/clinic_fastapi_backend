# Create Order - Run Asynchronously with celery
# Example process of long running task
from time import sleep

from extensions.celery import celery, celery_log


@celery.task
def hello_after_second(sec):
    sleep(sec)
    celery_log.info(f"Your Celery run successfully!")
    return True

from celery import Celery
from app.core.config import get_settings

celery_app = Celery("taskboard", broker=get_settings().redis_url, backend=get_settings().redis_url, include=["app.workers.jobs"])
celery_app.conf.update(task_track_started=True, result_expires=3600)

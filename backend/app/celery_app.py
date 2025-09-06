"""Celery application configuration."""

from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "auction_platform",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Zurich",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "fetch-shab-data": {
        "task": "app.tasks.fetch_shab_data",
        "schedule": settings.fetch_interval_hours * 3600,  # Convert hours to seconds
    },
    "cleanup-expired-data": {
        "task": "app.tasks.cleanup_expired_data",
        "schedule": 24 * 3600,  # Daily
    },
    "generate-daily-report": {
        "task": "app.tasks.generate_daily_report",
        "schedule": 24 * 3600,  # Daily at midnight
    },
}

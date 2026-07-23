import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery app
celery_app = Celery(
    "healthid_worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/2"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
    include=["ai_pipeline.worker"]
)

# Optional configuration, see the application user guide.
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300, # 5 minutes max per task
    task_default_queue='healthid_celery', # Isolate queue from other projects
)

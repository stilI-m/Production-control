import os
from celery import Celery
from celery.schedules import crontab
broker_url_env = os.getenv('CELERY_BROKER_URL')
REDIS_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
if not broker_url_env:
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
    RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')
    # Для работы внутри Docker по умолчанию стучимся в контейнер 'rabbitmq'
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    RABBITMQ_PORT = os.getenv('RABBITMQ_PORT', '5672')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
    broker_url_env = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}{RABBITMQ_VHOST}'

celery_app = Celery('production_tasks', broker=broker_url_env, backend=REDIS_BACKEND)

celery_app.autodiscover_tasks([
    "src.tasks.import_export",
    "src.tasks.webhooks",
    "src.tasks.cleanup",
    'src.tasks.aggregation',
    'src.tasks.reports',
])
celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "clean-old-export-files-every-midnight": {
        "task": "src.tasks.cleanup.cleanup_old_exports_task",
        "schedule": crontab(hour=0, minute=0),  # Каждый день в 00:00 UTC
        "args": (1,),                           # Файлы старше 1 дня
    },
}
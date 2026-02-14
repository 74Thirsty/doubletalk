from src.jobs.celeryApp import celery_app


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def send_reminder(self, reminder_id: int):
    return {'reminder_id': reminder_id, 'status': 'sent'}

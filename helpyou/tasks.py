from celery.task import periodic_task
__author__ = 'tmehta'
from mailer.engine import send_all
from datetime import timedelta

# this will run every 1 seconds
# send all emails in the mailer queue


@periodic_task(run_every=timedelta(seconds=1))
def email_tasks():
    send_all()
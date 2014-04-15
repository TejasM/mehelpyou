from celery.task import periodic_task
from django.contrib.auth.models import User
from django.db.models import Q
from django.template.loader import get_template
from django.utils import timezone
#from mailer import send_html_mail
#from mailer.engine import send_all
from datetime import timedelta
from mailer import send_html_mail
from helpyou import settings
from helpyou.notifications.models import Notification

from helpyou.request.models import Request
from helpyou.response.models import Response


# this will run every 1 seconds
# send all emails in the mailer queue
@periodic_task(run_every=timedelta(seconds=1))
def email_tasks():
    pass
    #send_all()


@periodic_task(run_every=timedelta(weeks=1))
def weekly_digest():
    users = User.objects.all()
    timenow = timezone.now()
    for user in users:
        if user.email:
            try:
                request_pending_connections = []
                requests_connection = Request.objects.all()
                for request in requests_connection:
                    if request.response_set.filter(user=user).count() == 0:
                        request_pending_connections.append(request)
                requests_your = Request.objects.filter(user=user).filter(Q(due_by__gte=timenow))
                responses_to = {}
                for request in requests_your:
                    responses = Response.objects.filter(request=request)
                    responses_to[request] = responses
                negotitation_notifications = Notification.objects.filter(message='RN', user=user)
                your_responses = Response.objects.filter(user=user).filter(~Q(buyer=None))
                earned = 0
                for response in your_responses:
                    earned += response.price
                write_weekly_email(user, request_pending_connections, responses_to,
                                   negotitation_notifications, earned)
            except Exception as e:
                print e
                pass


def write_weekly_email(user, connections_requests, your_requests, negotiations, points_earned):
    htmly = get_template('email/newsletter.html')
    message = htmly.render({'connections_requests': connections_requests, 'your_requests': your_requests,
                            'points_earned': points_earned})
    send_html_mail('MeHelpYou Digest', "", message, 'info@mehelpyou.com', [user.email], fail_silently=True)
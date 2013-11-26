from celery.task import periodic_task
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from mailer import send_html_mail
from mailer.engine import send_all
from datetime import timedelta
from helpyou import settings
from helpyou.notifications.models import Notification

from helpyou.request.models import Request
from helpyou.response.models import Response


# this will run every 1 seconds
# send all emails in the mailer queue
@periodic_task(run_every=timedelta(seconds=1))
def email_tasks():
    send_all()


@periodic_task(run_every=timedelta(minutes=60))
def weekly_digest():
    users = User.objects.all()
    timenow = timezone.now()
    for user in users:
        if user.email:
            try:
                profile = user.user_profile.get()
                connections = profile.connections.all()
                request_pending_connections = []
                for connection in connections:
                    requests_connection = Request.objects.filter(user=connection)
                    for request in requests_connection:
                        if request.response_set.filter(user=user).count() != 0:
                            request_pending_connections.append(request)
                requests_your = Request.objects.filter(user=user).filter(Q(due_by__gte=timenow))
                responses_to = {}
                for request in requests_your:
                    responses = Response.objects.filter(request=request)
                    responses_to[request] = responses
                negotitation_notifications = Notification.objects.filter(message='RN', user=user)
                your_responses = Response.objects.filter(user=user).filter(~Q(buyer=None)).filter(
                    time_accepted__gte=(timenow - timedelta(weeks=1)))
                earned = 0
                for response in your_responses:
                    earned += response.price
                write_weekly_email(user, request_pending_connections, responses_to,
                                   negotitation_notifications, earned)
            except Exception as e:
                print e
                pass


def write_weekly_email(user, connections_requests, your_requests, negotiations, points_earned):
    message = "<strong>MeHelpYou Weekly Digest</strong><br>"
    message += "<p>Your Connections' Pending Requests:"
    for request in connections_requests:
        message += "<br><a href='www.mehelpyou.com/request/view/" + str(request.id) + "'>" + request.title + "</a> from " + request.user.username
    if your_requests.iteritems():
        message += "</p><br><p>"
        for request, responses in your_requests.iteritems():
            message += "<br><p>For your request: <a href='www.mehelpyou.com/request/view/" + str(request.id) + "'>" + request.title + "</a> you have the following responses:"
            for response in responses:
                message += "<br><p style='text-indent: 5em;'> <a href='www.mehelpyou.com/response/view/" + str(response.id) + "'>" + response.preview + "</a></p>"
    if negotiations:
        message += "</p><br><p>"
        for negotiation in negotiations:
            message += "<br><p>Your <a href='www.mehelpyou.com/response/view/" + str(negotiation.response.id) + "'>response</a> for request " + negotiation.request.title + " has a negotiation."
    message += "<br>This week you have earned " + str(points_earned) + " points by helping your friends out"
    message += settings.NOTE
    send_html_mail('MeHelpYou Digest', "", message, 'info@mehelpyou.com', [user.email], fail_silently=True)
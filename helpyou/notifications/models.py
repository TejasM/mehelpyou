from django.contrib.auth.models import User
from django.db import models
from helpyou.request.models import Request
from helpyou.response.models import Response


def get_notification(instance):
    if instance.message == "RR":
        return 'Your Request ' + instance.request.title + ' has a Response'
    if instance.message == "RA":
        return 'Your Response for Request ' + instance.request.title + ' has been accepted'
    if instance.message == "RN":
        return 'Your Response for Request ' + instance.request.title + ' has a negotiation'
    if instance.message == 'CN':
        return 'Your Negotiation for Request ' + instance.request.title + ' has been updated'


class Notification(models.Model):
    user = models.ForeignKey(User)
    viewed = models.BooleanField(default=False)
    message = models.CharField(max_length=200)
    request = models.ForeignKey(Request)
    response = models.ForeignKey(Response)

    def __unicode__(self):
        return get_notification(self)
from django.contrib.auth.models import User
from django.db import models
from helpyou.request.models import Request
from helpyou.response.models import Response


def get_notification(instance):
    if instance.message == "RR":
        return 'Your Request ' + instance.request.title + ' has a Response'
    if instance.message == "RA":
        return 'Your Response for Request ' + instance.request.title + ' has been accepted'
    if instance.message == "AW":
        return 'Your Response for Request ' + instance.request.title + ' has been awarded'
    if instance.message == "RN":
        return 'Your Response for Request ' + instance.request.title + ' has a negotiation'
    if instance.message == 'CN':
        return 'Your Negotiation for Request ' + instance.request.title + ' has been updated'
    if instance.message == 'IN':
        return 'Invitation from ' + instance.to_user.first_name + " " + instance.to_user.last_name
    if instance.message == 'AN':
        return 'Invitation to ' + instance.to_user.first_name + " " + instance.to_user.last_name + 'accepted'


class Notification(models.Model):
    user = models.ForeignKey(User, related_name="from_user")
    viewed = models.BooleanField(default=False)
    message = models.CharField(max_length=200)
    request = models.ForeignKey(Request, null=True)
    response = models.ForeignKey(Response, null=True)
    to_user = models.ForeignKey(User, related_name="to_user", null=True)

    def __unicode__(self):
        return get_notification(self)
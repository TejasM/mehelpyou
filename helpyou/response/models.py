from django.contrib.auth.models import User
from django.db import models


# Create your models here.
from django.utils import timezone
from helpyou.request.models import Request


class Response(models.Model):
    request = models.ForeignKey(Request)
    user = models.ForeignKey(User, related_name="user")
    anon = models.BooleanField()
    preview = models.CharField(max_length=300)
    response = models.CharField(max_length=100000)
    viewed = models.BooleanField(default=False)

    create_time = models.DateTimeField(default=timezone.now())
    relevant = models.NullBooleanField(default=None, null=True)

    commission_paid = models.FloatField(default=0)
    commission_time = models.DateTimeField(default=None, null=True)
    buyer = models.ForeignKey(User, related_name="buyer", default=None, null=True)

    def __unicode__(self):
        return "Response to: " + self.request.title
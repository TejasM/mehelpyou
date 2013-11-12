from django.contrib.auth.models import User
from django.db import models


# Create your models here.
from django.utils import timezone
from helpyou.request.models import Request


class Response(models.Model):
    request = models.ForeignKey(Request)
    user = models.ForeignKey(User, related_name="user")
    anon = models.BooleanField()
    preview = models.CharField(max_length=10000)
    response = models.CharField(max_length=100000)
    available_till = models.DateTimeField()
    create_time = models.DateTimeField(default=timezone.now())
    price = models.FloatField()
    buyer = models.ForeignKey(User, related_name="buyer", default=None, null=True)
    counter_offer = models.FloatField(default=None, null=True)
    counter_comments = models.CharField(default=None, null=True, max_length=500)
    prev_negotiated = models.BooleanField(default=False)
    awarded = models.BooleanField(default=False)

    def __unicode__(self):
        return "Response to: " + self.request.title
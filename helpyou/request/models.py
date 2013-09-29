from django.contrib.auth.models import User
from django.db import models


# Create your models here.
from django.utils import timezone


class Request(models.Model):
    title = models.CharField(max_length=50)
    user = models.ForeignKey(User)
    anon = models.BooleanField(default=False)
    request = models.CharField(max_length=1000)
    due_by = models.DateTimeField()
    create_time = models.DateTimeField(default=timezone.now())
    reward = models.FloatField()

    def __unicode__(self):
        return self.title
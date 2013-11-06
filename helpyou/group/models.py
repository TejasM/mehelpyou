from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Group(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=5000)
    private = models.BooleanField(default=True)
    users = models.ManyToManyField(User, related_name="users")
    created = models.DateTimeField(default=timezone.now())
    administrators = models.ManyToManyField(User, related_name="administrators")
    logo = models.ImageField(default='default-avatar.png', null=True, upload_to='avatars')
    pending_requests = models.ManyToManyField(User, related_name="pending_requests")

    def __unicode__(self):
        return self.title

admin.site.register(Group)
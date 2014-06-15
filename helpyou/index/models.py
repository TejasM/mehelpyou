from django.contrib import admin
from django.db import models


class Feedback(models.Model):
    comments = models.CharField(max_length=2000, default="")
    name = models.CharField(max_length=200, default="")
    email = models.EmailField(null=True)

admin.site.register(Feedback)

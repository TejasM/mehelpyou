from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.ForeignKey(User, related_name="user_profile")
    interests = models.CharField(max_length=10000)
    skills = models.CharField(max_length=10000)
    city = models.CharField(max_length=50, default='', blank=True)
    industry = models.CharField(max_length=100, default='', blank=True)
    educations = models.CharField(max_length=10000, default='', blank=True)
    num_connections = models.IntegerField(default=0)
    num_recommenders = models.IntegerField(default=0)
    recommendations_received = models.CharField(max_length=10000, default='', null=True, blank=True)
    groups = models.CharField(max_length=10000, default='', blank=True)
    rating = models.FloatField(default=0)
    money_current = models.FloatField(default=0)
    lifetime_earning = models.FloatField(default=0)
    paypal_email = models.EmailField(default='')
    connections = models.ManyToManyField(User, related_name="connections")


class UserPic(models.Model):
    user = models.ForeignKey(User, related_name='user_info')
    image = models.ImageField(default='None', upload_to=user)

    def get_uid(self):
        return self.user.id

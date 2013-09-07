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
    points_current = models.FloatField(default=0)
    lifetime_points_earned = models.FloatField(default=0)
    paypal_email = models.EmailField(default='')
    connections = models.ManyToManyField(User, related_name="connections")


class UserPic(models.Model):
    user = models.ForeignKey(User, related_name='user_info')
    image = models.ImageField(default='None', upload_to=user)

    def get_uid(self):
        return self.user.id


class Invitees(models.Model):
    email_address = models.EmailField(default="")
    name = models.CharField(max_length=500, default="")
    uid = models.CharField(default='', max_length=500)
    social_media = models.CharField(default='linkedin-oauth2', max_length=100)
    user_from = models.ForeignKey(UserProfile, default=None, null=True)
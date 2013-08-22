from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.ForeignKey(User)
    interests = models.CharField(max_length=1000)
    skills = models.CharField(max_length=1000)
    city = models.CharField(max_length=50, default='')
    industry = models.CharField(max_length=100, default='')
    educations = models.CharField(max_length=1000, default='')
    num_connections = models.IntegerField(default=0)
    num_recomenders = models.IntegerField(default=0)
    recommandations_recieved = models.CharField(max_length=1000, default='')
    groups = models.CharField(max_length=1000, default='')
    rating = models.FloatField(default=0)
    money_current = models.FloatField(default=0)
    lifetime_earning = models.FloatField(default=0)
    paypal_email = models.EmailField(default='')


class UserPic(models.Model):
    user = models.ForeignKey(User, related_name='user_info')
    image = models.ImageField(default='None', upload_to=user)

    def get_uid(self):
        return self.user.id

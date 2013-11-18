from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from helpyou import settings


#Each feature is assigned a list of plan numbers and the plans map to list of points added each month
features = {"view_all": [1, 2, 3], "can_post_anonymously": [2, 3], "negotiate_more_than_once": [1, 2, 3],
            "bold": [2, 3], "larger_font": [2, 3], "2nd_connections": [2, 3]}

plan_points = {0: 0, 1: 15, 2: 33, 3: 75}

plan_costs = {0: 0, 1: 2500, 2: 5000, 3: 9900}


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
    picture = models.ImageField(default='default-avatar.png', upload_to='avatars')
    # Determines the features available
    plan = models.IntegerField(default=0)
    prev_plan = models.IntegerField(default=0)
    customer = models.CharField(default=None, null=True, max_length=200)
    notification_response = models.BooleanField(default=True)
    notification_connection_request = models.BooleanField(default=False)
    notification_reward = models.BooleanField(default=True)
    last_updated = models.DateTimeField(default=timezone.now())
    never_updated = models.BooleanField(default=True)

    #Static Variables
    plan_names = {0: "Free", 1: "Business", 2: "Business Plus", 3: "Executive"}

    #Implement Each Feature via some key and then just check it its available for the current profile.
    def features(self):
        return [feature for feature in features.keys() if self.plan in features[feature]]

    def is_feature_available(self, feature):
        return self.plan in features[feature]

    def __unicode__(self):
        return self.user.username


class Invitees(models.Model):
    email_address = models.EmailField(default="")
    name = models.CharField(max_length=500, default="")
    uid = models.CharField(default='', max_length=500)
    social_media = models.CharField(default='linkedin-oauth2', max_length=100)
    user_from = models.ForeignKey(UserProfile, default=None, null=True)


admin.site.register(UserProfile)
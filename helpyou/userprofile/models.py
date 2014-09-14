from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import watson
from helpyou import settings


# Each feature is assigned a list of plan numbers and the plans map to list of points added each month
from helpyou.request.models import Request
from helpyou.response.models import Response

features = {"view_all": [1, 2], "can_post_anonymously": [2], "negotiate_more_than_once": [1, 2],
            "bold": [2], "larger_font": [2], "2nd_connections": [2]}

plan_costs = {0: 0, 1: 2000, 2: 5000}


class UserProfile(models.Model):
    user = models.ForeignKey(User, related_name="user_profile")
    interests = models.CharField(max_length=10000)
    skills = models.CharField(max_length=10000)
    city = models.CharField(max_length=50, default='', blank=True)
    industry = models.CharField(max_length=100, default='', blank=True)
    educations = models.CharField(max_length=10000, default='', blank=True)
    num_connections = models.IntegerField(default=0)
    company = models.CharField(max_length=200, default='', blank=True)

    rating = models.FloatField(default=0)

    paypal_email = models.EmailField(default='')
    commission_earned = models.IntegerField(default=0)
    commission_paid = models.IntegerField(default=0)
    leads_generated = models.IntegerField(default=0)
    leads_useful = models.IntegerField(default=0)

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

    # Static Variables
    plan_names = {0: "Free", 1: "Business Plus", 2: "Executive"}

    # Implement Each Feature via some key and then just check it its available for the current profile.
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

    def __unicode__(self):
        return self.user_from.user.username + ' ' + self.name + ' ' + self.social_media


class Feed(models.Model):
    description = models.CharField(max_length=10000)
    avatar_link = models.CharField(max_length=1000, default="/avatars/default-avatar.png")
    users = models.ManyToManyField(User)
    time = models.DateTimeField(auto_now_add=True)
    request = models.ForeignKey(Request, default=None, null=True, blank=True)
    response = models.ForeignKey(Response, default=None, null=True, blank=True)
    rank = models.IntegerField(default=100)
    custom_avatar = models.CharField(max_length=1000, default=None, null=True, blank=True)

    def update_self(self):
        if self.response == None:
            name = self.request.user.first_name + " " + self.request.user.last_name
            if self.request.anonymous:
                name = "Anonymous"
            if str(self.request.company) == '':
                description = "<a href='/request/view/" + str(
                    self.request.id) + "'>" + name + " - offering referral fee up to <strong>$" + \
                              '{0:,.0f}'.format(
                                  self.request.commission_end) + "</strong> for " + 'request <em>"' + str(
                    self.request.title) + '"</em></a>'
            else:
                description = "<a href='/request/view/" + str(
                    self.request.id) + "'>" + name + " (" + str(self.request.company) + \
                              ") - offering referral fee up to <strong>$" + \
                              '{0:,.0f}'.format(
                                  self.request.commission_end) + "</strong> for " + 'request <em>"' + str(
                    self.request.title) + '"</em></a>'
            self.description = description
            self.save()

    def __unicode__(self):
        return self.description


class Message(models.Model):
    message_to_user = models.ForeignKey(User, related_name='message_to_user')
    message_from_user = models.ForeignKey(User, related_name='message_from_user')
    message = models.CharField(default="", max_length=10000)
    created = models.DateTimeField(default=timezone.now())
    subject = models.CharField(default="", max_length=1000)
    request = models.ForeignKey(Request, default=None, null=True)

    def __unicode__(self):
        return "<strong>" + self.subject + "</strong> " + self.message

        # admin.site.register(UserProfile)


from django.contrib.auth.signals import user_logged_in
from mailer import send_mail


def do_stuff(sender, user, request, **kwargs):
    send_mail(user.username + ' has logged in.', '', 'info@mehelpyou.com',
              ['tejasmehta0@gmail.com', 'aazar_zafar@yahoo.ca'])


user_logged_in.connect(do_stuff)

watson.register(Feed, fields=("request__request", "request__title", "description"))
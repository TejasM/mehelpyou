import os
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
    from mailer import send_html_mail
else:
    from django.core.mail import send_mail
from django.db import models
from helpyou.group.models import Group
# Create your models here.
from django.utils import timezone


class Request(models.Model):
    ACCOUNTANT = "Accountant"
    FINANCIAL_ADVISOR = "Financial"
    LAWYER = "Lawyer"
    INVEST = "Investment Related"
    PROFESSIONAL_RECRUITING = "Professional Recruiting"
    REAL_ESTATE = "Real Estate"
    HEALTH_BEAUTY = "Health & Beauty Related"
    SCHOOL = "School Related"
    STARTUPS = "Startups Looking For Help"
    NON_PROFIT = "Non Profit / Charity"
    HOME_RELATED = "Home Related"
    OTHER = "Other"
    TECHNOLOGY = "Technology"

    CATEGORY_CHOICES = [(TECHNOLOGY, "Technology"), (ACCOUNTANT, "Accountant"),
                        (FINANCIAL_ADVISOR, "Financial"), (LAWYER, "Lawyer"),
                        (INVEST, "Investment Related"),
                        (PROFESSIONAL_RECRUITING, "Professional Recruiting"),
                        (REAL_ESTATE, "Real Estate"), (HEALTH_BEAUTY, "Health & Beauty Related"),
                        (SCHOOL, "School Related"), (STARTUPS, "Startups Looking For Help"),
                        (NON_PROFIT, "Non Profit / Charity"), (HOME_RELATED, "Home Related"),
                        (OTHER, "Other")]

    title = models.CharField(max_length=1000)
    user = models.ForeignKey(User)
    request = models.TextField()
    city = models.CharField(max_length=100, default="Toronto")
    company = models.CharField(max_length=200, blank=True)
    anonymous = models.BooleanField(default=False)
    due_by = models.DateTimeField()
    start_time = models.DateTimeField(default=timezone.now())
    approved = models.BooleanField(default=False)
    create_time = models.DateTimeField(default=timezone.now())

    commission_start = models.FloatField(default=0)
    commission_end = models.FloatField(default=0)

    category = models.CharField(max_length=200, default=OTHER, choices=CATEGORY_CHOICES)

    document = models.FileField(upload_to='files', blank=True, null=True)

    groups = models.ManyToManyField(Group, blank=True)

    def filename(self):
        return os.path.basename(self.document.name)

    def __unicode__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
        self.old_state = self.approved

    def save(self, *args, **kwargs):
        if self.old_state == False and self.approved == True:
            from helpyou.userprofile.models import Feed

            send_mail('Your Request is approved', 'Thank-you for posting your Referral Request on MeHelpYou.com.\n\n\
Now tell everyone you know to join so they can see your referral request and send referrals to YOU!\n\n\
To see your request, please go to this link: https://www.mehelpyou.com/request/view/' + str(self.id) + '\n\n\
Be proud - You are now part of the growing MeHelpYou community!\n\n\
We hope it benefits you and that you spread the word to those you know as it will increase visibility of your referral request.\n\n\
Please let us know if you have any feedback or comments.\n\nYours Sincerely,\n\
The MeHelpYou Team', 'info@mehelpyou.com', [self.user.email], fail_silently=True)
            self.old_state = True
            name = self.user.first_name + " " + self.user.last_name
            if self.anonymous:
                name = "Anonymous"
            if str(self.company) == '':
                description = "<a href='/request/view/" + str(
                    self.id) + "'>" + name + " - offering referral fee up to <strong>$" + \
                              '{0:,.0f}'.format(
                                  self.commission_end) + "</strong> for " + 'request <em>"' + str(
                    self.title) + '"</em></a>'
            else:
                description = "<a href='/request/view/" + str(
                    self.id) + "'>" + name + " (" + str(self.company) + \
                              ") - offering referral fee up to <strong>$" + \
                              '{0:,.0f}'.format(
                                  self.commission_end) + "</strong> for " + 'request <em>"' + str(
                    self.title) + '"</em></a>'

            feed = Feed.objects.create(description=description,
                                       avatar_link=self.user.user_profile.get().picture.url,
                                       request=self)
            if self.groups.count() > 0:
                list_all = []
                for users in list(self.groups.all().values_list('users')):
                    list_all.extend(users)
                for users in list(list(self.groups.all().values_list('administrators'))):
                    list_all.extend(users)
                list_all = filter(lambda x: x is not None, list_all)
                feed.users.add(*list_all)
            else:
                feed.users.add(*list(User.objects.all()))
            feed.save()
        super(Request, self).save(*args, **kwargs)

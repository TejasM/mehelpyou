import os
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db import models
from helpyou.group.models import Group
# Create your models here.
from django.utils import timezone


class Request(models.Model):
    ACCOUNTANT = "Accountant"
    FINANCIAL_ADVISOR = "Financial Advisor"
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
                        (FINANCIAL_ADVISOR, "Financial Advisor"), (LAWYER, "Lawyer"),
                        (INVEST, "Investment Related"),
                        (PROFESSIONAL_RECRUITING, "Professional Recruiting"),
                        (REAL_ESTATE, "Real Estate"), (HEALTH_BEAUTY, "Health & Beauty Related"),
                        (SCHOOL, "School Related"), (STARTUPS, "Startups Looking For Help"),
                        (NON_PROFIT, "Non Profit / Charity"), (HOME_RELATED, "Home Related"),
                        (OTHER, "Other")]

    title = models.CharField(max_length=1000)
    user = models.ForeignKey(User)
    request = models.CharField(max_length=100000)
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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.old_state == False and self.approved == True:
            msg = EmailMessage('Your Request is approved', 'Good News ! Your request has been approved for posting. \n\n\
            Thank-you for posting your Referral Request on MeHelpYou.com.\n\n\
            To see your request, please go to this link: https://www.mehelpyou.com/request/view/' + str(self.id) + '\n\n\
            Be proud - You are now part of the growing MeHelpYou community!\n\n\
            We hope it benefits you and that you spread the word to those you know as it will increase visibility of your referral request.\n\n\
            Please let us know if you have any feedback or comments.', 'info@mehelpyou.com', [self.user.email])
            msg.send()
        super(Request, self).save(force_insert, force_update)
        self.old_state = True
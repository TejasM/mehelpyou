import os
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from helpyou.group.models import Group
# Create your models here.
from django.utils import timezone


class Request(models.Model):
    ACCOUNTANT = "Accountant"
    FINANCIAL_ADVISOR = "Financial Advisor"
    LAWYER = "Lawyer"
    SALES = "Sales Lead Generation"
    INVEST = "Investment Related"
    PROFESSIONAL_RECRUITING = "Professional Recruiting"
    REAL_ESTATE = "Real Estate"
    HEALTH_BEAUTY = "Health & Beauty Related"
    SCHOOL = "School Related"
    STARTUPS = "Startups Looking For Help"
    NON_PROFIT = "Non Profit / Charity"
    HOME_RELATED = "Home Related"
    OTHER = "Other"

    CATEGORY_CHOICES = [(ACCOUNTANT, "Accountant"), (FINANCIAL_ADVISOR, "Financial Advisor"), (LAWYER, "Lawyer"),
                        (SALES, "Sales Lead Generation"), (INVEST, "Investment Related"), (PROFESSIONAL_RECRUITING, "Professional Recruiting"),
                        (REAL_ESTATE, "Real Estate"), (HEALTH_BEAUTY, "Health & Beauty Related"),
                        (SCHOOL, "School Related"), (STARTUPS, "Startups Looking For Help"),
                        (NON_PROFIT, "Non Profit / Charity"), (HOME_RELATED, "Home Related"),
                        (OTHER, "Other")]

    title = models.CharField(max_length=60)
    user = models.ForeignKey(User)
    request = models.CharField(max_length=10000)
    city = models.CharField(max_length=100, default="Toronto")
    company = models.CharField(max_length=200, blank=True)

    due_by = models.DateTimeField()
    start_time = models.DateTimeField(default=timezone.now())

    create_time = models.DateTimeField(default=timezone.now())

    commission_start = models.FloatField(default=0)
    commission_end = models.FloatField(default=0)

    category = models.CharField(max_length=200, default=OTHER, choices=CATEGORY_CHOICES)

    document = models.FileField(upload_to='files', blank=True, null=True)

    groups = models.ManyToManyField(Group)

    def filename(self):
        return os.path.basename(self.document.name)

    def __unicode__(self):
        return self.title

admin.site.register(Request)

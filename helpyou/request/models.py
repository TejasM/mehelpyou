from django.contrib.auth.models import User
from django.db import models


# Create your models here.
from django.utils import timezone


class Request(models.Model):
    ACCOUNTANT = "Accountant"
    FINANCIAL_ADVISOR =  "Financial Advisor"
    LAWYER = "Lawyer"
    SALES = "Sales Lead Generation"
    PROFESSIONAL_RECRUITING = "Professional Recruiting"
    REAL_ESTATE = "Real Estate"
    HEALTH_BEAUTY = "Health & Beauty Related"
    SCHOOL = "School Related"
    STARTUPS = "Startups Looking For Help"
    NON_PROFIT = "Non Profit / Charity"
    HOME_RELATED = "Home Related"
    OTHER = "Other"

    CATEGORY_CHOICES = [(ACCOUNTANT, "Accountant"), (FINANCIAL_ADVISOR, "Financial Advisor"), (LAWYER, "Lawyer"),
                        (SALES, "Sales Lead Generation"), (PROFESSIONAL_RECRUITING, "Professional Recruiting"),
                        (REAL_ESTATE, "Real Estate"), (HEALTH_BEAUTY, "Health & Beauty Related"),
                        (SCHOOL, "School Related"), (STARTUPS, "Startups Looking For Help"),
                        (NON_PROFIT, "Non Profit / Charity"), (HOME_RELATED, "Home Related"),
                        (OTHER, "Other")]

    title = models.CharField(max_length=60)
    city = models.CharField(max_length=100)
    user = models.ForeignKey(User)
    anon = models.BooleanField(default=False)
    request = models.CharField(max_length=1000)
    due_by = models.DateTimeField()
    create_time = models.DateTimeField(default=timezone.now())
    reward = models.FloatField()
    category = models.CharField(max_length=200, default=OTHER, choices=CATEGORY_CHOICES)

    def __unicode__(self):
        return self.title
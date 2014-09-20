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

    CATEGORY_IMAGES = ['https://www.pace.com/Global/Images/Header_Features/477x257_technology.jpg',
                       'http://i.telegraph.co.uk/multimedia/archive/01806/accounting_1806520c.jpg',
                       'http://www.matthewsnc.gov/portals/0/Departments/Finance/finance.jpg',
                       'http://cash-advance--loans.org/wp-content/uploads/2012/03/stock-investments.png',
                       'http://static.squarespace.com/static/5260940ee4b0e20972c81fe9/t/52926441e4b0661bae3d0965/1385325636935/recruiting-magnify.jpg',
                       'http://www.lohncaulder.com/wp-content/uploads/2013/12/house_for_sale.jpg',
                       'http://www.saytopic.com/wp-content/uploads/2014/05/Women-Health-And-Beauty-Go-Hand-In-Hand.jpg',
                       'http://i.telegraph.co.uk/multimedia/archive/02357/students_2357903b.jpg',
                       'http://genesismediation.com/wp-content/uploads/2010/04/Charities-Non-Profits-Free-Membership-1.jpg',
                       'http://onionuser.com/wp-content/uploads/2014/01/blank-avatar.jpg',
                       'http://www.other-themovie.com/other_logo_03.png']

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
    custom_avatar = models.CharField(max_length=1000, default=None, null=True, blank=True)

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

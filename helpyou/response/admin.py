from django.contrib import admin
from helpyou.response.models import Response
from helpyou.userprofile.models import Invitees

__author__ = 'tmehta'

admin.site.register(Response)
admin.site.register(Invitees)
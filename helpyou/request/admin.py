from django.contrib import admin
from helpyou.request.models import Request
from helpyou.userprofile.models import Feed

__author__ = 'tmehta'
admin.site.register(Feed)
admin.site.register(Request)

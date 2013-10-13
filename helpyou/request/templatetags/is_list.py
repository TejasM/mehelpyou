from django import template
from django.utils import timezone
from django.utils.datetime_safe import strftime

register = template.Library()
__author__ = 'tmehta'


@register.filter
def in_list_user(list_response, user):
    if user.is_authenticated():
        for response in list_response:
            if response.user == user:
                return True
    return False
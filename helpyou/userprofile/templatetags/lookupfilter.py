from django import template

register = template.Library()
__author__ = 'tmehta'


@register.filter
def lookup(d, key):
    return d[key]
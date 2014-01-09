from django import template

register = template.Library()
__author__ = 'tmehta'


@register.filter
def lookup(d, key):
    return d[key]


@register.filter
def getDate(d):
    return d.date()


@register.filter
def getTime(d):
    return d.time()


@register.filter
def getList(d, s):
    return d.getlist(s)
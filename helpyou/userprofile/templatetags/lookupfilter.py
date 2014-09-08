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


@register.filter
def return_string(d):
    string = '&quick_commission_start='
    string += '&quick_commission_start='.join(d.getlist('quick_commission_start'))
    string += '&quick_category='
    string += '&quick_category='.join(d.getlist('quick_category'))
    string += '&quick_city='
    string += '&quick_city='.join(d.getlist('quick_city'))
    return string
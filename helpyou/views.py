from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

__author__ = 'tmehta'


def index(request):
    if request.user.is_authenticated():
        return redirect(reverse('user:index'))
    else:
        return render(request, "base.html")
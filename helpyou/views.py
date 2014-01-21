from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from helpyou.userprofile.forms import SignupForm

__author__ = 'tmehta'


def index(request):
    if request.user.is_authenticated():
        return redirect(reverse('user:feed'))
    elif request.method == "POST":
        if request.POST['type'] == 'sign-up':
            form = SignupForm(request.POST)
            if form.is_valid():
                user = User.objects.create(username=form.data["email"], email=form.data["email"],
                                           first_name=form.data["first_name"],
                                           last_name=form.data["last_name"])
                user.set_password(form.data["password"])
                user.save()
                messages.success(request, 'Account created, please proceed by logging in.')
                return HttpResponseRedirect(reverse('user:feed'))
        elif request.POST['type'] == 'login':
            user = authenticate(username=request.POST.get('username', ''), password=request.POST.get('password', ''))
            if user is not None:
                if user.is_active:
                    login(request, user)
                else:
                    messages.success(request, 'Your account needs password reset, please follow link sent to your email')
                    render(request, "base-home.html", {'form': SignupForm()})
                return redirect(reverse('user:feed'))
            else:
                try:
                    User.objects.get(username=request.POST.get('username', ''))
                except User.DoesNotExist as _:
                    return render(request, "base-home.html", {'username': True, 'form': SignupForm()})
                return render(request, "base.html", {'password': True, 'form': SignupForm()})
    return render(request, "base-home.html", {'form': SignupForm()})
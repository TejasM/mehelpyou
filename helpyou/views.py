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
                user = authenticate(username=request.POST.get('email', ''), password=request.POST.get('password', ''))
                if user is not None:
                    if user.is_active:
                        login(request, user)
                    else:
                        messages.error(request, 'User is not active')
                        return redirect('/')
                else:
                    messages.error(request, 'No Such User')
                    return redirect('/')
                return redirect(reverse('user:feed'))
        elif request.POST['type'] == 'login':
            user = authenticate(username=request.POST.get('username', ''), password=request.POST.get('password', ''))
            if user is not None:
                if user.is_active:
                    login(request, user)
                else:
                    return redirect('/')
                return redirect(reverse('user:feed'))
            else:
                try:
                    User.objects.get(username=request.POST.get('username', ''))
                except User.DoesNotExist as _:
                    messages.error(request, 'No such user')
                    return redirect('/')
                messages.error(request, 'No Such User')
                return redirect('/')
    return render(request, "base-home.html", {'form': SignupForm()})


def about(request):
    return render(request, "about.html", {'form': SignupForm()})
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import password_reset_confirm, password_reset
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import Context, RequestContext
from django.template.loader import get_template
from helpyou.request.models import Request
from helpyou.userprofile.forms import SignupForm
from helpyou.userprofile.models import UserProfile

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
    from mailer import send_html_mail
else:
    from django.core.mail import send_mail
__author__ = 'tmehta'


def reset_confirm(request, uibd):
    if request.method == "POST":
        email = request.POST['email']
        try:
            user = User.objects.get(username=email)
        except:
            messages.error(request, 'No such user')
            return redirect(reverse('index'))
        newpass = request.POST['password']
        user.set_password(newpass)
        user.save()
        return redirect(reverse('index'))
    else:
        try:
            user = User.objects.get(password=uibd)
        except:
            messages.error(request, 'Incorrect token')
            return redirect(reverse('index'))
        reset_form = True
        featured_requests = []
        featured_requests_id = [13, 2, 4, 3, 5, 7, 9, 10, 6, 12, 11]
        try:
            for r_id in featured_requests_id:
                featured_requests.append(Request.objects.get(pk=r_id))
        except Request.DoesNotExist:
            pass
        return render(request, "base-home.html",
                      {'form': SignupForm(), 'featured_requests': featured_requests, 'reset_form': reset_form})


def reset(request):
    if request.method == "POST":
        email = request.POST['email']
        try:
            user = User.objects.get(username=request.POST.get('email', ''))
        except User.DoesNotExist:
            messages.error(request, 'No such user')
            return redirect(reverse('index'))
        t = get_template('app/password_reset_email.html')
        c = RequestContext(request, {'email': email, 'uid': user.password})
        send_html_mail('Password Reset', '', t.render(c), 'info@mehelpyou.com', [user.email])
        messages.error(request, "An email with a password reset link has been sent.")
        return redirect(reverse('index'))
    return redirect(reverse('index'))


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
                if 'invite' in request.GET:
                    try:
                        p = UserProfile.objects.get(special_hash=request.GET['invite'])
                        p.signups += 1
                        p.save()
                    except UserProfile.DoesNotExist:
                        pass
                user = authenticate(username=request.POST.get('email', ''),
                                    password=request.POST.get('password', ''))
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
            else:
                messages.error(request, form.errors)
                return redirect('/')
        elif request.POST['type'] == 'login':
            user = authenticate(username=request.POST.get('username', ''),
                                password=request.POST.get('password', ''))
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
                messages.error(request, 'Incorrect Password')
                return redirect('/')
    featured_requests = []
    featured_requests_id = [13, 24, 4, 3, 5, 7, 9, 10, 6, 12, 11]
    try:
        for r_id in featured_requests_id:
            featured_requests.append(Request.objects.get(pk=r_id))
    except Request.DoesNotExist:
        pass
    if 'invite' in request.GET:
        try:
            p = UserProfile.objects.get(special_hash=request.GET['invite'])
            p.ins += 1
            p.save()
        except UserProfile.DoesNotExist:
            pass
    return render(request, "base-home.html", {'form': SignupForm(), 'featured_requests': featured_requests})


def about(request):
    return render(request, "about.html", {'form': SignupForm()})
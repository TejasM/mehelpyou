# Create your views here.
import urllib
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from social_auth.db.django_models import UserSocialAuth
from forms import SignupForm, UserProfileForm, UserPicForm
from helpyou.notifications.views import new_notifications
from models import UserProfile, UserPic


def MassPay(email, amt):
        params = {
            'USER': 'tejasmehta_api1.gmail.com',
            'PWD': 'VRKKVCB78H5CEZHV',
            'SIGNATURE': 'Ai1PaghZh5FmBLCDCTQpwG8jB264Al1J8WzpssiP53PSRB0BRkvxyImn',
            'VERSION': '2.3',
            'EMAILSUBJECT': 'You have money',
            'METHOD': "MassPay",
            'RECEIVERTYPE': "EmailAddress",
            'L_AMT0': amt,
            'CURRENCYCODE': 'CAD',
            'L_EMAIL0': email,
        }
        params_string = urllib.urlencode(params)
        response = urllib.urlopen("https://api-3t.sandbox.paypal.com/nvp", params_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        for key in response_tokens.keys():
            response_tokens[key] = urllib.unquote(response_tokens[key])
        return response_tokens

@new_notifications
def logout_view(request):
    logout(request)
    return redirect('/')


@new_notifications
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user:login'))
    else:
        form = SignupForm()
    return render(request, "userprofile/signup.html", {'form': form})


@new_notifications
def user_view(request, username):
    user = User.objects.get(username=username)
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=user)
    return render(request, "userprofile/profile.html", {"other_profile": profile})


@new_notifications
def loginUser(request):
    if request.method == "POST":
        user = authenticate(username=request.POST.get('username', ''), password=request.POST.get('password', ''))
        if user is not None:
            login(request, user)
            return redirect(reverse('user:index'))
        else:
            try:
                User.objects.get(username=request.POST.get('username', ''))
            except User.DoesNotExist as _:
                return render(request, "userprofile/login.html", {'username': True})
            return render(request, "userprofile/login.html", {'password': True})
    return render(request, "userprofile/login.html")


@new_notifications
def index(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=request.user)
    try:
        social_user = UserSocialAuth.objects.get(user=request.user)
        print social_user.extra_data
    except UserSocialAuth.DoesNotExist as _:
        pass
    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            profile_created = form.save(commit=False)
            profile.interests = profile_created.interests
            profile.skills = profile_created.skills
            profile.save()
            return redirect(reverse('user:index'))
    else:
        form = UserProfileForm(instance=profile)

    return render(request, "userprofile/profile.html",
                  {'profile': profile, 'form': form})


@new_notifications
def addPic(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    if request.method == "POST":
        form = UserPicForm(request.POST)
        if form.is_valid():
            try:
                pic = UserPic.objects.get(user=request.user)
            except UserPic.DoesNotExist as _:
                pic = UserPic.objects.create(user=request.user)
            pic_create = form.save(commit=False)
            pic.image = pic_create.image
            pic.save()
            return redirect(reverse('user:index'))
    else:
        return redirect(reverse('user:index'))


@new_notifications
def collect(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    try:
        profile = UserProfile.objects.get(user=request.user)
        if request.POST.get("email", '') != '':
            email = request.POST["email"]
        else:
            email = profile.paypal_email
        if email == '':
            return redirect(reverse('user:index'))
        response = MassPay(request.POST["email"], request.POST["amount"])
        if str(response["ACK"]) != "Failure":
            profile.money_current -= float(request.POST["amount"])
            profile.save()
        else:
            messages.error(request, "Failed to transfer money please try again later!")
        return redirect(reverse('user:index'))
    except Exception as e:
        return redirect(reverse('user:index'))

# Create your views here.
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from forms import SignupForm, UserProfileForm
from models import UserProfile


def logout_view(request):
    logout(request)
    return redirect('/')


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user:login'))
    else:
        form = SignupForm()
    return render(request, "userprofile/signup.html", {'form': form})


def user_view(request, username):
    user = User.objects.get(username=username)
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=user)
    return render(request, "userprofile/profile.html", {"other_profile": profile})


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


def index(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=request.user)
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

    return render(request, "userprofile/profile.html", {'profile': profile, 'form': form})

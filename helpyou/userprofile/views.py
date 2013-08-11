# Create your views here.
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from forms import SignupForm, UserProfileForm, UserPicForm
from helpyou.notifications.views import new_notifications
from models import UserProfile, UserPic


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
    if request.method == "POST":
        form = UserProfileForm(request.POST)
        form_pic = UserPicForm(request.POST, request.FILES)
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
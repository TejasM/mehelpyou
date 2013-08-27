# Create your views here.
import urllib
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
import facebook
from social_auth.db.django_models import UserSocialAuth
from forms import SignupForm, UserProfileForm, UserPicForm
from helpyou.notifications.models import Notification
from helpyou.notifications.views import new_notifications
from models import UserProfile, UserPic


def sync_up_user(user, social_user):
    if social_user.provider == 'linkedin':
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist as _:
            profile = UserProfile.objects.create(user=user)
        if profile.industry == '' and "industry" in social_user.extra_data:
            profile.industry = social_user.extra_data["industry"]
        if profile.educations == '' and "educations" in social_user.extra_data and len(
                social_user.extra_data["educations"]) <= 10000:
            profile.educations = social_user.extra_data["educations"]
        if profile.interests == '' and "interests" in social_user.extra_data and len(
                social_user.extra_data["interests"]) <= 10000:
            profile.interests = social_user.extra_data["interests"]
        if profile.skills == '' and "skills" in social_user.extra_data and len(
                social_user.extra_data["skills"]) <= 10000:
            profile.skills = social_user.extra_data["skills"]
        if profile.num_recommenders == '' and "num_recommenders" in social_user.extra_data:
            profile.num_recommenders = int(social_user.extra_data["num_recommenders"])
        if profile.num_connections == '' and "num_connections" in social_user.extra_data:
            profile.num_connections = int(social_user.extra_data["num_connections"])
        if profile.recommendations_received == '' and "recommendations_received" in social_user.extra_data and len(
                social_user.extra_data["recommendations_received"]) <= 10000:
            profile.recommendations_received = social_user.extra_data["recommendations_received"]
        if "connections" in social_user.extra_data:
            for connection in social_user.extra_data["connections"]['person']:
                try:
                    connect = UserSocialAuth.objects.get(uid=connection["id"])
                    if connect.user not in profile.connections.all():
                        profile.connections.add(connect.user)
                    try:
                        connect = UserProfile.objects.get(user=connect.user)
                    except UserProfile.DoesNotExist as _:
                        connect = UserProfile.objects.create(user=connect.user)
                    connect.connections.add(user)
                    connect.save()
                except UserSocialAuth.DoesNotExist as _:
                    continue
        profile.save()
    elif social_user.provider == 'facebook':
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist as _:
            profile = UserProfile.objects.create(user=user)
        graph = facebook.GraphAPI(social_user.extra_data["access_token"])
        friends = graph.get_connections("me", "friends")
        for friend in friends['data']:
            try:
                connect = UserSocialAuth.objects.get(uid=friend["id"])
                if connect.user not in profile.connections.all():
                    profile.connections.add(connect.user)
                try:
                    connect = UserProfile.objects.get(user=connect.user)
                except UserProfile.DoesNotExist as _:
                    connect = UserProfile.objects.create(user=connect.user)
                connect.connections.add(user)
                connect.save()
            except UserSocialAuth.DoesNotExist as _:
                continue
        profile.save()


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
            user = User.objects.create(username=form.data["email"], email=form.data["email"],
                                       first_name=form.data["first_name"],
                                       last_name=form.data["last_name"])
            user.set_password(form.data["password"])
            user.save()
            return HttpResponseRedirect(reverse('user:login'))
    else:
        form = SignupForm()
    return render(request, "userprofile/signup.html", {'form': form})


@new_notifications
def user_view(request, username):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    user = User.objects.get(username=username)
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=user)
    connected = False
    invitation = False
    try:
        my_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist as _:
        my_profile = UserProfile.objects.create(user=request.user)
    if user in my_profile.connections.all():
        connected = True
    if not connected:
        try:
            Notification.objects.filter(user=request.user, to_user=user)
            invitation = True
        except Notification.DoesNotExist as _:
            pass
    return render(request, "userprofile/profile.html",
                  {"other_profile": profile, "connected": connected, "invitation": invitation})


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
        if form.is_valid():
            profile_created = form.save(commit=False)
            profile.interests = profile_created.interests
            profile.skills = profile_created.skills
            profile.city = profile_created.city
            profile.educations = profile_created.educations
            profile.industry = profile_created.industry
            profile.save()
            return redirect(reverse('user:index'))
    else:
        try:
            social_user = UserSocialAuth.objects.get(user=request.user)
            sync_up_user(request.user, social_user)
        except UserSocialAuth.DoesNotExist as _:
            pass
        form = UserProfileForm(instance=profile)
    return render(request, "userprofile/profile.html",
                  {'profile': profile, 'form': form})


@new_notifications
def invite_connection(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    if request.method == "POST":
        Notification.objects.create(user_id=request.POST["id"], message="IN", to_user=request.user)
    return redirect(reverse('user:index'))


@new_notifications
def accept_connection(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=request.user)
    if request.method == "POST":
        user = User.objects.get(pk=request.POST["id"])
        Notification.objects.create(user=user, message="AN", to_user=request.user)
        profile.connections.add(user)
        profile.save()
        try:
            profile2 = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist as _:
            profile2 = UserProfile.objects.create(user=user)
        profile2.connections.add(request.user)
        profile2.save()
    return redirect(reverse('user:index'))


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

# Create your views here.
from __future__ import division
import json
import urllib
from urllib2 import Request, HTTPError
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import render, redirect
import facebook
import requests
from social_auth.db.django_models import UserSocialAuth
from social_auth.utils import dsa_urlopen
import stripe
from forms import SignupForm, UserProfileForm, UserPicForm
from helpyou import settings
from helpyou.notifications.models import Notification
from helpyou.notifications.views import new_notifications
from helpyou.userprofile.models import Invitees
from models import UserProfile, UserPic


def sync_up_user(user, social_users):
    for social_user in social_users:
        if social_user.provider == 'linkedin-oauth2':
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist as _:
                profile = UserProfile.objects.create(user=user)
            if profile.industry == '' and "industry" in social_user.extra_data and social_user.extra_data["industry"]:
                profile.industry = social_user.extra_data["industry"]
            if profile.educations == '' and "educations" in social_user.extra_data and social_user.extra_data["educations"] \
                and len(social_user.extra_data["educations"]) <= 10000:
                for education in social_user.extra_data["educations"]['values']:
                    if 'school-name' in education and education['school-name']:
                        profile.educations += education['school-name']
                    if 'field-of-study' in education and education['field-of-study']:
                        profile.educations += ": " + education['field-of-study'] + "\n"
            if profile.interests == '' and "interests" in social_user.extra_data and social_user.extra_data["interests"] \
                and len(social_user.extra_data["interests"]) <= 10000:
                profile.interests = social_user.extra_data["interests"]
            if profile.skills == '' and "skills" in social_user.extra_data and social_user.extra_data["skills"] and len(
                    social_user.extra_data["skills"]) <= 10000:
                for skill in social_user.extra_data["skills"]['values']:
                    profile.skills += skill["skill"]["name"] + ", "
            if profile.num_recommenders == '' and "num_recommenders" in social_user.extra_data and social_user.extra_data[
                "num_recommenders"]:
                profile.num_recommenders = int(social_user.extra_data["num_recommenders"])
            if profile.recommendations_received == '' and "recommendations_received" in social_user.extra_data and social_user.extra_data["recommendations_received"] and len(
                social_user.extra_data["recommendations_received"]) <= 10000:
                profile.recommendations_received = social_user.extra_data["recommendations_received"]
            if "connections" in social_user.extra_data and social_user.extra_data["connections"]:
                profile.num_connections = social_user.extra_data["connections"]["_total"]
                for connection in social_user.extra_data["connections"]['values']:
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
                        try:
                            Invitees.objects.get(uid=connection["id"], user_from=profile)
                        except Invitees.DoesNotExist as _:
                            Invitees.objects.create(uid=connection["id"], user_from=profile,
                                                    name=connection['firstName'] + " " + connection['lastName'],
                                                    social_media='linkedin-oauth2')
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
                    try:
                        Invitees.objects.get(uid=friend["id"], user_from=profile)
                    except Invitees.DoesNotExist as _:
                        Invitees.objects.create(uid=friend["id"], user_from=profile,
                                                name=friend['name'], social_media='facebook')
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
def user_view(request, user_id):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    user = User.objects.get(pk=user_id)
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
    if request.user.is_authenticated():
        try:
            social_users = UserSocialAuth.objects.filter(user=request.user)
            sync_up_user(request.user, social_users)
        except UserSocialAuth.DoesNotExist as _:
            pass
        return redirect(reverse('user:index'))
    if request.method == "POST":
        user = authenticate(username=request.POST.get('username', ''), password=request.POST.get('password', ''))
        if user is not None:
            login(request, user)
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
            messages.error(request, "Incorrect Paypal address!")
            return redirect(reverse('user:index'))
        response = MassPay(request.POST["email"], float(request.POST["amount"])/2)
        if str(response["ACK"]) != "Failure":
            profile.points_current -= float(request.POST["amount"])
            profile.save()
        else:
            messages.error(request, "Failed to transfer money please try again later!")
        return redirect(reverse('user:index'))
    except Exception as e:
        return redirect(reverse('user:index'))


def send_user_invites(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    if request.method == "POST":
        # Get and send invites
        user_ids = request.POST.getlist('users_invite')
        social_users = UserSocialAuth.objects.filter(user=request.user)
        linkedin_invites = []
        facebook_invites = []
        for user_id in user_ids:
            invitee = Invitees.objects.get(pk=user_id)
            if invitee.social_media == 'linkedin-oauth2':
                linkedin_invites.append(invitee)
            if invitee.social_media == 'facebook':
                facebook_invites.append(invitee)
        message = request.POST.get('message',
                                       'I am inviting you to use MeHelpYou, to make and get referrals and money! www.mehelpyou.com')
        for social_user in social_users:
            if social_user.provider == 'linkedin-oauth2':
                send_message = {"recipients": {
                    "values": []
                },
                                "subject": "Invited to Me Help You",
                                "body": message
                }
                for invitee in linkedin_invites:
                    send_message["recipients"]["values"].append({"person": {
                                                                "_path": "/people/" + str(invitee.uid),
                                                                }
                                                                },)
                token = social_user.tokens["access_token"]
                url = "https://api.linkedin.com/v1/people/~/mailbox"
                response = make_request(url, token, data=json.dumps(send_message))
                if response.reason == 'Created':
                    for invitee in linkedin_invites:
                        invitee.delete()
            elif social_user.provider == 'facebook':
                if social_user.extra_data["access_token"]:
                    to = ""
                    for invitee in facebook_invites:
                        to += invitee.uid + ","
                    to = to[:-1]
                    url = "https://www.facebook.com/dialog/feed?to=" + to + "&app_id=" + \
                          settings.FACEBOOK_APP_ID + "&message=" + message + "&" \
                          "redirect_uri=http://" + request.get_host() + "/users/"
                    for invitee in facebook_invites:
                        invitee.delete()
                    return redirect(url)
            return redirect(reverse('user:index'))
    else:
        return redirect(reverse('user:index'))


def make_request(url, token, data=None):
        headers = {'x-li-format': 'json', 'Content-Type': 'application/json'}
        kw = dict(data=data, params={'oauth2_access_token': token},
                  headers=headers)
        return requests.request("POST", url, **kw)


@new_notifications
def buy_points(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    if request.method == "POST":
        token = request.POST['stripeToken']
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Create the charge on Stripe's servers - this will charge the user's card
        try:
            stripe.Charge.create(
                amount=int(int(request.POST['points']) * 100), # amount in cents, again
                currency="cad",
                card=token,
                description=request.user.username,
            )
            profile = UserProfile.objects.get(user=request.user)
            profile.points_current += float(request.POST['points'])
            profile.save()
            return redirect(reverse('user:index'))
        except stripe.CardError, _:
            return redirect(reverse('user:index'))
    else:
        return redirect(reverse('user:index'))

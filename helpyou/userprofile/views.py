# Create your views here.
from __future__ import division
from datetime import timedelta
import json
import urllib
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import facebook
import oauth2
import requests
from social_auth.db.django_models import UserSocialAuth
import stripe
import twitter
from forms import SignupForm, UserProfileForm
from helpyou import settings
from helpyou.request.models import Request
from helpyou.notifications.models import Notification
from helpyou.notifications.views import new_notifications
from helpyou.userprofile.forms import UserSettingsForm
from helpyou.userprofile.models import Invitees, plan_points, plan_costs
from models import UserProfile
if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
    from mailer import send_html_mail
else:
    from django.core.mail import send_mail


def sync_up_user(user, social_users):
    for social_user in social_users:
        if social_user.provider == 'linkedin':
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist as _:
                profile = UserProfile.objects.create(user=user)
            if profile.last_updated < timezone.now() - timedelta(weeks=2):
                if profile.industry == '' and "industry" in social_user.extra_data and social_user.extra_data["industry"]:
                    profile.industry = social_user.extra_data["industry"]
                if profile.educations == '' and "educations" in social_user.extra_data and social_user.extra_data["educations"] \
                    and len(social_user.extra_data["educations"]) <= 10000:
                    for education in social_user.extra_data["educations"].values():
                        if 'school-name' in education and education['school-name']:
                            profile.educations += education['school-name']
                        if 'field-of-study' in education and education['field-of-study']:
                            profile.educations += ": " + education['field-of-study'] + "\n"
                if profile.interests == '' and "interests" in social_user.extra_data and social_user.extra_data["interests"] \
                    and len(social_user.extra_data["interests"]) <= 10000:
                    profile.interests = social_user.extra_data["interests"]
                if profile.skills == '' and "skills" in social_user.extra_data and social_user.extra_data["skills"] and len(
                        social_user.extra_data["skills"]) <= 10000:
                    for skill in social_user.extra_data["skills"]['skill']:
                        profile.skills += skill["skill"]["name"] + ", "
                if profile.num_recommenders == '' and "num_recommenders" in social_user.extra_data and social_user.extra_data[
                    "num_recommenders"]:
                    profile.num_recommenders = int(social_user.extra_data["num_recommenders"])
                if profile.recommendations_received == '' and "recommendations_received" in social_user.extra_data and social_user.extra_data["recommendations_received"] and len(
                    social_user.extra_data["recommendations_received"]) <= 10000:
                    profile.recommendations_received = social_user.extra_data["recommendations_received"]
                if "connections" in social_user.extra_data and social_user.extra_data["connections"]:
                    profile.num_connections = len(social_user.extra_data["connections"]["person"])
                    for connection in social_user.extra_data["connections"]["person"]:
                            connects = UserSocialAuth.objects.filter(uid=connection["id"])
                            if len(connects) == 0:
                                try:
                                    Invitees.objects.get(uid=connection["id"], user_from=profile)
                                except Invitees.DoesNotExist as _:
                                    Invitees.objects.create(uid=connection["id"], user_from=profile,
                                                            name=connection['first-name'] + " " + connection['last-name'],
                                                            social_media='linkedin-oauth2')
                                continue
                            else:
                                for connect in connects:
                                    if connect.user not in profile.connections.all():
                                        profile.connections.add(connect.user)
                                    try:
                                        connect = UserProfile.objects.get(user=connect.user)
                                    except UserProfile.DoesNotExist as _:
                                        connect = UserProfile.objects.create(user=connect.user)
                                    connect.connections.add(user)
                                    try:
                                        Invitees.objects.get(uid=social_user.id, user_from=connect).delete()
                                    except Invitees.DoesNotExist as _:
                                        pass
                                    connect.save()
                if 'default-avatar.png' in str(profile.picture):
                    token = social_user.tokens["access_token"].split('oauth_token=')[-1]
                    url = "https://api.linkedin.com/v1/people/~/picture-urls::(original)"
                    try:
                        consumer = oauth2.Consumer(
                                 key=settings.LINKEDIN_CONSUMER_KEY,
                                 secret=settings.LINKEDIN_CONSUMER_SECRET)
                        token = oauth2.Token(
                             key=token,
                             secret=social_user.tokens["access_token"].split('oauth_token_secret=')[1].split('&')[0])
                        client = oauth2.Client(consumer, token)
                        response, content = client.request(url)
                        if '<picture-url key="original">' in content:
                            content = content.split('<picture-url key="original">')[1].split('</picture-url>')[0]
                            file_content = ContentFile(urllib.urlopen(content).read())
                            profile.picture.save(str(profile.user.first_name) + ".png", file_content)
                    except Exception as _:
                        pass
                profile.save()

        elif social_user.provider == 'facebook':
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist as _:
                profile = UserProfile.objects.create(user=user)
            if profile.last_updated < timezone.now() - timedelta(weeks=2):
                graph = facebook.GraphAPI(social_user.extra_data["access_token"])
                friends = graph.get_connections("me", "friends")
                profile.num_connections = len(friends['data'])
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
                if 'default-avatar.png' in str(profile.picture):
                    graph = facebook.GraphAPI(social_user.extra_data["access_token"])
                    picture = graph.get_object("me", fields="picture.width(460).height(460)")["picture"]["data"]["url"]
                    file_content = ContentFile(urllib.urlopen(picture).read())
                    profile.picture.save(str(profile.user.first_name) + ".png", file_content)
                profile.save()

        elif social_user.provider == 'twitter':
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist as _:
                profile = UserProfile.objects.create(user=user)
            if profile.last_updated < timezone.now() - timedelta(weeks=2):
                api = twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY,
                                  consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                                  access_token_key=social_user.tokens['oauth_token'],
                                  access_token_secret=social_user.tokens['oauth_token_secret'])
                friends = api.GetFollowers()
                profile.num_connections = len(friends)
                for friend in friends:
                    try:
                        connect = UserSocialAuth.objects.get(uid=friend.id)
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
                            Invitees.objects.get(uid=friend.id, user_from=profile)
                        except Invitees.DoesNotExist as _:
                            Invitees.objects.create(uid=friend.id, user_from=profile,
                                                    name=friend.name, social_media='twitter')
                if 'default-avatar.png' in str(profile.picture):
                    if "profile_picture" in social_user.extra_data and social_user.extra_data["profile_picture"]:
                        file_content = ContentFile(urllib.urlopen(social_user.extra_data["profile_picture"].replace('_normal', '')).read())
                        if str(profile.picture) != 'default-avatar.png':
                            profile.picture.delete()
                        profile.picture.save(str(profile.user.first_name) + ".png", file_content)
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
            messages.success(request, 'Account created, please proceed by logging in.')
            return HttpResponseRedirect(reverse('user:login'))
    else:
        form = SignupForm()
    return render(request, "userprofile/signup.html", {'form': form})


@new_notifications
def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        users = User.objects.filter(email=email)
        if len(users) == 0:
            messages.success(request, 'Sorry no user with that email address was found')
            return HttpResponseRedirect(reverse('user:forgot_password'))
        for user in users:
            if user.social_auth.count() == 0:
                user.is_active = False
                user.save()
                send_html_mail('Your MeHelpYou Password Recovery', "",
                          settings.ForgotEmail(user.username, 'www.mehelpyou.com/users/reset_password/' + str(user.id)),
                  'info@mehelpyou.com', [email], fail_silently=True)
        messages.success(request, 'Email sent. Please check your email for your link to reset your password')
        return HttpResponseRedirect(reverse('user:login'))
    return render(request, "userprofile/forgot_password.html")


@new_notifications
def reset_password(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist as _:
        messages.success(request, 'Sorry no user with that email address was found')
        return HttpResponseRedirect(reverse('user:forgot_password'))
    if user.is_active:
        return HttpResponseRedirect(reverse('user:index'))
    if request.method == "POST":
        new_password = request.POST['new_password']
        user.is_active = True
        user.set_password(new_password)
        user.save()
        messages.success(request, 'Password has been changed. You may now proceed to login')
        return HttpResponseRedirect(reverse('user:login'))
    return render(request, "userprofile/reset_password.html", {'user_id': user_id})


@login_required
@new_notifications
def user_view(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.user == user:
        return redirect(reverse('user:index'))
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=user)
    connected = False
    invitation_from = False
    invitation_to = False
    try:
        my_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist as _:
        my_profile = UserProfile.objects.create(user=request.user)
    if user in my_profile.connections.all():
        connected = True
    if not connected:
        try:
            notificiation = Notification.objects.filter(user=user, to_user=request.user, message="IN")
            if notificiation:
                invitation_from = True
            notificiation = Notification.objects.filter(user=request.user, to_user=user, message="IN")
            if notificiation:
                invitation_to = True
        except Notification.DoesNotExist as _:
            pass
    return render(request, "userprofile/profile.html",
                  {"other_profile": profile, "connected": connected, "invitation_from": invitation_from,
                   "invitation_to": invitation_to, 'requests': Request.objects.filter(user=user)})


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
            if user.is_active:
                login(request, user)
            else:
                messages.success(request, 'Your account needs password reset, please follow link sent to your email')
            return redirect(reverse('user:index'))
        else:
            try:
                User.objects.get(username=request.POST.get('username', ''))
            except User.DoesNotExist as _:
                return render(request, "userprofile/login.html", {'username': True})
            return render(request, "userprofile/login.html", {'password': True})
    return render(request, "userprofile/login.html")


@login_required
@new_notifications
def index(request):
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


@login_required
@new_notifications
def settings_user(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=request.user)
    if request.method == "POST":
        form = UserSettingsForm(request.POST)
        if form.is_valid():
            profile_created = form.save(commit=False)
            profile.notification_response = profile_created.notification_response
            profile.notification_connection_request = profile_created.notification_connection_request
            profile.notification_reward = profile_created.notification_reward
            profile.save()
            return redirect(reverse('user:index'))
    else:
        form = UserSettingsForm(instance=profile)
    return render(request, "userprofile/settings.html",
                  {'profile': profile, 'form': form})

@new_notifications
def invite_connection(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    if request.method == "POST":
        messages.success(request, 'Invitation Sent to ' + request.user.username)
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
def cancel_connection(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=request.user)
    if request.method == "POST":
        user = User.objects.get(pk=request.POST["id"])
        notifications = Notification.objects.filter(user=request.user, to_user=user)
        for notification in notifications:
            notification.delete()
        profile.save()
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
        response = MassPay(request.POST["email"], float(request.POST["amount"]))
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
        user_ids = request.POST.getlist('invites[]')
        social_users = UserSocialAuth.objects.filter(user=request.user)
        linkedin_invites = []
        facebook_invites = []
        twitter_invites = []
        for user_id in user_ids:
            invitee = Invitees.objects.get(pk=user_id)
            if invitee.social_media == 'linkedin-oauth2':
                linkedin_invites.append(invitee)
            elif invitee.social_media == 'facebook':
                facebook_invites.append(invitee)
            elif invitee.social_media == 'twitter':
                twitter_invites.append(invitee)
        message = request.POST.get('message',
                                   'I am inviting you to use MeHelpYou, to make and ' +
                                   'get referrals and money! www.mehelpyou.com')
        successes = []
        for social_user in social_users:
            if social_user.provider == 'linkedin':
                chunks = [linkedin_invites[x:x+50] for x in xrange(0, len(linkedin_invites), 50)]
                for chunk in chunks:
                    send_message = {"recipients": {
                        "values": []
                    },
                        "subject": "Invited to Me Help You",
                        "body": message
                    }
                    for invitee in chunk:
                        if str(invitee.uid) != "private":
                            send_message["recipients"]["values"].append({"person": {
                                                                    "_path": "/people/" + str(invitee.uid),
                                                                    }
                                                                    },)
                    consumer = oauth2.Consumer(
                         key=settings.LINKEDIN_CONSUMER_KEY,
                         secret=settings.LINKEDIN_CONSUMER_SECRET)
                    token = oauth2.Token(
                         key=social_user.tokens["access_token"].split('oauth_token=')[-1],
                         secret=social_user.tokens["access_token"].split('oauth_token_secret=')[1].split('&')[0])
                    client = oauth2.Client(consumer, token)
                    url = "https://api.linkedin.com/v1/people/~/mailbox"
                    response, content = client.request(url, method="POST", body=json.dumps(send_message), headers={'x-li-format': 'json', 'Content-Type': 'application/json'})
                    if response.status == 201 or response.status == 200:
                        for invitee in chunk:
                            successes.append(invitee.name)
                            invitee.delete()
            elif social_user.provider == 'facebook':
                if social_user.extra_data["access_token"]:
                    to = ""
                    for invitee in facebook_invites:
                        to += invitee.uid + ","
                    to = to[:-1]
                    url = "https://www.facebook.com/dialog/send?to=" + to + "&app_id=" + \
                          settings.FACEBOOK_APP_ID + "&link=www.mehelpyou.com&redirect_uri=http://" + \
                          request.get_host() + "/users/"
                    for invitee in facebook_invites:
                        invitee.delete()
                    return redirect(url)
            elif social_user.provider == 'twitter':
                if social_user.tokens["oauth_token"]:
                        api = twitter.Api(consumer_key=settings.TWITTER_CONSUMER_KEY,
                                          consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                                          access_token_key=social_user.tokens['oauth_token'],
                                          access_token_secret=social_user.tokens['oauth_token_secret'])
                        for invitee in twitter_invites:
                            try:
                                api.PostDirectMessage(message, user_id=invitee.uid)
                                successes.append(invitee.name)
                                invitee.delete()
                            except twitter.TwitterError as _:
                                pass
            messages.success(request, "Your Invitations were sent to: " + ", ".join(map(str, successes)))
        return redirect(request.GET['next'])
    else:
        return redirect(reverse('user:index'))


def make_request(url, token, data=None, method="POST"):
        headers = {'x-li-format': 'json', 'Content-Type': 'application/json'}
        kw = dict(data=data, headers=headers)
        return requests.request(method, url, **kw)


@new_notifications
def buy_points(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    if request.method == "POST":
        token = request.POST['stripeToken']
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Create the charge on Stripe's servers - this will charge the user's card
        try:
            profile = UserProfile.objects.get(user=request.user)
            customer = stripe.Customer.retrieve(id=profile.customer)
            customer.card = token
            customer.save()
            if profile.customer:
                stripe.Charge.create(
                    amount=int(int(request.POST['points']) * 100), # amount in cents, again
                    currency="cad",
                    customer=profile.customer,
                    description=request.user.username,
                )
            else:
                customer = stripe.Customer.create(card=token, email=request.user.email)
                charge = stripe.Charge.create(
                    amount=int(int(request.POST['points']) * 100), # amount in cents, again
                    currency="cad",
                    customer=customer,
                    description=request.user.username,
                )
                profile.customer = charge["customer"]
            profile.points_current += float(request.POST['points'])
            profile.save()
            return redirect(reverse('user:index'))
        except stripe.CardError, _:
            return redirect(reverse('user:index'))
    else:
        return redirect(reverse('user:index'))


def pricing(request):
    if not request.user.is_authenticated():
        return render(request, "userprofile/pricing.html")
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=request.user)
    if request.method == "POST":
        token = request.POST.get('stripeToken', '')
        plan = request.POST['plan']
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Create the charge on Stripe's servers - this will charge the user's card
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.customer:
                c = stripe.Customer.retrieve(str(profile.customer))
                if int(plan) == 0:
                    c.cancel_subscription()
                else:
                    if int(plan) > int(profile.plan):
                        c.update_subscription(plan=profile.plan_names[int(plan)].lower().replace(" ", "_"),
                                              prorate="True")
                        messages.success(request, "Points will be added in a few minutes.")
                    else:
                        c.update_subscription(plan=profile.plan_names[int(plan)].lower().replace(" ", "_"),
                                              prorate="False")
                profile.prev_plan = profile.plan
                profile.plan = int(plan)
            else:
                customer = stripe.Customer.create(
                    plan=profile.plan_names[int(plan)].lower().replace(" ", "_"),
                    card=token,
                    email=request.user.email,
                    description=request.user.email,
                )

                profile.customer = customer.id
                profile.plan = plan
                messages.success(request, "Points will be added in a few minutes.")
            profile.save()
            return redirect(reverse('user:index'))
        except stripe.CardError, _:
            return redirect(reverse('user:pricing'))
    else:
        return render(request, "userprofile/pricing.html", {"profile": profile})


@csrf_exempt
def web_hook(request):
    event_json = json.loads(request.body)
    if event_json["type"] == "invoice.created":
        if event_json["data"]["object"]["lines"]["data"][0]["type"] == "subscription":
            try:
                profile = UserProfile.objects.get(customer=event_json["data"]["object"]["customer"])
                profile.points_current += float(plan_points[int(profile.plan)])
                profile.save()
            except UserProfile.DoesNotExist as _:
                pass
    if event_json["type"] == "invoiceitem.created":
        amount = event_json["data"]["object"]["amount"]
        try:
            profile = UserProfile.objects.get(customer=event_json["data"]["object"]["customer"])
            if amount < 0:
                points = plan_points[profile.prev_plan]
                perc_amount = amount/plan_costs[profile.prev_plan]
                profile.points_current += round(perc_amount*points)
            elif amount > 0:
                points = plan_points[profile.plan]
                perc_amount = amount/plan_costs[profile.plan]
                profile.points_current += round(perc_amount*points)
            profile.save()
        except UserProfile.DoesNotExist as _:
            pass

    return HttpResponse({}, content_type="application/json")


def change_pic(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    if request.method == "POST":
        file_content = ImageFile(request.FILES['pic'])
        profile = request.user.user_profile.get()
        profile.picture.save(str(request.user.first_name) + ".png", file_content)
        return redirect(reverse('user:index'))
    messages.error(request, "Couldn't Change Avatar Try Again")
    return redirect(reverse('user:index'))
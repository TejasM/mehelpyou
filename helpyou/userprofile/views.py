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
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import facebook
import gdata.contacts.service
from gdata.gauth import OAuth2Token
from mailer import send_html_mail
import oauth2
import requests
from social_auth.db.django_models import UserSocialAuth
import stripe
import twitter

from forms import SignupForm, UserProfileForm
from helpyou import settings
from helpyou.request.forms import FilterRequestsForm
from helpyou.request.models import Request
from helpyou.notifications.models import Notification
from helpyou.notifications.views import new_notifications
from helpyou.response.models import Response
from helpyou.userprofile.models import Invitees, Feed, Message
from models import UserProfile


def sync_up_user(user, social_users):
    for social_user in social_users:
        if social_user.provider == 'linkedin':
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist as _:
                profile = UserProfile.objects.create(user=user)
            if profile.last_updated < timezone.now() - timedelta(weeks=2) or profile.never_updated:
                if profile.industry == '' and "industry" in social_user.extra_data and social_user.extra_data[
                    "industry"]:
                    profile.industry = social_user.extra_data["industry"]
                if profile.educations == '' and "educations" in social_user.extra_data and social_user.extra_data[
                    "educations"] \
                        and len(social_user.extra_data["educations"]) <= 10000:
                    for education in social_user.extra_data["educations"].values():
                        if 'school-name' in education and education['school-name']:
                            profile.educations += education['school-name']
                        if 'field-of-study' in education and education['field-of-study']:
                            profile.educations += ": " + education['field-of-study'] + "\n"
                if profile.interests == '' and "interests" in social_user.extra_data and social_user.extra_data[
                    "interests"] \
                        and len(social_user.extra_data["interests"]) <= 10000:
                    profile.interests = social_user.extra_data["interests"]
                if profile.skills == '' and "skills" in social_user.extra_data and social_user.extra_data[
                    "skills"] and len(
                        social_user.extra_data["skills"]) <= 10000:
                    for skill in social_user.extra_data["skills"]['skill']:
                        profile.skills += skill["skill"]["name"] + ", "
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
                    token = social_user.tokens["oauth_token"]
                    url = "https://api.linkedin.com/v1/people/~/picture-urls::(original)"
                    try:
                        consumer = oauth2.Consumer(
                            key=settings.LINKEDIN_CONSUMER_KEY,
                            secret=settings.LINKEDIN_CONSUMER_SECRET)
                        token = oauth2.Token(
                            key=token,
                            secret=social_user.tokens["oauth_token_secret"])
                        client = oauth2.Client(consumer, token)
                        response, content = client.request(url)
                        if '<picture-url key="original">' in content:
                            content = content.split('<picture-url key="original">')[1].split('</picture-url>')[0]
                            file_content = ContentFile(urllib.urlopen(content).read())
                            profile.picture.save(str(profile.user.first_name) + ".png", file_content)
                    except Exception as _:
                        pass
                profile.last_updated = timezone.now()
                profile.never_updated = False
                profile.save()

        elif social_user.provider == 'facebook':
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist as _:
                profile = UserProfile.objects.create(user=user)
            if profile.last_updated < timezone.now() - timedelta(weeks=2) or profile.never_updated:
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
                profile.last_updated = timezone.now()
                profile.never_updated = False
                profile.save()

        elif social_user.provider == 'twitter':
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist as _:
                profile = UserProfile.objects.create(user=user)
            if profile.last_updated < timezone.now() - timedelta(weeks=2) or profile.never_updated:
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
                        file_content = ContentFile(
                            urllib.urlopen(social_user.extra_data["profile_picture"].replace('_normal', '')).read())
                        if str(profile.picture) != 'default-avatar.png':
                            profile.picture.delete()
                        profile.picture.save(str(profile.user.first_name) + ".png", file_content)
                profile.last_updated = timezone.now()
                profile.never_updated = False
                profile.save()

        elif social_user.provider == 'google-oauth2':
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist as _:
                profile = UserProfile.objects.create(user=user)
            if profile.last_updated < timezone.now() - timedelta(weeks=2) or profile.never_updated:
                google = gdata.contacts.service.ContactsService(source='')

                token = OAuth2Token(
                    '1042521437798-1q2c0dpckdkisrcnalb9pjm0maufri8e.apps.googleusercontent.com',
                    '0kwSY54y-SVqaKmAPr3Acjh7', 'https://www.google.com/m8/feeds', '',
                    access_token=social_user.tokens['access_token'])
                google.SetAuthSubToken(social_user.tokens['access_token'])
                contact_feed = google.GetContactsFeed(
                    uri='https://www.google.com/m8/feeds/contacts/' + profile.user.email + '/full')
                for i, entry in enumerate(contact_feed.entry):
                    if entry.title.text:
                        try:
                            connect = UserSocialAuth.objects.get(uid=entry.email[0].address)
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
                                Invitees.objects.get(uid=entry.email[0].address, user_from=profile)
                            except Invitees.DoesNotExist as _:
                                Invitees.objects.create(uid=entry.email[0].address, user_from=profile,
                                                        name=entry.title.text, social_media='google')


def MassPay(email, amt):
    params = {
        'USER': 'AAZAR_ZAFAR_api1.YAHOO.CA',
        'PWD': 'P53YYXBTHLZXM8B3',
        'SIGNATURE': 'AiPC9BjkCyDFQXbSkoZcgqH3hpacAydRo07t2A9JC6OnDlufilUck9Q-Z',
        'VERSION': '2.3',
        'EMAILSUBJECT': 'You have money',
        'METHOD': "MassPay",
        'RECEIVERTYPE': "EmailAddress",
        'L_AMT0': amt,
        'CURRENCYCODE': 'CAD',
        'L_EMAIL0': email,
    }
    params_string = urllib.urlencode(params)
    response = urllib.urlopen("https://api-3t.paypal.com/nvp", params_string).read()
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


@csrf_exempt
def contact_us(request):
    if request.method == "POST":
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        send_html_mail('Contact Us message from ' + email, "", '<h3>' + subject + '</h3><p>' + message + '</p>',
                       'info@mehelpyou.com', ['info@mehelpyou.com'], fail_silently=True)
    return HttpResponse({}, content_type='application/json')


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
    return render(request, "base.html", {'form': form})


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
                # send_html_mail('Your MeHelpYou Password Recovery', "",
                #           settings.ForgotEmail(user.username, 'www.mehelpyou.com/users/reset_password/' + str(user.id)),
                #   'info@mehelpyou.com', [email], fail_silently=True)
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
            notificiation = Notification.objects.filter(user=user, to_user=request.user, message="IN").count()
            if notificiation > 0:
                invitation_from = True
            notificiation = Notification.objects.filter(user=request.user, to_user=user, message="IN").count()
            if notificiation > 0:
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
        except twitter.TwitterError:
            pass
        return redirect(reverse('user:feed'))
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
                messages.success(request, 'Incorrect username')
                return redirect('/')
            messages.success(request, 'Incorrect password')
            return redirect('/')
    return redirect('/')


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
            profile.company = profile_created.company
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
def feed(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=request.user)
    data = request.GET.copy()
    feeds = Feed.objects.filter(users__id=request.user.id).order_by('-time')
    requests_inner = FilterRequestsForm(data, queryset=Request.objects.all())
    commission_start = request.GET.getlist('quick_commission_start')
    category = request.GET.getlist('quick_category')
    city = request.GET.getlist('quick_city')
    if feeds.count() < 20 and not commission_start and not category and not city:
        feeds = Feed.objects.filter(request__in=requests_inner).order_by('-time')[:20]
    else:
        feeds = feeds.filter(request__in=requests_inner)
    if commission_start:
        commission_start = commission_start[0]
        feeds = feeds.filter(request__commission_start__gte=float(commission_start))
    if category:
        feeds = feeds.filter(request__category__iregex=r'(' + '|'.join(category) + ')')
    if city:
        feeds = feeds.filter(request__city__iregex=r'(' + '|'.join(city) + ')')
    if 'page' in data:
        del data['page']
    form = requests_inner.form
    paginator = Paginator(feeds, 5)
    page = request.GET.get('page')
    try:
        feeds = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        feeds = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        feeds = paginator.page(paginator.num_pages)
    return render(request, "feed/feed.html",
                  {'profile': profile, 'feeds': feeds, 'form': form})


@login_required
@new_notifications
def invite_connection(request):
    if request.method == "POST":
        messages.success(request, 'Invitation Sent to ' + User.objects.get(pk=request.POST["id"]).username)
        Notification.objects.create(user_id=request.POST["id"], message="IN", to_user=request.user)
    return redirect(reverse('user:index'))


@login_required
def send_message(request):
    if request.method == "POST":
        try:
            Message.objects.create(message_to_user=User.objects.get(pk=request.POST['to_id']),
                                   message_from_user=request.user,
                                   subject=request.POST['subject'],
                                   message=request.POST['message'],
                                   request=Request.objects.get(pk=request.POST['request_id']))
            messages.success(request, 'Message Successfully Sent')
        except KeyError:
            messages.error(request, 'Something went wrong in sending message, please try again')
        return redirect(request.POST['next'])
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


@login_required
@new_notifications
def collect(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        email = request.POST.get("email", '')
        if email == '':
            messages.error(request, "Incorrect Paypal address!")
            return redirect(reverse('user:balance'))
        response = MassPay(request.POST["email"], float(request.POST["amount"]))
        if str(response["ACK"]) != "Failure":
            profile.points_current -= float(request.POST["amount"])
            profile.paypal_email = email
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
        google_invites = []
        for user_id in user_ids:
            invitee = Invitees.objects.get(pk=user_id)
            if invitee.social_media == 'linkedin-oauth2':
                linkedin_invites.append(invitee)
            elif invitee.social_media == 'facebook':
                facebook_invites.append(invitee)
            elif invitee.social_media == 'twitter':
                twitter_invites.append(invitee)
            elif invitee.social_media == 'google':
                google_invites.append(invitee)
        message = request.POST.get('message',
                                   'I am inviting you to use MeHelpYou, to make and ' +
                                   'get referrals and money! www.mehelpyou.com')
        successes = []
        for social_user in social_users:
            if social_user.provider == 'linkedin':
                chunks = [linkedin_invites[x:x + 50] for x in xrange(0, len(linkedin_invites), 50)]
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
                                                                        }, )
                    consumer = oauth2.Consumer(
                        key=settings.LINKEDIN_CONSUMER_KEY,
                        secret=settings.LINKEDIN_CONSUMER_SECRET)
                    token = oauth2.Token(
                        key=social_user.tokens["oauth_token"],
                        secret=social_user.tokens["oauth_token_secret"])
                    client = oauth2.Client(consumer, token)
                    url = "https://api.linkedin.com/v1/people/~/mailbox"
                    response, content = client.request(url, method="POST", body=json.dumps(send_message),
                                                       headers={'x-li-format': 'json',
                                                                'Content-Type': 'application/json'})
                    if response.status == 201 or response.status == 200:
                        for invitee in chunk:
                            successes.append(invitee.name)
                            invitee.delete()
            elif social_user.provider == 'facebook':
                if social_user.extra_data["access_token"] and facebook_invites:
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
            elif social_user.provider == 'google-auth2':
                htmly = get_template('email/gmail_invitee.html')
                for invitee in google_invites:
                    send_html_mail('Request Has A Response', "",
                                   htmly.render({'from': request.user.first_name + ' ' + request.user.last_name,
                                                 'to': invitee.name}),
                                   'info@mehelpyou.com', [invitee.uid], fail_silently=True)
                    successes.append(invitee.name)
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
            if profile.customer:
                customer = stripe.Customer.retrieve(id=profile.customer)
                customer.card = token
                customer.save()
                stripe.Charge.create(
                    amount=int(int(request.POST['points']) * 100),  # amount in cents, again
                    currency="cad",
                    customer=profile.customer,
                    description=request.user.username,
                )
            else:
                customer = stripe.Customer.create(card=token, email=request.user.email)
                charge = stripe.Charge.create(
                    amount=int(int(request.POST['points']) * 100),  # amount in cents, again
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
                        messages.success(request, "Subscription Updated.")
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
                messages.success(request, "Subscription Updated.")
            profile.save()
            return redirect(reverse('user:index'))
        except stripe.CardError, _:
            return redirect(reverse('user:pricing'))
    else:
        return render(request, "userprofile/pricing.html", {"profile": profile})


def downgrade(request, plan):
    if not request.user.is_authenticated():
        return render(request, "userprofile/pricing.html")
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=request.user)
    if request.method == "GET":
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Create the charge on Stripe's servers - this will charge the user's card
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.customer:
                c = stripe.Customer.retrieve(str(profile.customer))
                if int(plan) == 0:
                    c.cancel_subscription()
                else:
                    c.update_subscription(plan=profile.plan_names[int(plan)].lower().replace(" ", "_"),
                                          prorate="False")
                profile.prev_plan = profile.plan
                profile.plan = int(plan)
                messages.success(request, "Subscription Updated.")
                profile.save()
            return redirect(reverse('user:pricing'))
        except stripe.CardError, _:
            return redirect(reverse('user:pricing'))
    else:
        return render(request, "userprofile/pricing.html", {"profile": profile})


@login_required()
def balance(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist as _:
        profile = UserProfile.objects.create(user=request.user)

    transaction_list = Response.objects.filter(user=request.user).filter(~Q(commission_time=None)).order_by(
        'commission_time')
    last7_balance = transaction_list.filter(commission_time__gte=timezone.now() - timedelta(days=7))
    last30_balance = transaction_list.filter(commission_time__gte=timezone.now() - timedelta(days=30))
    if last7_balance:
        last7_balance = reduce(lambda x, y: x + y, map(lambda x: x.commission_paid, last7_balance))
    else:
        last7_balance = 0
    if last30_balance:
        last30_balance = reduce(lambda x, y: x + y, map(lambda x: x.commission_paid, last30_balance))
    else:
        last30_balance = 0
    if transaction_list:
        total_earned = reduce(lambda x, y: x + y, map(lambda x: x.commission_paid, transaction_list))
    else:
        total_earned = 0

    paid_list = Response.objects.filter(request__user=request.user).filter(~Q(commission_time=None)).order_by(
        'commission_time')
    last7_paid = paid_list.filter(commission_time__gte=timezone.now() - timedelta(days=7))
    last30_paid = paid_list.filter(commission_time__gte=timezone.now() - timedelta(days=30))
    if last7_paid:
        last7_paid = reduce(lambda x, y: x + y, map(lambda x: x.commission_paid, last7_paid))
    else:
        last7_paid = 0
    if last30_paid:
        last30_paid = reduce(lambda x, y: x + y, map(lambda x: x.commission_paid, last30_paid))
    else:
        last30_paid = 0
    if paid_list:
        total_paid = reduce(lambda x, y: x + y, map(lambda x: x.commission_paid, paid_list))
    else:
        total_paid = 0

    return render(request, "userprofile/balance.html", {"profile": profile, "transaction_list": transaction_list,
                                                        "seven": last7_balance, "thirty": last30_balance,
                                                        "total_earned": total_earned,
                                                        "paid_list": paid_list, "last7_paid": last7_paid,
                                                        "last30_paid": last30_paid, "total_paid": total_paid})


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
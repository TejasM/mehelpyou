# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
import stripe
from forms import CreateResponseForm
from helpyou import settings

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
    from mailer import send_html_mail
else:
    from django.core.mail import send_mail
from helpyou.notifications.models import Notification
from helpyou.notifications.views import new_notifications
from helpyou.request.models import Request
from helpyou.userprofile.models import UserProfile, Feed, Message
from models import Response


@login_required
@new_notifications
def create(request, request_id):
    if request.method == "POST":
        form = CreateResponseForm(request.POST)
        if form.is_valid():
            response_created = form.save(commit=False)
            response_created.user = request.user
            response_created.request = Request.objects.get(pk=request_id)
            response_created.save()
            Notification.objects.create(user=response_created.request.user, request=response_created.request,
                                        response=response_created, message="RR")
            """
            feed = Feed.objects.create(description="<a href='/request/view/" + str(
                response_created.request.id) + "'>" + response_created.request.company +
                                                   " has received a referral for " + response_created.request.title + "request </a>",
                                       request=response_created.request,
                                       avatar_link='avatars/' + request.user.user_profile.get().picture.name)
            feed.users.add(*list(User.objects.all()))
            feed.save()
            """
            send_html_mail('Request Has A Response', "",
                           settings.ResponseToRequest(response_created.request.user.username,
                                                      response_created.request.title,
                                                      'www.mehelpyou.com/request/view/' + str(
                                                          response_created.request.id),
                                                      response_created.request.response_set.count()),
                           'info@mehelpyou.com', [response_created.request.user.email], fail_silently=True)
            return redirect(reverse('response:view_responses_to', args=(request_id,)))
    else:
        form = CreateResponseForm()
    request_your = Request.objects.get(pk=request_id)
    return render(request, "response/create.html", {'form': form, 'request_your': request_your})


@login_required
@new_notifications
def view_your(request):
    responses = Response.objects.filter(user=request.user)
    return render(request, "response/view_your_responses.html", {'responses': responses})


@login_required
@new_notifications
def view_responses_id(request, id_request):
    if request.method == "POST":
        return redirect(reverse('response:view_responses_to', args=(id_request,)))
    else:
        request_your = Request.objects.get(pk=id_request)
        responses = Response.objects.filter(user=request.user, request=request_your)
        if responses.count() == 0:
            return redirect(reverse('response:create', args=(id_request,)))
        return render(request, "response/view_your_response.html",
                      {'request_your': request_your, 'responses': responses})


@login_required
@new_notifications
def view_id(request, id_response):
    return redirect(reverse('response:edit', args=(id_response,)))


@login_required
@new_notifications
def edit_id(request, id_response):
    try:
        response_your = Response.objects.get(user=request.user, id=id_response)
    except Response.DoesNotExist as _:
        return redirect(reverse('user:index'))
    if request.method == "POST":
        form = CreateResponseForm(request.POST)
        if response_your.commission_paid == 0:
            if form.is_valid():
                response_created = form.save(commit=False)
                response_your = Response.objects.get(user=request.user, id=id_response)
                response_your.preview = response_your.preview
                response_your.response = response_created.response
                response_your.save()
                send_html_mail('Request Has A Response', "",
                               settings.ResponseToRequest(response_your.request.user.username,
                                                          response_your.request.title,
                                                          'www.mehelpyou.com/request/view/' + str(
                                                              response_your.request.id),
                                                          list(
                                                              response_your.request.response_set.all().order_by(
                                                                  'create_time').values_list('id',
                                                                                             flat=True)).index(
                                                              response_your.id) + 1),
                               'info@mehelpyou.com', [response_your.request.user.email], fail_silently=True)
                return redirect(reverse('response:view_your'))
    else:
        form = CreateResponseForm(instance=response_your)
    message_list = Message.objects.filter(request=response_your.request).filter(
        Q(message_to_user=request.user) | Q(message_from_user=request.user))
    return render(request, "response/edit.html", {'form': form, 'id_response': id_response, 'response': response_your,
                                                  'request_your': response_your.request, 'message_list': message_list})


@login_required
@new_notifications
def offer_commission(request, id_response):
    try:
        response_your = Response.objects.get(id=id_response)
        if response_your.request.user != request.user:
            return redirect(reverse('user:index'))
        if request.method == "POST":
            token = request.POST['stripeToken']
            stripe.api_key = settings.STRIPE_SECRET_KEY
            # Create the charge on Stripe's servers - this will charge the user's card
            try:
                profile = UserProfile.objects.get(user=response_your.user)
                your_profile = UserProfile.objects.get(user=request.user)
                if your_profile.customer:
                    customer = stripe.Customer.retrieve(id=your_profile.customer)
                    customer.card = token
                    customer.save()
                    stripe.Charge.create(
                        amount=int(float(request.POST['money_form']) * 100),
                        currency="cad",
                        customer=your_profile.customer,
                        description=request.user.username,
                    )
                else:
                    customer = stripe.Customer.create(card=token, email=request.user.email)
                    charge = stripe.Charge.create(
                        amount=int(float(request.POST['money_form']) * 100),
                        currency="cad",
                        customer=customer.id,
                        description=request.user.username,
                    )
                    your_profile.customer = charge["customer"]
                profile.commission_earned += float(request.POST['money_form'])
                profile.save()
                your_profile.commission_paid += float(request.POST['money_form'])
                your_profile.save()
                response_your.commission_paid += float(request.POST['money_form'])
                response_your.commission_time = timezone.now()
                response_your.save()
                feed = Feed.objects.create(description="<a href='/users/" + str(
                    response_your.user.id) + "'>" + response_your.user.first_name + " " + response_your.user.last_name +
                                                       " gave a lead and earned " + str(
                    int(request.POST['money_form'])) + " referral fee." + "</a>",
                                           request=response_your.request,
                                           avatar_link=response_your.user.user_profile.get().picture.name)
                # feed.users.add(*list(User.objects.all()))
                send_html_mail('Your Response has received commission', "",
                               settings.ResponseBought(response_your.user.username,
                                                       response_your.request.user.username, response_your.request.title,
                                                       'www.mehelpyou.com/request/view/' + str(
                                                           response_your.request.id),
                                                       float(request.POST['money_form'])),
                               'info@mehelpyou.com', [response_your.user.email], fail_silently=True)
                feed.save()
                return redirect(reverse('request:view_your_id', args=(response_your.request.id,)))
            except stripe.CardError, _:
                return redirect(reverse('request:view_your_id', args=(response_your.request.id,)))
        else:
            return redirect(reverse('request:view_your_id', args=(response_your.request.id,)))
    except Response.DoesNotExist as _:
        return redirect(reverse('user:index'))


@login_required
@new_notifications
def relevant(request, id_response):
    try:
        response_your = Response.objects.get(id=id_response)
        if response_your.request.user != request.user:
            return redirect(reverse('user:index'))
        response_your.relevant = True
        response_your.save()
        """
        feed = Feed.objects.create(description="<a href='/request/" + str(
            response_your.request.id) + "'>" + response_your.user.first_name + " " + response_your.user.last_name +
                                               " has submitted a referral that was relevant" + "</a>",
                                   request=response_your.request,
                                   avatar_link='avatars/' + response_your.user.user_profile.get().picture.name)
        feed.users.add(*list(User.objects.all()))
        feed.save()
        """
        return redirect(reverse('request:view_your_id', args=(response_your.request.id,)))
    except Response.DoesNotExist as _:
        return redirect(reverse('user:index'))


@login_required
@new_notifications
def not_relevant(request, id_response):
    try:
        response_your = Response.objects.get(id=id_response)
        if response_your.request.user != request.user:
            return redirect(reverse('user:index'))
        response_your.relevant = False
        response_your.save()
        return redirect(reverse('request:view_your_id', args=(response_your.request.id,)))
    except Response.DoesNotExist as _:
        return redirect(reverse('user:index'))
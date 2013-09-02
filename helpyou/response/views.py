# Create your views here.
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.utils.datastructures import MultiValueDictKeyError
import stripe
from forms import CreateResponseForm
from helpyou import settings
from helpyou.notifications.models import Notification
from helpyou.notifications.views import new_notifications
from helpyou.request.models import Request
from helpyou.userprofile.models import UserProfile
from models import Response


@new_notifications
def create(request, request_id):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    if request.method == "POST":
        form = CreateResponseForm(request.POST)
        if form.is_valid():
            response_created = form.save(commit=False)
            response_created.user = request.user
            response_created.request = Request.objects.get(pk=request_id)
            response_created.save()
            Notification.objects.create(user=response_created.request.user, request=response_created.request,
                                        response=response_created, message="RR")
            return redirect(reverse('response:view_your'))
    else:
        form = CreateResponseForm()
    request_your = Request.objects.get(pk=request_id)
    return render(request, "response/create.html", {'form': form, 'request_your': request_your})


@new_notifications
def view_your(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    responses = Response.objects.filter(user=request.user)
    return render(request, "response/view_your_responses.html", {'responses': responses})


@new_notifications
def view_id(request, id_response):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    response_your = Response.objects.get(id=id_response)
    if not request.user == response_your.buyer and not request.user == response_your.user and response_your.price != 0:
        return redirect(reverse('request:view_your_id', kwargs={"id_request": response_your.request.id}))
    return render(request, "response/view_your_response.html", {'response': response_your})


@new_notifications
def edit_id(request, id_response):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    if request.method == "POST":
        form = CreateResponseForm(request.POST)
        if form.is_valid():
            response_created = form.save(commit=False)
            response_your = Response.objects.get(user=request.user, id=id_response)
            response_your.anon = response_created.anon
            response_your.available_till = response_created.available_till
            response_your.response = response_created.response
            response_your.price = response_created.price
            if response_your.counter_offer:
                response_your.counter_offer = None
                response_your.counter_comments = None
                Notification.objects.create(user=response_your.request.user, response=response_your,
                                            request=response_your.request,
                                            message="CN")

            response_your.save()
            return redirect(reverse('response:view_your'))
    else:
        try:
            response_your = Response.objects.get(user=request.user, id=id_response)
        except Response.DoesNotExist as _:
            return redirect(reverse('user:index'))
        form = CreateResponseForm(instance=response_your)
    return render(request, "response/edit.html", {'form': form, 'id_response': id_response})


@new_notifications
def buy(request, id_response):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    try:
        response_your = Response.objects.get(id=id_response)
        profile = UserProfile.objects.get(user=response_your.user)
        your_profile = UserProfile.objects.get(user=request.user)
        if response_your.price <= profile.points_current:
            response_your.buyer = request.user
            profile.points_current += response_your.price
            your_profile.points_current -= response_your.price
            profile.lifetime_points_earned += response_your.price
            profile.save()
            response_your.save()
            request_answered = Request.objects.get(pk=response_your.request_id)
            Notification.objects.create(user=response_your.user, request=request_answered,
                                        response=response_your, message='RA')
            return redirect(reverse('response:view_your_id', args=(response_your.id,)))
        else:
            messages.error(request, "Not enough points, you can buy more points on profile page")
            return redirect(reverse('request:view_your_id', args=(response_your.request_id,)))
    except Response.DoesNotExist as _:
        return redirect(reverse('user:index'))


def negotiate(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    try:
        id_response = request.POST['id']
        response_your = Response.objects.get(id=id_response)
        response_your.counter_offer = request.POST['offer']
        response_your.counter_comments = request.POST['comments']
        response_your.save()
        Notification.objects.create(user=response_your.user, response=response_your, request=response_your.request,
                                    message="RN")
        return redirect(reverse('request:view_your_id', args=(response_your.request_id,)))
    except Response.DoesNotExist as _:
        return redirect(reverse('user:index'))
    except MultiValueDictKeyError as _:
        return redirect(reverse('user:index'))
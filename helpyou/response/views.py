# Create your views here.
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
import stripe
from forms import CreateResponseForm
from helpyou import settings
from helpyou.notifications.models import Notification
from helpyou.notifications.views import new_notifications
from helpyou.request.models import Request
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
        token = request.POST['stripeToken']
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Create the charge on Stripe's servers - this will charge the user's card
        try:
            charge = stripe.Charge.create(
                amount=int(response_your.price * 100), # amount in cents, again
                currency="cad",
                card=token,
                description=request.user.username,
            )
            response_your.buyer = request.user
            response_your.save()
            request_answered = Request.objects.get(pk=response_your.request_id)
            Notification.objects.create(user=response_your.user, request=request_answered,
                                        response=response_your, message='RA')
            return redirect(reverse('response:view_your_id', kwargs={"id_response": response_your.id}))
            #TODO: save customer credit card
            # token = request.POST['stripeToken']
            # # Create a Customer
            # customer = stripe.Customer.create(
            #     card=token,
            #     description="payinguser@example.com"
            # )
            # # Charge the Customer instead of the card
            # stripe.Charge.create(
            #     amount=1000, # in cents
            #     currency="usd",
            #     customer=customer.id
            # )
        except stripe.CardError, e:
            return redirect(reverse('user:view_your_id', id_response))

    except Response.DoesNotExist as _:
        return redirect(reverse('user:index'))


@new_notifications
def collect(request, id_response):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    try:
        response_your = Response.objects.get(id=id_response)
        token = request.POST['stripeToken']
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Create the charge on Stripe's servers - this will charge the user's card
        try:
            charge = stripe.Charge.create(
                amount=int(response_your.price * 100), # amount in cents, again
                currency="cad",
                card=token,
                description=request.user.username,
            )
            response_your.collected = True
            response_your.save()
            return redirect(reverse('response:view_your_id', kwargs={"id_response": response_your.id}))
            #TODO: save customer credit card
            # token = request.POST['stripeToken']
            # # Create a Customer
            # customer = stripe.Customer.create(
            #     card=token,
            #     description="payinguser@example.com"
            # )
            # # Charge the Customer instead of the card
            # stripe.Charge.create(
            #     amount=1000, # in cents
            #     currency="usd",
            #     customer=customer.id
            # )
        except stripe.CardError, e:
            return redirect(reverse('user:view_your_id', id_response))

    except Response.DoesNotExist as _:
        return redirect(reverse('user:index'))
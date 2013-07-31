# Create your views here.
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from forms import CreateResponseForm
from helpyou.request.models import Request
from models import Response


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
            return redirect(reverse('response:view_your'))
    else:
        form = CreateResponseForm()
    request_your = Request.objects.get(pk=request_id)
    return render(request, "response/create.html", {'form': form, 'request_your': request_your})


def view_your(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    responses = Response.objects.filter(user=request.user)
    return render(request, "response/view_your_responses.html", {'responses': responses})


def view_id(request, id_response):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    response_your = Response.objects.get(id=id_response)
    return render(request, "response/view_your_response.html", {'response': response_your})


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
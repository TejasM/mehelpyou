# Create your views here.
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect
from forms import CreateRequestForm
from helpyou.notifications.views import new_notifications
from helpyou.request.forms import FilterRequestsForm
from helpyou.response.models import Response
from helpyou.userprofile.models import features, UserProfile
from models import Request


@new_notifications
def create(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    if request.method == "POST":
        form = CreateRequestForm(request.POST)
        if form.is_valid():
            request_created = form.save(commit=False)
            request_created.user = request.user
            request_created.save()
            return redirect(reverse('request:view_your'))
    else:
        form = CreateRequestForm()
    return render(request, "request/create.html",
                  {'form': form})


@new_notifications
def view_your(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    requests = Request.objects.filter(user=request.user)
    return render(request, "request/view_your_requests.html", {'requests': requests})


@new_notifications
def view_id(request, id_request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    request_your = Request.objects.get(id=id_request)
    responses = Response.objects.filter(request=request_your)
    have_responsed = len(Response.objects.filter(request=request_your, user=request.user)) == 1
    return render(request, "request/view_your_request.html", {'request_your': request_your, "responses": responses,
                                                              "have_responded": have_responsed})


@new_notifications
def edit_id(request, id_request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    if request.method == "POST":
        form = CreateRequestForm(request.POST)
        if form.is_valid():
            request_created = form.save(commit=False)
            request_your = Request.objects.get(user=request.user, id=id_request)
            request_your.title = request_created.title
            request_your.anon = request_created.anon
            request_your.due_by = request_created.due_by
            request_your.request = request_created.request
            request_your.reward = request_created.reward
            request_your.save()
            return redirect(reverse('request:view_your'))
    else:
        try:
            request_your = Request.objects.get(user=request.user, id=id_request)
        except Request.DoesNotExist as _:
            return redirect(reverse('user:index'))
        form = CreateRequestForm(instance=request_your)
    return render(request, "request/edit.html", {'form': form, 'id_request': id_request})


@new_notifications
def view_all(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    connections = request.user.connections.all()
    connections = map(lambda x: x.user, connections)
    requests = Request.objects.filter(~Q(user=request.user)).filter(~Q(user__in=connections)).order_by(
        'user__user_profile__plan')
    requests = [req for req in requests if req.user.user_profile.all()[0].is_feature_available("view_all")]
    data = request.GET.copy()
    if 'page' in data:
        del data['page']
    requests = FilterRequestsForm(data, queryset=requests)
    form = requests.form
    # paginator = Paginator(requests, 25) # Show 25 contacts per page
    # page = request.GET.get('page')
    # try:
    #     requests = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     requests = paginator.page(1)
    # except EmptyPage:
    #     # If page is out of range (e.g. 9999), deliver last page of results.
    #     requests = paginator.page(paginator.num_pages)
    return render(request, "request/view_all.html", {'requests': requests, 'form': form})


@new_notifications
def view_connections(request):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    connections = request.user.connections.all()
    connections = map(lambda x: x.user, connections)
    second_deg_connections = []
    for connection in connections:
        for second_connection in connection.user_profile.all()[0].connections.all():
            if second_connection.user != request.user:
                if second_connection.user_profile.get().is_feature_available("2nd_connections"):
                    second_deg_connections.append(second_connection)

    connections += second_deg_connections
    requests = Request.objects.filter(user__in=connections, anon=False).order_by('user__user_profile__plan')
    data = request.GET.copy()
    if 'page' in data:
        del data['page']
    requests = FilterRequestsForm(data, queryset=requests)
    form = requests.form
    # paginator = Paginator(requests, 25) # Show 25 contacts per page
    # page = request.GET.get('page')
    # try:
    #     requests = paginator.page(page)
    # except PageNotAnInteger:
    #     # If page is not an integer, deliver first page.
    #     requests = paginator.page(1)
    # except EmptyPage:
    #     # If page is out of range (e.g. 9999), deliver last page of results.
    #     requests = paginator.page(paginator.num_pages)
    return render(request, "request/view_all.html", {'requests': requests, 'form': form})
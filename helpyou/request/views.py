# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from helpyou import settings
from helpyou.userprofile.models import Feed

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
    from mailer import send_html_mail
else:
    from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect
from forms import CreateRequestForm
from helpyou.notifications.views import new_notifications
from helpyou.request.forms import FilterRequestsForm
from helpyou.response.models import Response
from models import Request


@login_required
@new_notifications
def create(request):
    if request.method == "POST":
        form = CreateRequestForm(request.POST, request.FILES)
        if form.is_valid():
            request_created = form.save(commit=False)
            request_created.user = request.user
            if str(request_created.company) == '':
                request_created.company = request.user.first_name + " " + request.user.last_name
            request_created.save()
            feed = Feed.objects.create(description="<a href='/request/view/" + str(
                request_created.id) + "'>" + request.user.user_profile.get().company +
                " has put up a referral request and is offering up to $" + str(request_created.commission_end) + "</a>",
                avatar_link=request.user.user_profile.get().picture.url)
            emails = []
            feed.users.add(*list(User.objects.all()))
            for connection in request.user.user_profile.get().connections.all():
                #feed.users.add(connection.user)
                if connection.user.email:
                    emails.append(connection.user.email)
            send_html_mail('Request Has A Response', "",
                           'Your Connection ' + request.user.username + ' has Request for ' + request_created.title +
                           '.<br>Please help your friend out.<br>Link: www.mehelpyou.com/request/view/' + str(
                               request_created.id),
                           'info@mehelpyou.com', emails, fail_silently=True)
            feed.save()
            return redirect(reverse('request:view_your'))
    else:
        form = CreateRequestForm()
    return render(request, "request/create.html",
                  {'form': form})


@login_required
@new_notifications
def view_your(request):
    requests = Request.objects.filter(user=request.user)
    return render(request, "request/view_your_requests.html", {'requests': requests})


@login_required
@new_notifications
def view_id(request, id_request):
    request_your = Request.objects.get(id=id_request)
    if request_your.user != request.user:
        return redirect(reverse('response:create', args=(request_your.id,)))
    responses = Response.objects.filter(request=request_your)
    have_responsed = len(Response.objects.filter(request=request_your, user=request.user)) == 1
    return render(request, "request/view_your_request.html",
                  {'request_your': request_your, "responses": responses, "have_responded": have_responsed})


@login_required
@new_notifications
def edit_id(request, id_request):
    if request.method == "POST":
        form = CreateRequestForm(request.POST, request.FILES)
        if form.is_valid():
            request_created = form.save(commit=False)
            request_your = Request.objects.get(user=request.user, id=id_request)
            request_your.title = request_created.title
            request_your.start_time = request_created.start_time
            request_your.due_by = request_created.due_by
            request_your.request = request_created.request
            request_your.commission_start = request_created.commission_start
            request_your.commission_end = request_created.commission_end
            request_your.document = request_created.document
            request_your.save()
            return redirect(reverse('request:view_your'))
    else:
        try:
            request_your = Request.objects.get(user=request.user, id=id_request)
        except Request.DoesNotExist as _:
            return redirect(reverse('user:index'))
        form = CreateRequestForm(instance=request_your)
    return render(request, "request/edit.html", {'form': form, 'id_request': id_request})


@login_required
@new_notifications
def view_all(request):
    connections = request.user.connections.all()
    connections = map(lambda x: x.user, connections)
    requests = Request.objects.filter(~Q(user=request.user)).filter(~Q(user__in=connections))
    # requests = requests.filter(Q(user__user_profile__plan__gte=2))
    requests = requests.order_by(
        '-user__user_profile__plan', '-start_time')
    data = request.GET.copy()
    if 'page' in data:
        del data['page']
    requests = FilterRequestsForm(data, queryset=requests)
    form = requests.form
    paginator = Paginator(requests, 10) # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        requests = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        requests = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        requests = paginator.page(paginator.num_pages)
    return render(request, "request/view_all.html", {'requests': requests, 'form': form})


@login_required
@new_notifications
def view_connections(request):
    connections = request.user.connections.all()
    connections = map(lambda x: x.user, connections)
    second_deg_connections = []
    for connection in connections:
        for second_connection in connection.user_profile.all()[0].connections.all():
            if second_connection.user != request.user:
                if second_connection.user_profile.get().is_feature_available("2nd_connections"):
                    second_deg_connections.append(second_connection)

    connections += second_deg_connections
    requests = Request.objects.filter(user__in=connections).order_by('-user__user_profile__plan', '-start_time')
    data = request.GET.copy()
    if 'page' in data:
        del data['page']
    requests = FilterRequestsForm(data, queryset=requests)
    form = requests.form
    paginator = Paginator(requests, 10) # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        requests = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        requests = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        requests = paginator.page(paginator.num_pages)
    return render(request, "request/view_all.html",
                  {'requests': requests, 'form': form, 'title': "Connection's Requests"})
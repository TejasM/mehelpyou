# Create your views here.
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from helpyou import settings
from helpyou.userprofile.models import Feed, Message

if "mailer" in settings.INSTALLED_APPS:
    from mailer import send_mail
    # from mailer import send_html_mail
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
        if request.POST.getlist('groups'):
            request.POST.getlist('groups').remove('-1')
        form = CreateRequestForm(request.POST, request.FILES, id=request.user.id)
        if form.is_valid():
            request_created = form.save(commit=False)
            request_created.user = request.user
            request_created.save()
            form.save_m2m()
            messages.info(request,
                          'Thank you. Your request has been created and will be reviewed. If approved, it will be posted within 24 hours.')
            """
            name = request.user.first_name + " " + request.user.last_name
            if request_created.anonymous:
                name = "Anonymous"
            if str(request_created.company) == '':
                description = "<a href='/request/view/" + str(
                    request_created.id) + "'>" + name + " is offering a referral fee up to $" + \
                              str(request_created.commission_end) + ", for a " + 'lead request entitled "' + str(
                    request_created.title) + '"</a>'
            else:
                description = "<a href='/request/view/" + str(
                    request_created.id) + "'>" + name + " (" + str(request_created.company) + \
                              ") is offering a referral fee up to $" + str(
                    request_created.commission_end) + ", for a " + \
                              'lead request entitled "' + str(request_created.title) + '"</a>'

            feed = Feed.objects.create(description=description,
                                       avatar_link=request.user.user_profile.get().picture.url,
                                       request=request_created)
            emails = []
            if request_created.groups.count() > 0:
                list_all = []
                for users in list(request_created.groups.all().values_list('users')):
                    list_all.extend(users)
                for users in list(list(request_created.groups.all().values_list('administrators'))):
                    list_all.extend(users)
                list_all = filter(lambda x: x is not None, list_all)
                feed.users.add(*list_all)
            else:
                feed.users.add(*list(User.objects.all()))
            for connection in request.user.user_profile.get().connections.all():
                #feed.users.add(connection.user)
                if connection.email:
                    emails.append(connection.email)
            #send_html_mail('Request Has A Response', "",
            #               'Your Connection ' + request.user.username + ' has Request for ' + request_created.title +
            #               '.<br>Please help your friend out.<br>Link: www.mehelpyou.com/request/view/' + str(
            #                   request_created.id),
            #               'info@mehelpyou.com', emails, fail_silently=True)
            feed.save()
            """
            return redirect(reverse('request:view_your'))
    else:
        form = CreateRequestForm(id=request.user.id)
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
    not_viewed = responses.filter(viewed=False)
    for res in not_viewed:
        res.viewed = True
        res.save()
    messages_for_request = Message.objects.filter(request=request_your)
    users_id_list = set(messages_for_request.values_list('message_from_user__id', flat=True))
    users_id_list = list(map(lambda x: int(x), users_id_list))
    first_id = None
    if users_id_list:
        first_id = users_id_list[0]
    users_first_list = set(messages_for_request.values_list('message_from_user__first_name', flat=True))
    users_last_list = set(messages_for_request.values_list('message_from_user__last_name', flat=True))
    return render(request, "request/view_your_request.html",
                  {'request_your': request_your, "responses": responses.order_by('-create_time'),
                   "have_responded": False,
                   'messages_list': messages_for_request, 'users_id_list': users_id_list,
                   'users_first_list': users_first_list, 'users_last_list': users_last_list, 'first_id': first_id})


@login_required
@new_notifications
def view_sample(request):
    return render(request, "request/view_sample.html")


@login_required
@new_notifications
def edit_id(request, id_request):
    if request.method == "POST":
        form = CreateRequestForm(request.POST, request.FILES, id=request.user.id)
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
            for f in request_your.feed_set.all():
                f.update_self()
            request_your.save()
            return redirect(reverse('request:view_your'))
    else:
        try:
            request_your = Request.objects.get(user=request.user, id=id_request)
        except Request.DoesNotExist as _:
            return redirect(reverse('user:index'))
        form = CreateRequestForm(instance=request_your, id=request.user.id)
    return render(request, "request/edit.html", {'form': form, 'id_request': id_request})


@login_required
@new_notifications
def view_all(request):
    connections = request.user.connections.all()
    connections = map(lambda x: x.user, connections)
    requests = Request.objects.filter(~Q(user=request.user)).filter(~Q(user__in=connections)).filter(approved=True)
    # requests = requests.filter(Q(user__user_profile__plan__gte=2))
    requests = requests.order_by(
        '-user__user_profile__plan', '-start_time')
    data = request.GET.copy()
    if 'page' in data:
        del data['page']
    requests = FilterRequestsForm(data, queryset=requests)
    form = requests.form
    paginator = Paginator(requests, 10)  # Show 25 contacts per page
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
    requests = Request.objects.filter(user__in=connections).filter(~Q(user=request.user)).filter(
        approved=True).order_by(
        '-user__user_profile__plan', '-start_time')
    data = request.GET.copy()
    if 'page' in data:
        del data['page']
    requests = FilterRequestsForm(data, queryset=requests)
    form = requests.form
    paginator = Paginator(requests, 10)  # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        requests = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        requests = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        requests = paginator.page(paginator.num_pages)
    return render(request, "request/view_connections.html",
                  {'requests': requests, 'form': form})
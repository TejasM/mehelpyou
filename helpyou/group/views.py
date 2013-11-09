from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import render, redirect
from helpyou.group.forms import CreateGroupForm
from helpyou.group.models import Group
from helpyou.notifications.views import new_notifications


@login_required
@new_notifications
def index(request, group_id):
    group = Group.objects.get(pk=group_id)
    users = group.users.all()
    administrators = group.administrators.all()
    if request.user in users:
        return render(request, "group/index.html",
                      {'group': group, 'in_group': True, 'administrator': request.user in administrators,
                       'administrators': administrators, 'users': users})
    elif request.user in administrators:
        contacts = request.user.connections.filter(~Q(user__in=users)).filter(~Q(user__in=administrators))
        return render(request, "group/index.html",
                      {'group': group, 'in_group': True, 'administrator': True,
                       'administrators': administrators, 'users': users, 'contacts': contacts,
                       'pending': group.pending_requests.all()})
    else:
        return render(request, "group/index.html",
                      {'group': group, 'in_group': False, 'administrator': False,
                       'administrators': administrators, 'users': users, 'pending': group.pending_requests.all()})


@login_required
@new_notifications
def create(request):
    if request.method == "POST":
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            group.administrators.add(request.user)
            group.save()
            return redirect(reverse('group:index', args=(group.id,)))
    else:
        form = CreateGroupForm()
    return render(request, "group/create.html",
                  {'form': form})


@login_required
@new_notifications
def edit(request, group_id):
    group = Group.objects.get(pk=group_id)
    if request.user in group.administrators.all():
        if request.method == "POST":
            form = CreateGroupForm(request.POST)
            if form.is_valid():
                new_group = form.save(commit=False)
                if new_group.logo:
                    group.logo = new_group.logo
                group.description = new_group.description
                group.title = new_group.title
                group.save()
                return redirect(reverse('group:index', args=(group_id,)))
        else:
            form = CreateGroupForm(instance=group)
        return render(request, "group/edit.html",
                      {'form': form, 'group': group_id})
    return redirect(reverse('group:index', args=(group_id,)))


@login_required
@new_notifications
def add_to_group(request, group_id):
    group = Group.objects.get(pk=group_id)
    if request.user in group.administrators.all():
        if request.method == "POST" and "add[]" in request.POST:
            users = User.objects.filter(pk__in=request.POST.getlist('add[]'))
            for user in users:
                if user not in group.administrators.all():
                    group.users.add(user)
                    if user in group.pending_requests.all():
                        group.pending_requests.remove(user)
            group.save()
            messages.success(request, 'Added ' + str([str(x.username) for x in users]) + ' to group')
    return redirect(reverse('group:index', args=(group_id,)))


@login_required
@new_notifications
def remove_from_group(request, group_id):
    group = Group.objects.get(pk=group_id)
    if request.user in group.administrators.all():
        if request.method == "POST" and "add[]" in request.POST:
            users = User.objects.filter(pk__in=request.POST.getlist('add[]'))
            for user in users:
                group.users.remove(user)
            group.save()
            messages.success(request, 'Removed ' + str([str(x.username) for x in users]) + ' to group')
    return redirect(reverse('group:index', args=(group_id,)))


@login_required
@new_notifications
def move_to_administrators(request, group_id):
    group = Group.objects.get(pk=group_id)
    if request.user in group.administrators.all():
        if request.method == "POST" and "add[]" in request.POST:
            users = User.objects.filter(pk__in=request.POST.getlist('add[]'))
            if len(users) + len(group.administrators.all()) > 2:
                messages.success(request, 'There is a limit of 2 administrators per group')
            else:
                for user in users:
                    if user in group.users.all():
                        group.users.remove(user)
                        group.administrators.add(user)
                messages.success(request, 'Added ' + str([str(x.username) for x in users]) + ' to administrators')
                group.save()
    return redirect(reverse('group:index', args=(group_id,)))


@login_required
@new_notifications
def request_invitation(request, group_id):
    group = Group.objects.get(pk=group_id)
    if request.user not in group.administrators.all() or request.user not in group.users.all():
        if group.private:
            group.pending_requests.add(request.user)
        else:
            group.users.add(request.user)
    return redirect(reverse('group:index', args=(group_id,)))


@login_required
@new_notifications
def list_your(request):
    groups = Group.objects.filter(Q(users=request.user) | Q(administrators=request.user)).distinct()
    return render(request, "group/list.html",
                  {'groups': groups})

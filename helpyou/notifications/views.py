# Create your views here.
from functools import wraps
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from helpyou.notifications.models import Notification


def new_notifications(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        # if request.user.is_authenticated():
        #     new_notification = getNotifications(request, False)
        #     request.session['notifications'] = new_notification
        return view(request, *args, **kwargs)

    # return the wrapped function, replacing the original view
    return inner


def getNotifications(request, viewed):
    user = request.user
    if user.is_authenticated():
        return Notification.objects.filter(user=user, viewed=viewed)
    return []


@new_notifications
def notifications(request):
    new_notifications = getNotifications(request, False)
    context = {'notifications': new_notifications, 'old_notifications': getNotifications(request, True)}
    return render(request, 'notifications/notifications.html', context)


@new_notifications
def view_notification(request, id_notification):
    if not request.user.is_authenticated():
        return redirect(reverse('user:login'))
    notification = Notification.objects.get(pk=id_notification)
    if not notification.viewed:
        notification.viewed = True
        notification.save()
    if notification.request and notification.response:
        if notification.request.user == request.user:
            return redirect(reverse('request:view_your_id', args=(notification.request.id,)))
        else:
            return redirect(reverse('response:view_your_id', args=(notification.response.id,)))
    else:
        return redirect(reverse('user:user', args=(notification.to_user.id,)))
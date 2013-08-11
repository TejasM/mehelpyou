# Create your views here.
from functools import wraps
from django.shortcuts import render
from helpyou.notifications.models import Notification


def new_notifications(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated():
            new_notification = getNotifications(request, False)
            request.session['notifications'] = new_notification
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
    for new_notification in new_notifications:
        new_notification.viewed = True
        new_notification.save()
    context = {'notifications': new_notifications, 'old_notifications': getNotifications(request, True)}
    return render(request, 'notifications/notifications.html', context)

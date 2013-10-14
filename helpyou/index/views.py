from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from helpyou.index.forms import FeedbackForm


def contact(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        form.save()
        messages.success(request, "Thank you for your feedback")
        return redirect(reverse('user:index'))
    else:
        if request.user.is_authenticated():
            form = FeedbackForm(initial={'email': request.user.email, 'name': request.user.username})
        else:
            form = FeedbackForm()
    return render(request, "index/contact.html", {"form": form})
from django.db.models import Q
from helpyou.request.models import Request
from helpyou.userprofile.forms import SignupForm
from helpyou.userprofile.models import UserProfile

__author__ = 'tmehta'


def feature_context_processor(request):
    if request.user.is_authenticated():
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist as _:
            profile = UserProfile.objects.create(user=request.user)
        return {'features': profile.features(), 'invitees': profile.invitees_set.all().order_by('name'),
                'categories': Request.CATEGORY_CHOICES}
    else:
        return {'form': SignupForm()}
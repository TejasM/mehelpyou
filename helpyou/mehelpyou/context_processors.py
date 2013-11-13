from django.db.models import Q
from helpyou.group.models import Group
from helpyou.userprofile.models import UserProfile

__author__ = 'tmehta'


def feature_context_processor(request):
    if request.user.is_authenticated():
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist as _:
            profile = UserProfile.objects.create(user=request.user)
        groups = Group.objects.filter(Q(users=request.user) | Q(administrators=request.user)).distinct()
        return {'features': profile.features(), 'invitees': profile.invitees_set.all().order_by('name'),
                'groups': groups}
    return {}
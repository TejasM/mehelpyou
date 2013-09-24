from helpyou.userprofile.models import UserProfile

__author__ = 'tmehta'


def feature_context_processor(request):
    if request.user.is_authenticated():
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist as _:
            profile = UserProfile.objects.create(user=request.user)
        return {'features': profile.features()}
    return {}
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.ForeignKey(User)
    interests = models.CharField(max_length=1000)
    skills = models.CharField(max_length=1000)


class UserPic(models.Model):
    user = models.ForeignKey(User, related_name='user_info')
    image = models.ImageField(default='None', upload_to=user)

    def get_uid(self):
        return self.user.id

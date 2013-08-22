from django.contrib.auth.models import User
from django.core.files.images import get_image_dimensions
from django.forms import Textarea
from models import UserProfile, UserPic

__author__ = 'tmehta'
from django import forms


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['interests', 'skills', 'city', 'industry', 'educations']
        widgets = {
            'interests': Textarea(attrs={'rows': 20, 'cols': 80, 'placeholder': 'Interests'}),
            'skills': Textarea(attrs={'rows': 20, 'cols': 80, 'placeholder': 'Skills'}),
            'educations': Textarea(attrs={'rows': 20, 'cols': 80, 'placeholder': 'Skills'}),
        }


class UserField(forms.CharField):
    def clean(self, value):
        super(UserField, self).clean(value)
        try:
            User.objects.get(username=value)
            raise forms.ValidationError("Someone is already using this username. Please pick an other.")
        except User.DoesNotExist:
            return value


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
                                 label="First Name")
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
                                label="Last Name")
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email', 'type': 'email'}), label="Email")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
                                label="Repeat your password")

    def clean_email(self):
        if self.data['email'] != self.data['email2']:
            raise forms.ValidationError('Emails are not the same')
        return self.data['email']

    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password']

    def clean(self, *args, **kwargs):
        self.clean_email()
        self.clean_password()
        return super(SignupForm, self).clean(*args, **kwargs)


class UserPicForm(forms.ModelForm):
    class Meta:
        model = UserPic
        fields = ['image']

    def clean_avatar(self):
        avatar = self.cleaned_data['image']

        try:
            w, h = get_image_dimensions(avatar)

            #validate dimensions
            max_width = max_height = 100
            if w != max_width or h != max_height:
                raise forms.ValidationError(u'Please use an image that is %s x %s pixels.' % (max_width, max_height))

            #validate content type
            main, sub = avatar.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                raise forms.ValidationError(u'Please use a JPEG, GIF or PNG image.')

            #validate file size
            if len(avatar) > (20 * 1024):
                raise forms.ValidationError(u'Avatar file size may not exceed 20k.')

        except AttributeError:
            pass

        return avatar

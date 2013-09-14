from django.contrib.auth.models import User
from django.core.files.images import get_image_dimensions
from django.forms import Textarea
from models import UserProfile

__author__ = 'tmehta'
from django import forms


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False

    class Meta:
        model = UserProfile
        fields = ['interests', 'skills', 'city', 'industry', 'educations']
        widgets = {
            'interests': Textarea(attrs={'rows': 20, 'cols': 80, 'placeholder': 'Interests'}),
            'skills': Textarea(attrs={'rows': 20, 'cols': 80, 'placeholder': 'Skills'}),
            'educations': Textarea(attrs={'rows': 20, 'cols': 80, 'placeholder': 'Educations'}),
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

    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password']

    def clean(self, *args, **kwargs):
        self.clean_password()
        return super(SignupForm, self).clean(*args, **kwargs)
from django.forms import Textarea
from helpyou.index.models import Feedback

__author__ = 'tmehta'
from django import forms


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'comments']
        widgets = {
            'comments': Textarea(attrs={'rows': 20, 'cols': 80, 'placeholder': 'Feedback'}),
        }

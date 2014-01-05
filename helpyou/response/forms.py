from decimal import Decimal
from django.forms import ModelForm, Textarea, DateTimeInput
from django.forms.widgets import TextInput
from models import Response
from re import sub

__author__ = 'tmehta'


class CreateResponseForm(ModelForm):
    class Meta:
        model = Response
        fields = ['preview', 'response']
        widgets = {
            'preview': TextInput(),
            'response': Textarea(),
        }
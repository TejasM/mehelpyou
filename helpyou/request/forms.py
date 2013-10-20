from decimal import Decimal
from django.db import models
from django.forms import ModelForm, Textarea, DateTimeInput
from django.forms.widgets import TextInput
from models import Request
from re import sub
import django_filters

__author__ = 'tmehta'


class CreateRequestForm(ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'category', 'anon', 'request', 'due_by', 'reward']
        widgets = {
            'request': Textarea(attrs={'rows': 100, 'cols': 80}),
            'due_by': DateTimeInput(),
            'reward': TextInput(attrs={'type': 'hidden'}),
        }

    def clean_reward(self):
        data = float(Decimal(sub(r'[^\d.]', '', self.data['reward'])))
        return data

    def clean(self):
        self.cleaned_data['reward'] = self.clean_reward()
        if self.errors.get('reward', '') != '':
            del self.errors['reward']
        super(CreateRequestForm, self).clean()
        return self.cleaned_data


class FilterRequestsForm(django_filters.FilterSet):
    reward = django_filters.NumberFilter(lookup_type='gt')

    class Meta:
        model = Request
        fields = ['category', 'reward']

    def __init__(self, *args, **kwargs):
        super(FilterRequestsForm, self).__init__(*args, **kwargs)
        self.form.fields['category'].empty_label = "All Categories"
        self.form.fields['reward'].label = "Rewards Greater or Equal To"
        self.filters['category'].extra.update(
            {'empty_label': 'All Categories'})
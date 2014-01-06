from decimal import Decimal
from re import sub

from django.forms import ModelForm, Textarea, DateTimeInput
import django_filters

from models import Request


__author__ = 'tmehta'


class CreateRequestForm(ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'category', 'company', 'request', 'city', 'start_time', 'due_by', 'commission_start', 'commission_end',
                  'document']
        widgets = {
            'request': Textarea(),
            'start_time': DateTimeInput(attrs={'class': 'date-class'}),
            'due_by': DateTimeInput(attrs={'class': 'date-class'}),
        }

    def clean_commission_start(self):
        data = float(Decimal(sub(r'[^\d.]', '', self.data['commission_start'])))
        return data

    def clean_commission_end(self):
        data = float(Decimal(sub(r'[^\d.]', '', self.data['commission_end'])))
        return data

    def clean(self):
        self.cleaned_data['commission_start'] = self.clean_commission_start()
        if self.errors.get('commission_start', '') != '':
            del self.errors['commission_start']
        self.cleaned_data['commission_end'] = self.clean_commission_end()
        if self.errors.get('commission_end', '') != '':
            del self.errors['commission_end']
        super(CreateRequestForm, self).clean()
        return self.cleaned_data


class FilterRequestsForm(django_filters.FilterSet):
    class Meta:
        model = Request
        fields = ['category']

    def __init__(self, *args, **kwargs):
        super(FilterRequestsForm, self).__init__(*args, **kwargs)
        self.form.fields['category'].empty_label = "All Categories"
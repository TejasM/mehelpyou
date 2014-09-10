from decimal import Decimal
from re import sub
from django.conf import settings
from django.db.models import Q

from django.forms import ModelForm, Textarea, DateTimeInput, DateInput
import django_filters

from models import Request
from helpyou.group.models import Group


__author__ = 'tmehta'


class CreateRequestForm(ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'category', 'company', 'request', 'city', 'start_time', 'due_by', 'commission_start',
                  'commission_end',
                  'document', 'groups', 'anonymous']
        widgets = {
            'request': Textarea(),
            'start_time': DateInput(attrs={'class': 'date-class'}),
            'due_by': DateInput(attrs={'class': 'date-class'}),
        }

    def __init__(self, *args, **kwargs):
        userid = kwargs.pop('id')
        super(CreateRequestForm, self).__init__(*args, **kwargs)
        self.fields["groups"].queryset = Group.objects.filter(
            Q(users__id=userid) | Q(administrators__id=userid))

    def clean_commission_start(self):
        try:
            data = float(Decimal(sub(r'[^\d.]', '', self.data['commission_start'])))
        except:
            data = 0
        return data

    def clean_commission_end(self):
        try:
            data = float(Decimal(sub(r'[^\d.]', '', self.data['commission_end'])))
        except:
            data = 0
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


CHOICES_FOR_PRIORITY_FILTER = [
    ('', 'Any'),
]
CHOICES_FOR_PRIORITY_FILTER.extend(list(Request.CATEGORY_CHOICES))


class FilterRequestsForm(django_filters.FilterSet):
    commission_start = django_filters.NumberFilter(lookup_type='gte')

    class Meta:
        model = Request
        fields = ['category', 'city', 'commission_start']

    def __init__(self, *args, **kwargs):
        super(FilterRequestsForm, self).__init__(*args, **kwargs)
        self.filters['category'].extra.update(
            {
                'choices': CHOICES_FOR_PRIORITY_FILTER
            })
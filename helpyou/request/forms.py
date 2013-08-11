from decimal import Decimal
from django.forms import ModelForm, Textarea, DateTimeInput
from django.forms.widgets import TextInput
from models import Request
from re import sub

__author__ = 'tmehta'


class CreateRequestForm(ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'anon', 'request', 'due_by', 'reward', 'max_reward']
        widgets = {
            'request': Textarea(attrs={'rows': 100, 'cols': 80}),
            'due_by': DateTimeInput(),
            'reward': TextInput(),
        }

    def clean_reward(self):
        data = float(Decimal(sub(r'[^\d.]', '', self.data['reward'])))
        return data

    def clean_max_reward(self):
        data = float(Decimal(sub(r'[^\d.]', '', self.data['max_reward'])))
        return data

    def clean(self):
        self.cleaned_data['reward'] = self.clean_reward()
        self.cleaned_data['max_reward'] = self.clean_max_reward()
        if self.errors.get('reward', '') != '':
            del self.errors['reward']
        if self.errors.get('max_reward', '') != '':
            del self.errors['max_reward']
        super(CreateRequestForm, self).clean()
        return self.cleaned_data

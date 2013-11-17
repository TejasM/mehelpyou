from decimal import Decimal
from django.forms import ModelForm, Textarea, DateTimeInput
from django.forms.widgets import TextInput
from models import Response
from re import sub

__author__ = 'tmehta'


class CreateResponseForm(ModelForm):
    class Meta:
        model = Response
        fields = ['preview', 'response', 'anon', 'price']
        widgets = {
            'preview': Textarea(attrs={'rows': 100, 'cols': 80}),
            'response': Textarea(attrs={'rows': 100, 'cols': 80}),
            'price': TextInput(),
        }

    def clean_price(self):
        data = float(Decimal(sub(r'[^\d.]', '', self.data['price'])))
        return data

    def clean(self):
        self.cleaned_data['price'] = self.clean_price()
        if self.errors.get('price', '') != '':
            del self.errors['price']
        super(CreateResponseForm, self).clean()
        return self.cleaned_data

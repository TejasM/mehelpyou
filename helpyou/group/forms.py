from django.forms import ModelForm, Textarea
from helpyou.group.models import Group


class CreateGroupForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateGroupForm, self).__init__(*args, **kwargs)

        self.fields['logo'].required = False

    class Meta:
        model = Group
        fields = ['title', 'description', 'private', 'logo']
        widgets = {
            'description': Textarea(attrs={'rows': 100, 'cols': 80}),
        }
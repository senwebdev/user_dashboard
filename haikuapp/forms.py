import datetime
import time

from django import forms
from django.contrib.auth.models import User
from haikuapp.models import TemplateFields, CardField


class UpdateCardForm(forms.Form):
    date = forms.CharField(required=True)
    hour = forms.CharField(required=False)
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)
    time_from = forms.TimeField(required=False)
    time_to = forms.TimeField(required=False)

    def __init__(self, *args, **kwargs):
        card_id = kwargs.pop('card_id', 0)

        super(UpdateCardForm, self).__init__(*args, **kwargs)
        fields = CardField.objects.filter(card=card_id).all()
        for field in fields:
            # generate extra fields in the number specified via extra_fields
            self.fields['field_id_{index}'.format(index=field.id)] = \
                forms.CharField(max_length=255)


class TemlpateFieldForm(forms.Form):
    images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    date = forms.CharField(required=True)
    hour = forms.CharField(required=False)
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)
    time_from = forms.TimeField(required=False)
    time_to = forms.TimeField(required=False)
    user_input = forms.CharField(widget=forms.Textarea, required=False) # added for json variable user_input
    

    def __init__(self, *args, **kwargs):
        template_id = kwargs.pop('template_id', 0)

        super(TemlpateFieldForm, self).__init__(*args, **kwargs)
        fields = TemplateFields.objects.filter(template=template_id).all()
        for field in fields:
            # generate extra fields in the number specified via extra_fields
            #self.fields['field_id_{index}'.format(index=field.id)] = \
            self.fields[field.variable] = \
                forms.CharField(max_length=255, required=False) # added required=False

    def clean(self):
        date_from = self.cleaned_data.get('date_from')
        date_to = self.cleaned_data.get('date_to')
        time_from = self.cleaned_data.get('time_from')
        time_to = self.cleaned_data.get('time_to')
        # user_input = self.cleaned_data.get('user_input') # added for json variable user_input

        if date_to:
            if date_to < datetime.date.today():
                raise forms.ValidationError('TO date can\'t be less than TODAY!')

            if date_to < date_from:
                raise forms.ValidationError('TO date can\'t be less than FROM!')

        if time_to:
            if time_to < time_from:
                raise forms.ValidationError('TO time can\'t be less than FROM!')
        return self.cleaned_data


class LoginForm(forms.Form):
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': True
            },
        )
    )

    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'required': True,
            }
        )
    )


class RegisterForm(forms.Form):
    class Meta:
        model = User

    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'required': True,
            }
        )
    )

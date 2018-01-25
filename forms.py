import django.forms as forms
from django.db import models
from django.forms import ModelForm, Textarea, TextInput, Select
from .models import CallToClient, Visitation, Bidding, CallFromCard
from ancrm.models import ObjectMeeting
from client.models import Clients, ClientPhone
from functools import partial

DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=DateInput())
    end_date = forms.DateField(widget=DateInput())


class AddCallForm(ModelForm):

    class Meta:
        model = CallToClient
        fields = ('content', )


class CallFromCardForm(ModelForm):

    class Meta:
        model = CallFromCard
        fields = ('content', )


class VisitationForm(ModelForm):
    date_v = forms.DateField(input_formats='%Y-%m-%d', label='Дата посещения')
    time = forms.TimeField(input_formats='%H:%M', label='Время посещения')

    class Meta:
        model = Visitation
        fields = (
            'date_v',
            'time',
            'content',
            'date_answer',
            'price_from_client',
         )
        widgets = {
            'date_v': TextInput(attrs={'id': 'datepicker'}),
            'time': TextInput(attrs={'id': 'timepicker'}),
        }


class RejectionForm(ModelForm):

    class Meta:
        model = Visitation
        fields = ('date', 'obj', 'client', 'content')


class BiddingForm(ModelForm):

    class Meta:
        model = Bidding
        fields = ('manager', 'buyer', 'price_usd_o', 'price_usd_b', 'content')


class NewClientForm(models.Model):
    first_name = forms.CharField(label='Имя', required=False)
    surname = forms.CharField(label='Фамилия', required=False)
    comment = forms.CharField(label='Комментарий', required=False, widget=forms.Textarea)
    phone = forms.CharField(label='Телефон', required=False)


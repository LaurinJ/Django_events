from django import forms

from .models import Event, EventRun


class EventForm(forms.ModelForm):
    gallery = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Event
        exclude = ['host', 'slug']

class EventRunForm(forms.ModelForm):
    date = forms.DateField(input_formats=["%d.%m.%Y"], 
        widget=forms.DateInput(format = '%d.%m.%Y'))

    class Meta:
        model = EventRun
        exclude = ['event']


class EventFilterForm(forms.Form):
    date_from = forms.DateField(label="From", initial=None,
                                widget=forms.SelectDateWidget, required=False)

    date_to = forms.DateField(label="To", initial=None,
                              widget=forms.SelectDateWidget, required=False, )

    guests = forms.IntegerField(required=False, min_value=1)


class EventSearchFilterForm(EventFilterForm):
    q = forms.CharField(required=False, max_length=1000, initial='',
                        widget=forms.HiddenInput())
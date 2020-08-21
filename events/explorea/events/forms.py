from django.forms import ModelForm
from .models import EventRun, Event

class EventForm(ModelForm):

    class Meta:
        model = Event
        exclude = ['host']

class EditEventForm(ModelForm):

    class Meta:
        model = Event
        fields = ['name',
                  'description',
                  'location',
                  'category']

class EventRunForm(ModelForm):

    class Meta:
        model = EventRun
        exclude = ['event']
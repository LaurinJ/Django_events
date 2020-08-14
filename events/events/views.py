from django.shortcuts import render
from django.http import HttpResponse
from .models import Event, EventRun

def index(request):
    return render(request, 'events/index.html')

def event_detail(request, id):
    event = Event.objects.get(pk=id)
    event_run = EventRun.objects.filter(event_id=id)
    if event:
        return render(request, 'events/event_detail.html', {'event':event, 'event_run':event_run})
    return HttpResponse('Neexistujci udalost')

def event_listing(request):
    events = Event.objects.all()
    return render(request, 'events/event_listning.html', {'events':events})
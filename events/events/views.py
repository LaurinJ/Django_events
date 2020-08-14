from django.shortcuts import render
from django.http import HttpResponse
from .models import Event, EventRun

def index(request):
    return render(request, 'events/index.html')

def events(request, name):
    events = {'swiming':'456 Euro',
              'programing':'686 Euro',
              'sleeping':'6466 Euro',
              'chill':'4526 Euro',}
    if name in events:
        return HttpResponse(events[name])
    return HttpResponse('Neexistujci udalost')

def event_listing(request):
    events = Event.objects.all()
    return render(request, 'events/event_listning.html', {'events':events})
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Event, EventRun
from .forms import EventRunForm, EventForm, EditEventForm

def index(request):
    return render(request, 'events/index.html')

def event_detail(request, id):
    event = Event.objects.get(pk=id)
    event_run = event.eventrun_set.all()
    if event:
        return render(request, 'events/event_detail.html', {'event':event, 'event_run':event_run})
    return HttpResponse('Neexistujci udalost')

def event_listing(request):
    events = Event.objects.all()
    return render(request, 'events/event_listning.html', {'events':events})

def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.host = request.user
            event.save()
            return redirect('event_listing')
    form = EventForm()
    return render(request, 'events/event_add.html', {'form':form})

def edit_event(request, pk):
    event = Event.objects.get(pk=pk)
    if request.method == 'POST':
        form = EditEventForm(request.POST, instance=event)
        if form.is_valid():
            event.save()
            return redirect('event_listing')
    form = EditEventForm(instance=event)
    return render(request, 'events/event_edit.html', {'form':form})

def create_event_run(request, pk):
    event = Event.objects.get(pk=pk)
    if request.method == 'POST':
        form = EventRunForm(request.POST)
        if form.is_valid():
            event_run = form.save(commit=False)
            event_run.event_id = event.pk
            event_run.save()
            return redirect('event_listing')
    form = EventRunForm()
    return render(request, 'events/event_run_add.html', {'form':form})

def edit_event_run(request, pk):
    event_run = EventRun.objects.get(pk=pk)
    if request.method == 'POST':
        form = EventRunForm(request.POST, instance=event_run)
        if form.is_valid():
            form.save()
            return redirect('event_listing')
    form = EventRunForm(instance=event_run)
    return render(request, 'events/event_run_add.html', {'form': form})
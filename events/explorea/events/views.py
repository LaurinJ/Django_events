from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Event, EventRun
from .forms import EventForm, EventRunForm


def index(request):

    return render(request, 'events/index.html')

def event_listing(request):

    events = Event.objects.all()

    return render(request, 'events/event_listing.html', {'events': events})


def event_detail(request, pk):

    event = Event.objects.get(pk=pk)
    runs = event.eventrun_set.all().order_by('date', 'time')
    args = {'event': event, 'runs': runs}

    return render(request, 'events/event_detail.html', args)

@login_required
def create_event(request):

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.host = request.user
            event.save()

            return redirect('my_events')

    form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def my_events(request):

    events = Event.objects.filter(host_id=request.user.id)

    return render(request, 'events/my_events.html', {'events': events})

@login_required
def update_event(request, pk):
    event = Event.objects.get(pk=pk)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)

        if form.is_valid():
            event = form.save()
            return redirect('events:my_events')

    form = EventForm(instance=event)
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def delete_event(request, pk):

    Event.objects.get(pk=pk).delete()
    return redirect('my_events')

@login_required
def create_event_run(request, event_id):

    if request.method == 'POST':
        form = EventRunForm(request.POST)
        
        if form.is_valid():
            event_run = form.save(commit=False)
            event_run.event = Event.objects.get(pk=event_id)
            event_run.save()

            url = '/events/detail/{}'.format(event_id)
            return redirect(url)

    args = {'form': EventRunForm()}
    return render(request, 'events/create_event_run.html', args)

@login_required
def update_event_run(request, event_run_id):

    event_run = EventRun.objects.get(pk=event_run_id)

    if request.method == 'POST':
        form = EventRunForm(request.POST, instance=event_run)
        
        if form.is_valid():
            event_run = form.save()
            event_id = event_run.event.id
            url = '/events/detail/{}'.format(event_id)
            return redirect(url)

    args = {'form': EventRunForm(instance=event_run)}
    return render(request, 'events/update_event_run.html', args)

@login_required
def delete_event_run(request, event_run_id):

    run = EventRun.objects.get(pk=event_run_id)
    event_id = run.event.id
    run.delete()

    url = '/events/detail/{}'.format(event_id)
    return redirect(url)
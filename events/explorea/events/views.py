from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Event, EventRun, Album, Image
from .forms import EventForm, EventRunForm, EventFilterForm, MultipleFileForm


def index(request):

    return render(request, 'events/index.html')


def event_listing(request, category=None):
    events_run = EventRun.objects.all().filter_by_category(category).distinct()
    filter_form = EventFilterForm(request.GET or None)

    if request.GET and filter_form.is_valid():
        data = filter_form.cleaned_data
    else:
        data = {}

    events_run = events_run.filter_available(**data)
    paginator = Paginator(events_run, 10)
    page = request.GET.get('page')
    events = paginator.get_page(page)
    return render(request, 'events/event_listing.html',
                  {'events_run': events_run, 'filter_form': filter_form})

def event_search(request):
    query = request.GET.get('q')
    events_run = EventRun.objects.search(query)
    filter_form =  EventFilterForm()
    paginator = Paginator(events_run, 4)
    page = request.GET.get('page')
    events_run = paginator.get_page(page)
    return render(request, 'events/event_listing.html',
                  {'events_run': events_run, 'filter_form': filter_form})

def event_detail(request, slug):

    event = Event.objects.get(slug=slug)
    runs = event.eventrun_set.all().order_by('date', 'time')
    args = {'event': event, 'runs': runs}

    return render(request, 'events/event_detail.html', args)

@login_required
def create_event(request):
    event_form = EventForm(request.POST or None, request.FILES or None)
    file_form = MultipleFileForm(files=request.FILES or None)

    if request.method == 'POST':
        if event_form.is_valid() and file_form.is_valid():
            event = event_form.save(commit=False)
            event.host = request.user
            event.save()
            # save the individual images
            for file in request.FILES.getlist('gallery'):
                Image.objects.create(album=event.album, image=file, title=file.name)
            return redirect(event.get_absolute_url())

    return render(request, 'events/create_event.html', {'event_form': event_form, 'file_form':file_form})

@login_required
def my_events(request):

    events = Event.objects.filter(host_id=request.user.id)

    return render(request, 'events/my_events.html', {'events': events})

@login_required
def update_event(request, slug):
    event = Event.objects.get(slug=slug)
    event_form = EventForm(request.POST or None, request.FILES or None, instance=event)
    file_form = MultipleFileForm(files=request.FILES or None)
    if request.method == 'POST':
        if event_form.is_valid() and file_form.is_valid():
            event = event_form.save()
            for file in request.FILES.getlist('gallery'):
                Image.objects.create(album=event.album, image=file, title=file.name)
            return redirect(event.get_absolute_url())

    return render(request, 'events/create_event.html', {'event_form': event_form, 'file_form':file_form})

@login_required
def delete_event(request, slug):

    Event.objects.get(slug=slug).delete()
    return redirect('events:my_events')

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
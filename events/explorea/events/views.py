from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Event, EventRun, Image
from .forms import EventForm, EventRunForm, EventFilterForm, EventSearchFilterForm
from .mixins import GroupRequiredMixin, MessageActionMixin, GetFormMixin

from explorea.cart.forms import CartAddForm

def index(request):

    return render(request, 'events/index.html')

class EventListView(GetFormMixin, ListView):
    model = EventRun
    context_object_name = 'event_runs'
    form_class = EventFilterForm
    template_name = 'events/event_listing.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.form = self.get_form()
        if self.form.is_valid():
            return super().get(request, *args, **kwargs)
        else:
            self.object_list = []
            return self.form_invalid(self.form)

    def get_queryset(self):
        qs = self.model._default_manager.all().filter_by_category(self.kwargs['category'])
        return qs.filter_first_available(**self.form.cleaned_data)

    def get_context_data(self, **kwargs):
        contex = super().get_context_data()
        contex['filter_form'] = self.form
        return contex

class EventSearchView(GetFormMixin, ListView):
    model = EventRun
    form_class = EventSearchFilterForm
    template_name = 'events/event_listing.html'
    paginate_by = 4
    context_object_name = 'event_runs'

    def get(self, request, *args, **kwargs):
        self.form = self.get_form()
        if self.form.is_valid():
            self.query = self.form.cleaned_data.pop('q')
            return super().get(request, *args, **kwargs)
        else:
            self.object_list = []
            return self.form_invalid(self.form)

    def get_queryset(self):
        return self.model._default_manager.search(self.query).filter_first_available(**self.form.cleaned_data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.form
        return context

class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'
    template_name = 'events/event_detail.html'
    form_class = CartAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['runs'] = self.object.eventrun_set.all()
        context['cart_add_form'] = self.form_class()
        return context

class CreateEventView(GroupRequiredMixin, MessageActionMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/create_event.html'
    success_message = 'The event %(name)s has been created successfully'
    error_message = 'The event could not be created'
    groups_required = ['hosts']

    def form_valid(self, form):
        form.cleaned_data.pop('gallery')
        event = self.object = Event.objects.create(host=self.request.user, **form.cleaned_data)
        # save the individual images
        for file in self.request.FILES.getlist('gallery'):
            Image.objects.create(album=event.album, image=file, title=file.name)
        super().form_valid(form)
        return redirect(event.get_absolute_url())

class MyEventView(ListView):
    context_object_name = 'events'
    template_name = 'events/my_events.html'

    def get_queryset(self):
        return Event.objects.filter(host_id=self.request.user.id)

class UpdateEventView(UserPassesTestMixin, MessageActionMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/create_event.html'
    success_message = 'The event %(name)s has been updated successfully'
    error_message = 'The event %(name)s could not be updated'
    groups_required = ['hosts']
    permission_denied_message = "Too bad, you don't have access to these lands"

    def test_func(self):
        event = self.get_object()
        return self.request.user.id == event.host.id

    def handle_no_permission(self):
        raise PermissionDenied(self.get_permission_denied_message())

    def form_valid(self, form):
        event = form.save()

        for file in self.request.FILES.getlist('gallery'):
            Image.objects.create(album=event.album, image=file, title=file.name)
        super().form_valid(form)
        return redirect(event.get_absolute_url())

class DeleteEventView(UserPassesTestMixin, MessageActionMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('events:my_events')
    success_message = "The event %(name)s has been removed successfully"
    groups_required = ['hosts']
    permission_denied_message = "Too bad, you don't have access to these lands"

    def test_func(self):
        event = self.get_object()
        return self.request.user.id == event.host.id

    def handle_no_permission(self):
        raise PermissionDenied(self.get_permission_denied_message())

class CreateEventRunView(GroupRequiredMixin, CreateView):
    model = Event
    form_class = EventRunForm
    template_name = 'events/create_event_run.html'
    groups_required = ['hosts']

    def form_valid(self, form):
        event = Event.objects.get(slug=self.kwargs['slug'])
        self.object = EventRun.objects.create(event=event, **form.cleaned_data)
        messages.success(self.request, 'EventRun byl uspesne vytvo5en')
        return redirect(self.object.event.get_absolute_url())

class UpdateEventRunView(UserPassesTestMixin, UpdateView):
    model = EventRun
    form_class = EventRunForm
    template_name = 'events/update_event_run.html'
    groups_required = ['hosts']
    permission_denied_message = "Too bad, you don't have access to these lands"

    def test_func(self):
        event = self.get_object()
        return self.request.user.id == event.host.id

    def handle_no_permission(self):
        raise PermissionDenied(self.get_permission_denied_message())

    def get_success_url(self):
        return self.object.event.get_absolute_url()

class DeleteEventRunView(UserPassesTestMixin, DeleteView):
    model = EventRun
    groups_required = ['hosts']
    permission_denied_message = "Too bad, you don't have access to these lands"

    def test_func(self):
        event = self.get_object()
        return self.request.user.id == event.host.id

    def handle_no_permission(self):
        raise PermissionDenied(self.get_permission_denied_message())

    def get_success_url(self):
        return self.object.event.get_absolute_url()
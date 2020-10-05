from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, FormView, View
from django.views.generic.detail import SingleObjectMixin
from django.contrib import messages

from explorea.events.models import Event, EventRun
from .forms import CartAddForm


class CartDetailView(TemplateView):
    template_name = "cart/cart_detail.html"


class CartAddView(SingleObjectMixin, FormView):
    model = Event
    form_class =  CartAddForm
    template_name = 'events/event_detail.html'
    slug_url_kwarg = 'event_slug'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):

        self.request.cart.add(**form.cleaned_data)

        if form.cleaned_data['update']:
            messages.success(self.request, 'Cart has been updated')
            return redirect('cart:detail')
        else:
            messages.success(self.request, 'The run has been added to the cart')
            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        if form.cleaned_data['update']:
            messages.error(self.request, 'The cart could not be updated')
            return redirect('cart:detail')
        else:
            messages.error(self.request, 'The run could not be added into the cart')
            return HttpResponseRedirect(self.get_success_url())        
        

class CartRemoveView(View):

    def get(self, request, *args, **kwargs):
        self.request.cart.remove(self.kwargs['product_id'])
        return redirect('cart:detail')

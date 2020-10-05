from unittest import skip
from datetime import date, timedelta, time

from django.test import TestCase, TransactionTestCase
from django.urls import resolve, reverse
from django.contrib.auth import get_user_model

from explorea.events.models import Event, EventRun
from ..views import CartDetailView, CartAddView
from ..forms import CartAddForm

UserModel = get_user_model()


class CartDetailViewTest(TestCase):

    @classmethod
    def setUpClass(cls):
        # fix login
        super().setUpClass()
        cls.username = 'TEST'
        cls.password = 'password123'
        cls.user = UserModel.objects.create_user(username=cls.username, 
                                                 password=cls.password)
        # allow showing cart detail
        cls.event1 = Event.objects.create(host=cls.user, 
                                         name='Test Event1', 
                                         description='Test Event1 Description', 
                                         location='Test Event1 Location')
        cls.eventrun1 = EventRun.objects.create(event=cls.event1,
                                               date=date.today() + timedelta(days=2),
                                               time=time(hour=10, minute=30),
                                               seats_available=20,
                                               price=200)

        cls.event2 = Event.objects.create(host=cls.user, 
                 name='Test Event2', 
                 description='Test Event2 Description', 
                 location='Test Event2 Location')
        cls.eventrun2 = EventRun.objects.create(event=cls.event2,
           date=date.today() + timedelta(days=3),
           time=time(hour=11, minute=30),
           seats_available=20,
           price=200)

    def setUp(self):
        self.client.login(username=self.username, password=self.password)

    def test_cart_detail_url_resolves_to_cart_detail_view(self):
        page = resolve(reverse('cart:detail'))
        self.assertEqual(page.func.__name__, CartDetailView.__name__)

    def test_cart_detail_shows_no_items_when_empty(self):
        response = self.client.get(reverse('cart:detail'))
        self.assertIn(b'The cart is empty', response.content)

    def test_cart_detail_shows_items_when_cart_not_empty(self):

        payload = {
            'product_id': self.event1.id, 
            'quantity': 2, 
            'current_quantity': 0
        }
        self.client.post(
                reverse('cart:add', args=[self.event1.slug]), 
                payload
            )

        payload = {
            'product_id': self.event2.id, 
            'quantity': 3, 
            'current_quantity': 0
        }

        self.client.post(
                reverse('cart:add', args=[self.event2.slug]), 
                payload
            )

        response = self.client.get(reverse('cart:detail'))

        self.assertIn(self.event1.name.encode(), response.content)
        self.assertIn(self.event2.name.encode(), response.content)


class CartAddViewTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = 'TEST'
        cls.password = 'password123'
        cls.user = UserModel.objects.create_user(username=cls.username, 
                                                 password=cls.password)
        cls.event = Event.objects.create(host=cls.user, 
                                         name='Test Event', 
                                         description='Test Event Description', 
                                         location='Test Event Location')
        cls.eventrun = EventRun.objects.create(event=cls.event,
                                               date=date.today() + timedelta(days=2),
                                               time=time(hour=10, minute=30),
                                               seats_available=20,
                                               price=200)

    def setUp(self):
        self.view = CartAddView
        self.url = reverse('cart:add', args=[self.event.slug])
        self.client.login(username=self.username, password=self.password)

    def test_cart_detail_url_resolves_to_cart_detail_view(self):
        page = resolve(self.url)
        self.assertEqual(page.func.__name__, self.view.__name__)

    def test_cart_add_view_valid_form_data_redirects_to_corresponding_product_page_with_success(self):
        data = {
            'quantity': self.eventrun.seats_available, 
            'product_id': self.eventrun.id,
            'current_quantity': 0
        }
        response = self.client.post(self.url, 
                                   data=data, 
                                   follow=True)
        self.assertRedirects(response, self.event.get_absolute_url())

        msg = list(response.context.get('messages'))[0]
        self.assertEqual(msg.message, 'The run has been added to the cart')
        self.assertEqual(msg.tags, 'success')

    def test_cart_add_view_invalid_form_data_redirects_to_corresponding_product_page_with_error(self):
        data = {
            'quantity': self.eventrun.seats_available + 1, 
            'product_id': self.eventrun.id,
            'current_quantity': 0
        }
        response = self.client.post(self.url, 
                                   data=data, 
                                   follow=True)
        
        self.assertRedirects(response, self.event.get_absolute_url())

        msg = list(response.context.get('messages'))[0]
        self.assertEqual(msg.message, 'The run could not be added into the cart')
        self.assertEqual(msg.tags, 'error')
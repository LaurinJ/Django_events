from datetime import date, timedelta, time

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from ..forms import CartAddForm, PositiveIntegerField
from explorea.events.models import Event, EventRun


UserModel = get_user_model()

class PositiveIntegerFieldTest(TestCase):

    def test_validate_positive_integer(self):
        field = PositiveIntegerField()
        self.assertIsNone(field.validate(2))

    def test_validated_integer_less_than_one(self):
        field = PositiveIntegerField()
        with self.assertRaises(ValidationError):
            field.validate(-5)


class CartAddFormTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserModel.objects.create_user(username='TEST', password='password123')
        cls.event = Event.objects.create(host=cls.user, 
                                         name='Test Event', 
                                         description='Test Event Description', 
                                         location='Test Event Location')
        cls.eventrun = EventRun.objects.create(event=cls.event,
                                               date=date.today() + timedelta(days=2),
                                               time=time(hour=10, minute=30),
                                               seats_available=4,
                                               price=200)


    def test_form_valid_with_positive_int_quantity_and_existing_id(self):
        data = {
            'quantity': 1, 
            'product_id': 1, 
            'current_quantity': 0
        }

        form = CartAddForm(data=data)

        self.assertTrue(form.is_valid())

    def test_form_invalid_with_adding_less_than_one_quantity(self):
        data = {
            'quantity': 0, 
            'product_id': 1, 
            'current_quantity': 0
        }

        form = CartAddForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIsNotNone(form.errors.get('quantity'))
        self.assertIn('Only positive integer allowed', form.errors.get('quantity'))

    

    def test_form_rendered_invalid_for_non_existent_item_id(self):
        data = {
            'quantity': 2, 
            'product_id': -1,
            'current_quantity': 0,
        }

        form = CartAddForm(data=data)


        self.assertFalse(form.is_valid())
        self.assertIsNotNone(form.errors.get('product_id'))
        self.assertIn('Requested item does not exist', form.errors.get('product_id'))

    def test_invalid_if_number_of_items_added_greater_than_items_available(self):

        data = {
            'quantity': 20, 
            'product_id': 1, 
            'current_quantity': 0
        }
        
        form = CartAddForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIsNotNone(form.errors.get('quantity'))
        self.assertIn('Not enough items available', form.errors.get('quantity'))

    def test_form_invalid_with_updating_to_quantity_greater_than_avaialable(self):

        data = {
            'quantity': 10, 
            'product_id': 1, 
            'current_quantity': 0, 
            'update': True
        }

        form = CartAddForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIsNotNone(form.errors.get('quantity'))
        self.assertIn('Not enough items available', form.errors.get('quantity'))

    def test_form_invalid_with_updating_to_quantity_greater_than_avaialable_current_quantity_greater_zero(self):

        data = {
            'quantity': 10, 
            'product_id': 1, 
            'current_quantity': 5, 
            'update': True
        }

        form = CartAddForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIsNotNone(form.errors.get('quantity'))
        self.assertIn('Not enough items available', form.errors.get('quantity'))
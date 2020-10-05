from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings

from ..cart import Cart

class CartTest(TestCase):

    def setUp(self):
        self.session = SessionStore()
        self.cart = Cart(self.session)

    def test_create_cart(self):     
        self.assertTrue(hasattr(self.cart, 'session'))
        self.assertIsInstance(self.cart.session, SessionStore)
        self.assertTrue(hasattr(self.cart, 'cart'))
        self.assertIsInstance(self.cart.cart, dict)

    def test_new_cart_is_empty(self):
        self.assertTrue(self.cart.is_empty())

    def test_cart_add_item(self):
        product_id = 2
        quantity = 4

        self.cart.add(product_id=product_id, quantity=quantity)

        self.assertEqual(self.cart[product_id]['quantity'], quantity)

    def test_cart_add_adds_one_item_by_default(self):
        product_id = 2

        self.cart.add(product_id=product_id)

        self.assertEqual(self.cart[product_id]['quantity'], 1)
    
    def test_add_cart_updates_session(self):
        product_id = 2
        quantity = 1

        self.cart.add(product_id=product_id, quantity=quantity)

        self.assertEqual(self.session[settings.CART_SESSION_ID][str(product_id)],
                         self.cart[product_id])

    def test_cart_add_updates_to_correct_quantity_if_update_true(self):
        product_id = 2
        quantity = 1

        self.cart.add(product_id=product_id, quantity=quantity)
        self.cart.add(product_id=product_id, quantity=quantity, update=True)

        self.assertEqual(self.cart[product_id]['quantity'], 1)

    def test_cart_add_changes_quantity_if_update_false(self):
        product_id = 2
        quantity = 1

        self.cart.add(product_id=product_id, quantity=quantity)
        self.cart.add(product_id=product_id, quantity=quantity, update=False)

        self.assertEqual(self.cart[product_id]['quantity'], 2)

    def test_cart_removes_correct_item(self):
        product_id = 2
        quantity = 1

        self.cart.add(product_id=product_id, quantity=quantity)
        self.cart.remove(product_id)

        self.assertNotIn(product_id, self.cart)

    def test_cart_remove_handles_non_existent_id(self):
        product_id = 2
        quantity = 1

        self.cart.add(product_id=product_id, quantity=quantity)
        self.cart.remove(30)

        self.assertEqual(self.cart, {'2': {'quantity':1}})

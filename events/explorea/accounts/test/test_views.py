from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..views import ValidateUsernameView

UserModel = get_user_model()

class UserLoginMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = 'TEST'
        cls.password = 'password123'
        cls.user = UserModel.objects.create_user(username=cls.username,
                                                 password=cls.password)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)

class ValidateUsernameViewTest(UserLoginMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('accounts:validate_username')
    def test_returns_false_if_exists(self):
        data = {
            'username': self.username
        }
        response = self.client.post(self.url, data=data)
        expected_json = {
            'exists': True,
            'error_message': 'The username already exists'
        }
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_json)

    def test_returns_true_and_no_error_if_not_exist(self):
        data = {
            'username': 'NONEXIST'
        }
        response = self.client.post(self.url, data=data)
        expected_json = {
            'exists': False,
        }
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, expected_json)
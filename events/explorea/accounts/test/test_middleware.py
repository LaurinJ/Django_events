from unittest.mock import Mock
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.conf import settings

from explorea.events.views import EventListView, MyEventView
from ..middleware import LoginMiddleware

class LoginMiddlewareTest(TestCase):

    def get_request(self, url, is_authenticated):
        request_factory = RequestFactory()
        request = request_factory.get(url)
        request.user = Mock()
        request.user.is_authenticated = is_authenticated
        return request

    def setUp(self):
        self.middleware = LoginMiddleware(None)
        self.non_login_view = EventListView.as_view()
        self.login_required_view = MyEventView.as_view()
        self.login_required_url = reverse('events:my_events')
        self.non_login_url = reverse('events:events', args=['all'])

    def test_non_login_required_view_not_intercepted_for_anonymous_user(self):

        request = self.get_request(self.non_login_url, False)

        response = self.middleware.process_view(request, self.non_login_view, (), {})
        self.assertIsNone(response)

    def test_login_required_view_returns_login_redirect_for_anonymous_user(self):
        request = self.get_request(self.login_required_url, False)
        response = self.middleware.process_view(request, self.login_required_view, (), {})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, settings.LOGIN_URL)

    def test_non_login_required_view_not_intercepted_for_loggedin_user(self):
        request = self.get_request(self.non_login_url, True)
        response = self.middleware.process_view(request, self.non_login_view, (), {})
        self.assertIsNone(response)

    def test_login_required_view_not_intercepted_for_loggedin_user(self):
        request = self.get_request(self.login_required_url, True)
        result = self.middleware.process_view(request, self.login_required_view, (), {})
        self.assertIsNone(result)
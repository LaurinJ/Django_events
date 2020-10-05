from django.conf import settings
from django.shortcuts import redirect

class LoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        is_exempt = any(url.match(request.path_info) for url in settings.LOGIN_EXEMPT_URLS)
        if is_exempt or request.user.is_authenticated:
            return None
        else:
            return redirect(settings.LOGIN_URL)
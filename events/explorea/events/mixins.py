from django.core.exceptions import PermissionDenied
from django.views.generic.edit import FormMixin
from django.contrib import messages


class GroupRequiredMixin:
    groups_required = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        else:
            user_groups = set(request.user.groups.values_list('name', flat=True))
            if not user_groups.intersection(set(self.groups_required)):
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class GetFormMixin(FormMixin):

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'data': self.request.GET
        }
        return kwargs

class MessageActionMixin:
    @property
    def success_message(self):
        return NotImplemented

    @property
    def error_message(self):
        return NotImplemented

    def get_object(self, queryset=None):
        return getattr(self, 'object', None) or super().get_object(queryset)

    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)

    def form_invalid(self, form):
        obj = self.get_object()
        messages.error(self.request, self.error_message % obj.__dict__)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super().delete(request, *args, **kwargs)
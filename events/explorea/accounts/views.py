from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash, get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views.generic import TemplateView, ListView, DetailView, View
from django.views.generic.base import TemplateResponseMixin, ContextMixin
from django.views.generic.edit import CreateView, UpdateView, FormMixin, ProcessFormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import ImproperlyConfigured

from .forms import RegisterForm, EditUserForm, EditProfileForm
from .models import Profile

token_generator = PasswordResetTokenGenerator()
UserModel = get_user_model()


class MultipleFormsMixin(ContextMixin):
    form_classes = {}
    initial = {}
    success_url = ''

    def forms_valid(self, forms):
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data(forms=forms))

    def get_context_data(self, **kwargs):
        if 'forms' not in kwargs:
            forms = self.get_forms()
            for name, form in forms.items():
                kwargs[name] = form
        return super().get_context_data(**kwargs)

    def get_forms(self, form_classes=None):
        """Return a dict of form instances to be used in this view."""
        if form_classes is None:
            forms = self.get_form_classes()
        kwargs = self.get_forms_kwargs()

        return {name: form(**kwargs[name]) for name, form in forms.items()}

    def get_form_classes(self):
        return self.form_classes.copy()

    def get_forms_kwargs(self):
        kwargs = {}
        for name, form in self.form_classes.items():
            kwargs[name] = {
                'initial': self.get_initial(),
            }
            if self.request.method in ('POST', 'PUT'):
                kwargs[name].update({
                    'data': self.request.POST,
                    'files': self.request.FILES,
                })
        return kwargs

    def get_initial(self):
        return self.initial.copy()

    def get_success_url(self):
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)


class MultipleModelFormsMixin(MultipleFormsMixin):
    instances = {}

    def dispatch(self, request, *args, **kwargs):
        self.instances = self.get_instances()
        return super().dispatch(request, *args, **kwargs)

    def get_instances(self):
        instances = {}
        for name in self.form_classes:
            instances[name] = None
        return instances

    def forms_valid(self, forms):
        for form in forms:
            form.save()
        return super().forms_valid(forms)

    def get_forms_kwargs(self):
        kwargs = super().get_forms_kwargs()
        for name, form in self.form_classes.items():
            kwargs[name].update({
                'instance': self.instances[name]
            })
        return kwargs


class ProcessMultipleFormsView(MultipleFormsMixin, TemplateResponseMixin,
                               ProcessFormView):

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.forms = self.get_forms()
        if all(form.is_valid for form in self.forms.values()):
            return self.forms_valid(self.forms.values())
        else:
            return self.forms_invalid(self.forms.values())


class ProcessMultipleModelFormsView(MultipleModelFormsMixin, ProcessMultipleFormsView):
    pass


class BecomHostView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/verification_sent.html'

    def get(self, request, *args, **kwargs):
        verification_email_template = 'accounts/host_verification_email.html'
        email_context = {
            'user': request.user,
            'domain': get_current_site(request).domain,
            'uidb64': urlsafe_base64_encode(force_bytes(request.user.pk)),
            'token': token_generator.make_token(request.user)
        }

        html_body = render_to_string(verification_email_template, email_context)
        subject = 'Explorea Host Verification'
        from_email = 'admin@explorea.com'
        to_email = request.user.email

        email = EmailMessage(subject, html_body, from_email, [to_email])
        email.send()

        return super().get(request, *args, **kwargs)

class ActivateHostView(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            uidb64 = self.kwargs['uidb64']
            token = self.kwargs['token']
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and token_generator.check_token(user, token):
            user.profile.is_host = True
            user.profile.save()
            return render(request, 'accounts/verification_complete.html')

        else:
            return render(request, 'accounts/invalid_link.html')


class HostProfileView(LoginRequiredMixin, DetailView):
    model = UserModel
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'host'
    template_name = 'accounts/host_profile.html'



class HostListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'accounts/host_list.html'
    context_object_name  = 'profiles'

    def get_queryset(self):
        profiles = Profile.objects.filter(is_host=True)
        profiles = profiles.exclude(user__pk=self.request.user.id)
        return profiles

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'


class RegisterView(CreateView):
    model = UserModel
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        self.object = form.save()
        user = authenticate(username=self.object.username, password=form.cleaned_data['password1'])
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

class EditProfileView(LoginRequiredMixin, ProcessMultipleModelFormsView):
    template_name = 'accounts/edit_profile.html'
    form_classes = {'user_form': EditUserForm, 'profile_form': EditProfileForm}
    success_url = reverse_lazy('accounts:profile')

    def get_forms_kwargs(self):
        kwargs = super().get_forms_kwargs()
        kwargs['user_form'].update({
                'instance': self.request.user
        })
        kwargs['profile_form'].update({
                'instance': self.request.user.profile
        })
        return kwargs

class ChangePasswordView(LoginRequiredMixin, UpdateView):
    model = UserModel
    form_class = PasswordChangeForm
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        self.object = form.save()
        update_session_auth_hash(self.request, self.object)
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance')
        kwargs.update({'user': self.object})
        return kwargs

    def get_object(self):
        return self.request.user
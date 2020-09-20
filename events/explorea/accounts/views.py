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

from .forms import RegisterForm, EditUserForm, EditProfileForm
from .models import Profile

token_generator = PasswordResetTokenGenerator()
UserModel = get_user_model()

@login_required
def become_host(request):
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
    return render(request, 'accounts/verification_sent.html')

def activate_host(request, uidb64, token):
    try:
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

@login_required
def host_profile(request, username):
    host = UserModel.objects.get(username=username)
    return render(request, 'accounts/host_profile.html', {'host': host})

@login_required
def host_list(request):
    profiles = Profile.objects.filter(is_host=True)
    if request.user.profile.is_host:
        profiles = profiles.exclude(user__pk=request.user.id)

    return render(request, 'accounts/host_list.html', {'profiles': profiles})

@login_required
def profile(request):

    return render(request, 'accounts/profile.html')


def register(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            raw_password = form.cleaned_data.get('password1')
            
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)

            return redirect('/accounts/profile')
        else:
            return render(request, 'accounts/register.html', {'form': form} )

    form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form} )

@login_required
def edit_profile(request):
    form_user = EditUserForm(request.POST or None, instance=request.user)
    form_profile = EditProfileForm(request.POST or None, request.FILES or None, instance=request.user.profile)

    if request.method == 'POST':
        if form_user.is_valid() and form_profile.is_valid():
            user = form_user.save()
            profile = form_profile.save()
            # request.session['profile_changes'] = request.session.setdefault('profile_changes', 0) + 1
            return redirect('accounts:profile')
        else:
            return render(request, 'accounts/edit_profile.html', {'form_user': form_user, 'form_profile':form_profile} )

    return render(request, 'accounts/edit_profile.html', {'form_user':form_user, 'form_profile':form_profile} )

@login_required
def change_password(request):

    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('/accounts/profile/')
        else:
            return render(request, 'accounts/change_password.html', {'form': form})

    form = PasswordChangeForm(user=request.user)
    return render(request, 'accounts/change_password.html', {'form': form})



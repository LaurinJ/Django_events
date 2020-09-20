from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required

from .forms import RegisterForm, EditUserForm, EditProfileForm

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
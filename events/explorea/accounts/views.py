from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

from .forms import RegisterForm

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
            return redirect('profile')
    form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})
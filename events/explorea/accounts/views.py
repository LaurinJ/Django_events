from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login

from .forms import RegisterForm

def profile(request):
    return render(request, 'accounts/profile.html')

def register(request):
    if request.method == 'POST':

        # create the form and populate it with data from the POST request
        form = RegisterForm(request.POST)

        # validate the data in the form
        if form.is_valid():
            # get the validated data from the form
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            password = form.cleaned_data.get('password1')

            # create and save the user
            User = get_user_model()
            u = User(username=username,
                     email=email,
                     first_name=first_name,
                     last_name=last_name)
            u.set_password(password)
            u.save()

            user = authenticate(username=username, password=password)
            login(request, user)

            # redirect to another page
            return redirect('profile')

        # if the request is of type GET
    form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})
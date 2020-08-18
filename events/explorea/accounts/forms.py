from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

UserModel = get_user_model()

class RegisterForm(UserCreationForm):

    class Meta:
        model = UserModel
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        ]

class EditProfileForm(UserChangeForm):

    class Meta:
        model = UserModel
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        ]


# class RegisterForm(forms.Form):
#     username = forms.CharField(max_length=30, help_text='How will we call you?')
#     email = forms.EmailField()
#     first_name = forms.CharField(max_length=100)
#     last_name = forms.CharField(max_length=100)
#     password1 = forms.CharField(
#         label="Password",
#         strip=False,
#         widget=forms.PasswordInput,
#     )
#     password2 = forms.CharField(
#         label="Password confirmation",
#         widget=forms.PasswordInput,
#         strip=False,
#         help_text="Enter the same password as before, for verification.",
#     )
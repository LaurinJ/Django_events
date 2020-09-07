from django.urls import path, re_path
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name="accounts/login.html"), name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(template_name="accounts/logged_out.html"),
         name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),

    path('reset-password/', auth_views.PasswordResetView.as_view(
        template_name = 'accounts/reset_password.html',
        email_template_name='accounts/reset_password_email.html'
        ),
        name='reset_password'),

    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(),  name='password_reset_done'),
    re_path(r'^reset-password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
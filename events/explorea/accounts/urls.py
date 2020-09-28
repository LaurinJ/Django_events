from django.urls import path, re_path
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name="accounts/login.html"), name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(template_name="accounts/logged_out.html"),
         name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('hosts/', views.HostListView.as_view(), name='host_list'),
    path('host/profile/<username>/', views.HostListView.as_view(), name='host_profile'),

    path('become-host/', views.BecomHostView.as_view(), name='become_host'),
    re_path(r'^become-host/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.ActivateHostView.as_view(),
        name='activate_host'),

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
app_name = 'accounts'


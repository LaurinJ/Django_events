from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('events/<int:id>/', views.event_detail, name='events'),
    path('events/', views.event_listing, name='event_listing'),
    path('events/add/', views.create_event, name='create_event'),
    path('events/<int:pk>/edit', views.edit_event, name='edit_event'),
    path('events/<int:pk>/add_run/', views.create_event_run, name='create_event_run'),
    path('events/<int:pk>/edit_run/', views.edit_event_run, name='edit_event_run'),
]

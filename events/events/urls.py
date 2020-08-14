from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('events/<int:id>/', views.event_detail, name='events'),
    path('events/', views.event_listing, name='event_listing'),
]

from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    # path('', views.index, name='index'),
    # path('', views.event_listing, name='events'),
    path('new/', views.CreateEventView.as_view(), name='create_event'),
    path('mine/', views.MyEventView.as_view(), name='my_events'),
    path('search/', views.EventSearchView.as_view(), name='search'),

    path('detail/<slug:slug>/', views.EventDetailView.as_view(), name='detail'),
    path('update/<slug:slug>/', views.UpdateEventView.as_view(), name='update_event'),
    path('delete/<slug:slug>/', views.DeleteEventView.as_view(), name='delete_event'),
    
    path('<slug:event_slug>/update-run/<int:pk>/', views.UpdateEventRunView.as_view(), name='update_event_run'),
    path('delete-run/<int:pk>/', views.DeleteEventRunView.as_view(), name='delete_event_run'),
    path('<slug:slug>/newRun/', views.CreateEventRunView.as_view(), name='create_event_run'),
    path('<category>/', views.EventListView.as_view(), name='events'),
    
]
from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.event_listing, name='events'),
    path('new/', views.CreateEventView.as_view(), name='create_event'),
    path('mine/', views.MyEventView.as_view(), name='my_events'),
    path('search/', views.event_search, name='search'),

    path('detail/<slug:slug>/', views.EventDetailView.as_view(), name='detail'),
    path('update/<slug:slug>/', views.UpdateEventView.as_view(), name='update_event'),
    path('delete/<slug:slug>/', views.DeleteEventView.as_view(), name='delete_event'),
    
    path('updateRun/<int:event_run_id>', views.update_event_run, name='update_event_run'),
    path('deleteRun/<int:event_run_id>', views.delete_event_run, name='delete_event_run'),
    path('<int:event_id>/newRun/', views.create_event_run, name='create_event_run'),
    path('<category>/', views.event_listing, name='events_by_category'),
    
]
from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.event_listing, name='events'),
    path('new/', views.create_event, name='create_event'),
    path('mine/', views.my_events, name='my_events'),
    path('search/', views.event_search, name='search'),
    
    path('detail/<int:pk>', views.event_detail, name='detail'),
    path('update/<int:pk>', views.update_event, name='update_event'),
    path('delete/<int:pk>', views.delete_event, name='delete_event'),
    
    path('updateRun/<int:event_run_id>', views.update_event_run, name='update_event_run'),
    path('deleteRun/<int:event_run_id>', views.delete_event_run, name='delete_event_run'),
    path('<int:event_id>/newRun/', views.create_event_run, name='create_event_run'),
    path('<category>/', views.event_listing, name='events_by_category'),
    
]
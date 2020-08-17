from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('explorea.events.urls')),
    path('accounts/', include('explorea.accounts.urls')),
]

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from explorea.events import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('events/', include('explorea.events.urls', namespace='events')),
    path('accounts/', include('explorea.accounts.urls', namespace='accounts')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
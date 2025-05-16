from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('countries.urls')),
    path('accounts/', include('accounts.urls')),
    path('api/', include('accounts.urls', namespace='api')),  # Add API endpoints
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if settings.DEBUG else []
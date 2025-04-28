from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('countries.urls')),
    path('users/', include('users.urls')),
    path('countries/', include('countries.urls'), name='countries'),
    
]
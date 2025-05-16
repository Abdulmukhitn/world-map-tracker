from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

# Create router for API endpoints
router = DefaultRouter()
router.register(r'visits', views.VisitViewSet, basename='visit')

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('api/', include(router.urls)),  # Add API endpoints
]
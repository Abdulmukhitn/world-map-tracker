from django.urls import path
from . import views

app_name = 'ai_guide'

urlpatterns = [
    path('', views.guide, name='guide'),
    path('api/travel-guide/', views.travel_guide, name='travel_guide'),
]
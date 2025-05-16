from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'countries'

router = DefaultRouter()
router.register(r'travel-plans', views.TravelPlanViewSet, basename='travel-plan')
router.register(r'journals', views.TravelJournalViewSet, basename='journal')
router.register(r'groups', views.TravelGroupViewSet, basename='group')
router.register(r'tips', views.TravelTipViewSet, basename='tip')

urlpatterns = [
    path('', views.MapView.as_view(), name='map'),
    path('api/countries/', views.country_list, name='country-list'),
    path('api/visits/', views.visits_view, name='visits-list-create'),
    path('api/visits/<str:iso_code>/', views.visit_detail, name='visit-detail'),
    path('api/', include(router.urls)),
    path('achievements/', views.achievement_list, name='achievements'),
    path('travel-stats/', views.travel_stats, name='travel-stats'),
    path('api/travel-stats/', views.travel_stats_api, name='travel-stats-api'),
]
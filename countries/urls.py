from django.urls import path
from . import views

app_name = 'countries'

urlpatterns = [
    path('', views.MapView.as_view(), name='map'),
    path('api/countries/', views.country_list, name='country-list'),
    path('api/visits/', views.visits_view, name='visits-list-create'),
    path('api/visits/<str:iso_code>/', views.visit_detail, name='visit-detail'),
]
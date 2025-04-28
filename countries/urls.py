from django.urls import path
from . import views

app_name = 'countries'

urlpatterns = [
    path('', views.MapView.as_view(), name='map'),
    path('api/countries/', views.country_list, name='country-list'),
    path('api/visits/', views.visits_view, name='visits_view'),  # общий для GET и POST
    path('api/visits/<str:iso_code>/', views.update_delete_visit, name='update_delete_visit'),
]
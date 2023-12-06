from django.urls import path, include
from . import views
from .views import *

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('logout/', views.logout, name='logout'),
    path('submit_water_station/', views.submit_water_station, name='submit_water_station'),
    path('map',views.map, name='map'),
    path('map/<str:place_id>/', views.MapStationsView.as_view(), name='map_stations'),
    path('approve_water_station/', views.approve_water_station, name='approve_water_station'),
    path('error/', views.error, name='error'),
    path('user_water_stations/', user_water_stations,name='user_water_stations'),
]
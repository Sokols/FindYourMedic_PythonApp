from django.urls import path

from .views import find_station_view

app_name = 'airqualitystations'
urlpatterns = [
    path('', find_station_view)
]

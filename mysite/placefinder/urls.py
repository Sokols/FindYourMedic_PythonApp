from django.urls import path

from .views import find_place_view

app_name = 'placefinder'
urlpatterns = [
    path('', find_place_view)
]

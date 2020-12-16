from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModelForm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
import folium


def calculate_distance_view(request):
    # initial values
    distance = None
    destination = None
    folium_map = None

    form = MeasurementModelForm(request.POST or None)
    geo_locator = Nominatim(user_agent='findyourmedic')

    # ip = get_ip_address(request)
    ip = '2.23.108.1'
    location_country, location_city, location_latitude, location_longitude = get_geo(ip)
    location = geo_locator.geocode(location_city)

    # setting coordinates of location
    location_point = (location_latitude, location_longitude)

    if form.is_valid():
        instance = form.save(commit=False)
        _destination = form.cleaned_data.get('destination')
        destination = geo_locator.geocode(_destination)

        # setting coordinates of destination
        destination_latitude = destination.latitude
        destination_longitude = destination.longitude
        destination_point = (destination_latitude, destination_longitude)

        # distance calculation
        distance = round(geodesic(location_point, destination_point).km, 2)

        # setting folium map
        folium_map = folium.Map(width=800, height=500, zoom_start=get_zoom(distance), location=get_center_coordinates(
            location_latitude, location_longitude, destination_latitude, destination_longitude))

        # location marker
        folium.Marker([location_latitude, location_longitude], tooltip='click here for more',
                      popup=location_city['city'],
                      icon=folium.Icon(color='purple')).add_to(folium_map)

        # destination marker
        folium.Marker([destination_latitude, destination_longitude], tooltip='click here for more', popup=destination,
                      icon=folium.Icon(color='red', icon='cloud')).add_to(folium_map)

        # draw the line between location and destination
        line = folium.PolyLine(locations=[location_point, destination_point], weight=5, color='blue')
        folium_map.add_child(line)

        instance.location = location
        instance.distance = distance
        instance.save()

    folium_map = folium_map._repr_html_()

    # dictionary used in the template
    context = {
        'distance': distance,
        'destination': destination,
        'form': form,
        'map': folium_map,
    }

    return render(request, 'findyourmedic/main.html', context)

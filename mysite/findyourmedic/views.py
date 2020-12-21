import folium
from django.shortcuts import render
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

from .forms import MeasurementModelForm
from .utils import get_geo, get_center_coordinates


def calculate_distance_view(request):
    # initial values
    distance = None
    destination = None

    form = MeasurementModelForm(request.POST or None)
    geo_locator = Nominatim(user_agent='findyourmedic')

    # ip = get_ip_address(request)
    ip = '2.23.108.1'
    location_country, location_city, location_latitude, location_longitude = get_geo(ip)
    location = geo_locator.geocode(location_city)

    # setting coordinates of location
    location_point = (location_latitude, location_longitude)

    # setting folium map
    folium_map = folium.Map(location=(location_latitude, location_longitude))

    # location marker
    folium.Marker([location_latitude, location_longitude], tooltip='click here for more',
                  popup=location_city['city'],
                  icon=folium.Icon(color='purple')).add_to(folium_map)

    if form.is_valid():
        instance = form.save(commit=False)
        destination = geo_locator.geocode(form.cleaned_data.get('location'))

        # setting coordinates of destination
        destination_latitude = destination.latitude
        destination_longitude = destination.longitude
        destination_point = (destination_latitude, destination_longitude)

        # distance calculation
        distance = round(geodesic(location_point, destination_point).km, 2)

        # setting folium map
        folium_map = folium.Map(location=get_center_coordinates(
            location_latitude, location_longitude, destination_latitude, destination_longitude))

        # location marker
        folium.Marker([location_latitude, location_longitude], tooltip='click here for more',
                      popup=location_city['city'],
                      icon=folium.Icon(color='purple')).add_to(folium_map)

        # destination marker
        folium.Marker([destination_latitude, destination_longitude], tooltip='click here for more', popup=destination,
                      icon=folium.Icon(color='red', icon='cloud')).add_to(folium_map)

        # map zoom scale
        folium_map.fit_bounds(bounds=[(location_latitude, location_longitude),
                                      (destination_latitude, destination_longitude)])

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

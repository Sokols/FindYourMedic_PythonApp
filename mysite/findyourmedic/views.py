import folium
from django.shortcuts import render
from geopy.geocoders import Nominatim

from .forms import MeasurementModelForm
from .models import Station
from .utils import get_center_coordinates, get_destination_for_location


def calculate_distance_view(request):
    # initial values
    distance = None
    location = None

    form = MeasurementModelForm(request.POST or None)
    geo_locator = Nominatim(user_agent='findyourmedic')

    folium_map = folium.Map()

    if form.is_valid():
        instance = form.save(commit=False)
        location = geo_locator.geocode(form.cleaned_data.get('location'))

        # get nearest station data
        data = get_destination_for_location(location)
        station = data['station']
        distance = data['distance']

        # set location and station points
        location_point = (location.latitude, location.longitude)

        # setting folium map
        folium_map = folium.Map(location=get_center_coordinates(
            location.latitude, location.longitude, station.latitude, station.longitude))

        # location marker
        folium.Marker(location_point, tooltip='Click here for more!',
                      popup=location.address,
                      icon=folium.Icon(color='purple')).add_to(folium_map)

        # station marker
        folium.Marker([station.latitude, station.longitude], tooltip='Click here for more!', popup=station.station_name,
                      icon=folium.Icon(color='red', icon='cloud')).add_to(folium_map)

        # map zoom scale
        folium_map.fit_bounds(bounds=[location_point,
                                      (station.latitude, station.longitude)])

        # draw the line between location and destination
        line = folium.PolyLine(locations=[location_point, (station.latitude, station.longitude)], weight=5,
                               color='blue')
        folium_map.add_child(line)

        instance.location = location
        instance.distance = distance
        instance.save()

    folium_map = folium_map._repr_html_()

    # dictionary used in the template
    context = {
        'distance': distance,
        'location': location,
        'form': form,
        'map': folium_map,
    }

    return render(request, 'findyourmedic/main.html', context)

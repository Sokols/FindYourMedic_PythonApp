import folium
from django.shortcuts import render
from geopy.geocoders import Nominatim

from .forms import MeasurementModelForm
from .utils import get_center_coordinates, get_destination_for_localization


def calculate_distance_view(request):
    # initial values
    distance = None
    localization = None
    station = None

    form = MeasurementModelForm(request.POST or None)
    geo_locator = Nominatim(user_agent='airqualitystations')

    folium_map = folium.Map()

    if form.is_valid():
        localization = geo_locator.geocode(form.cleaned_data.get('localization'))

        if localization:
            print(localization.address)

            # get nearest station data
            data = get_destination_for_localization(localization)
            station = data['station']
            distance = data['distance']

            # set localization and station points
            location_point = (localization.latitude, localization.longitude)
            station_point = (station.latitude, station.longitude)

            # setting folium map
            folium_map = folium.Map(location=get_center_coordinates(
                localization.latitude, localization.longitude, station.latitude, station.longitude))

            # localization marker
            folium.Marker(location_point,
                          tooltip='Click here for more!',
                          popup=localization.address,
                          icon=folium.Icon(color='red', icon='home')).add_to(folium_map)

            # station marker
            folium.Marker(station_point,
                          tooltip='Click here for more!',
                          popup=station.station_name,
                          icon=folium.Icon(color='blue', icon='flash')).add_to(folium_map)

            # map zoom scale
            folium_map.fit_bounds(bounds=[location_point, station_point])

            # draw the line between localization and destination
            folium_map.add_child(folium.PolyLine(locations=[location_point, station_point],
                                                 weight=3,
                                                 color='red'))

            instance = form.save(commit=False)
            instance.localization = localization
            instance.station = station.station_name
            instance.distance = distance
            instance.save()

    folium_map = folium_map._repr_html_()

    # dictionary used in the template
    context = {
        'distance': distance,
        'station': station,
        'localization': localization,
        'form': form,
        'map': folium_map,
    }

    return render(request, 'airqualitystations/main.html', context)

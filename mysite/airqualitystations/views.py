import folium
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from geopy.geocoders import Nominatim

from .forms import MeasurementModelForm
from .utils import get_destination_for_localization, prepare_map


def find_station_view(request):
    """
    Method is the main view of site - finds the nearest air quality station from typed location.
    :param request: request from site
    :return: render of site
    """
    # initial values
    distance = None
    localization = None
    station = None
    form = MeasurementModelForm(request.POST or None)
    geo_locator = Nominatim(user_agent='airqualitystations')
    folium_map = folium.Map()

    if form.is_valid():
        localization = geo_locator.geocode(form.cleaned_data.get('localization'))

        # check if typed localization really exists
        if localization:

            # get the nearest station data
            station_dict = get_destination_for_localization(localization)
            station = station_dict['station']
            distance = station_dict['distance']

            folium_map = prepare_map(localization, station)

            # save data into local database
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

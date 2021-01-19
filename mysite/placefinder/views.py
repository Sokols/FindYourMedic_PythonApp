import folium
from django.shortcuts import render
from geopy.geocoders import Nominatim

from .forms import MeasurementModelForm
from .models import CONTENT_TYPE_CHOICES
from .utils import get_destination_for_localization, prepare_map


def find_place_view(request):
    """
    Method is the main view of site - finds the nearest chosen destination.
    :param request: request from site
    :return: render of site
    """
    # initial values
    distance = None
    localization = None
    destination = None
    form = MeasurementModelForm(request.POST or None)
    geo_locator = Nominatim(user_agent='placefinder')
    folium_map = folium.Map()

    if form.is_valid():
        localization = geo_locator.geocode(form.cleaned_data.get('localization'))

        # check if typed localization really exists
        if localization:

            content_type = form.cleaned_data.get('content_type')
            path_type = form.cleaned_data.get('path_type')
            # get the nearest destination data
            destination_dict = get_destination_for_localization(localization, content_type)
            destination = destination_dict['destination']
            distance = destination_dict['distance']

            folium_map = prepare_map(localization, destination, path_type)

            # save data into local database
            instance = form.save(commit=False)
            instance.localization = localization
            instance.destination = destination.name
            instance.distance = distance
            instance.save()

    folium_map = folium_map._repr_html_()

    # dictionary used in the template
    context = {
        'distance': distance,
        'destination': destination,
        'localization': localization,
        'form': form,
        'map': folium_map,
    }

    return render(request, 'placefinder/main.html', context)

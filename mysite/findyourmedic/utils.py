import requests
from geopy.distance import geodesic

from .models import Station


def get_center_coordinates(loc_lat, loc_long, dest_lat=None, dest_long=None):
    coordinates = (loc_lat, loc_long)
    if dest_lat:
        coordinates = [(loc_lat + dest_lat) / 2, (loc_long + dest_long) / 2]
    return coordinates


def get_stations_list():
    api = "http://api.gios.gov.pl/pjp-api/rest/station/findAll"
    data = requests.get(api).json()
    station_list = list()
    for obj in data:
        station = Station(obj)
        station_list.append(station)
    return station_list


def get_destination_for_location(location):
    # set coordinates of location
    location_point = (location.latitude, location.longitude)

    # check distance for every station
    station_list = get_stations_list()
    distance = 0
    nearest_station = None
    for station in station_list:
        station_point = (station.latitude, station.longitude)
        temp_distance = round(geodesic(location_point, station_point).km, 2)

        # save nearer distance and station
        if temp_distance <= distance or station == station_list[0]:
            distance = temp_distance
            nearest_station = station

    return dict({'station': nearest_station, 'distance': distance})

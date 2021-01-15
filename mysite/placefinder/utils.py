import folium
import requests
# import osmnx as ox
# import networkx as nx

from geopy.distance import geodesic

from .models import Station


def get_center_coordinates(loc_lat, loc_long, dest_lat=None, dest_long=None):
    """
    Method calculates a center point of two or one other points.
    :param loc_lat: location latitude
    :param loc_long: location longitude
    :param dest_lat: destination longitude (optional)
    :param dest_long: destination longitude (optional)
    :return: center point
    """
    coordinates = (loc_lat, loc_long)
    if dest_lat:
        coordinates = [(loc_lat + dest_lat) / 2, (loc_long + dest_long) / 2]
    return coordinates


def get_stations_list():
    """
    Method retrieves a list of stations from a remote database.
    :return: list of stations
    """
    api = "http://api.gios.gov.pl/pjp-api/rest/station/findAll"
    data = requests.get(api).json()
    station_list = list()
    for obj in data:
        station = Station(obj)
        station_list.append(station)
    return station_list


def get_destination_for_localization(localization):
    """
    Method to get the destination for localization from remote database.
    :param localization: address of the location
    :return: dictionary with the station name and distance from the location
    """
    # set coordinates of location
    localization_point = (localization.latitude, localization.longitude)

    station_list = get_stations_list()
    distance = 0
    nearest_station = None

    # check distance for every station
    for station in station_list:
        station_point = (station.latitude, station.longitude)
        temp_distance = round(geodesic(localization_point, station_point).km, 2)

        # save nearer distance and station
        if temp_distance <= distance or station == station_list[0]:
            distance = temp_distance
            nearest_station = station

    return dict({'station': nearest_station, 'distance': distance})


def prepare_map(localization, station):
    """
    Method prepares the map for display.
    :param localization: typed localization point
    :param station: found station point
    :return: prepared map
    """
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
    return folium_map

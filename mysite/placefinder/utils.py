import csv
import os
from typing import List

import folium
import networkx as nx
import osmnx as ox
import requests
from geopy.distance import geodesic

from .models import Station, CONTENT_TYPE_CHOICES, PATH_TYPE_CHOICES, Destination


def get_center_coordinates(loc_lat, loc_long, dest_lat=None, dest_long=None):
    """
    Method calculates a center point of two or one point.
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
    station_dest_list: List[Destination] = list()
    for obj in data:
        station = Station(obj)
        station_dest_list.append(Destination(name=station.station_name,
                                             address=station.address_street,
                                             city=station.city.name,
                                             latitude=station.latitude,
                                             longitude=station.longitude))

    return station_dest_list


def get_medicals_list():
    file = os.path.dirname(os.path.abspath(__file__)) + '\\data\\rejestr.csv'
    medical_dest_list: List[Destination] = list()
    with open(file, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=';')
        next(csv_reader)
        for i, row in enumerate(csv_reader):
            medical_dest_list.append(Destination(name=row[0],
                                                 city=row[4],
                                                 address=row[4] + " " + row[5] + " " + row[6],
                                                 latitude=float(row[7]),
                                                 longitude=float(row[8])))
        file.close()
    return medical_dest_list


def get_destination_for_localization(localization, content_type):
    """
    Method to get the destination for localization from remote database.
    :param localization: address of the location
    :param content_type: type of content
    :return: dictionary with the destination name and distance from the location
    """
    # set coordinates of location
    localization_point = (localization.latitude, localization.longitude)

    destinations = None
    distance = 0
    nearest_destination = None

    # MEDICALS
    if content_type == CONTENT_TYPE_CHOICES[0][0]:
        destinations = get_medicals_list()

    # STATIONS
    elif content_type == CONTENT_TYPE_CHOICES[1][0]:
        destinations = get_stations_list()

    # check distance for every destination
    for destination in destinations:
        destination_point = (destination.latitude, destination.longitude)
        temp_distance = round(geodesic(localization_point, destination_point).km, 2)

        # save nearer distance and destination
        if temp_distance <= distance or destination == destinations[0]:
            distance = temp_distance
            nearest_destination = destination

    return dict({'destination': nearest_destination, 'distance': distance})


def prepare_map(localization, destination, path_type):
    """
    Method prepares the map for display.
    :param localization: typed localization point
    :param destination: found destination point
    :param path_type: type of path
    :return: prepared map
    """
    # set localization and destination points
    location_point = (localization.latitude, localization.longitude)
    destination_point = (destination.latitude, destination.longitude)

    # setting folium map
    folium_map = folium.Map(location=get_center_coordinates(
        localization.latitude, localization.longitude, destination.latitude, destination.longitude))

    # localization marker
    folium.Marker(location_point,
                  tooltip='Click here for more!',
                  popup=localization.address,
                  icon=folium.Icon(color='red', icon='home')).add_to(folium_map)

    # destination marker
    folium.Marker(destination_point,
                  tooltip='Click here for more!',
                  popup=destination.name,
                  icon=folium.Icon(color='blue', icon='flash')).add_to(folium_map)

    # map zoom scale
    folium_map.fit_bounds(bounds=[location_point, destination_point])

    # STRAIGHT LINE
    if path_type == PATH_TYPE_CHOICES[0][0]:
        folium_map.add_child(folium.PolyLine(locations=[location_point, destination_point],
                                             weight=3,
                                             color='red'))

    # ROUTE
    elif path_type == PATH_TYPE_CHOICES[1][0]:
        ox.config(log_console=True, use_cache=True)
        graph = ox.graph_from_point(location_point, dist_type='network', dist=3000)
        location_node = ox.get_nearest_node(graph, location_point)
        destination_node = ox.get_nearest_node(graph, destination_point)
        route = nx.shortest_path(graph, location_node, destination_node)
        ox.plot_route_folium(graph, route, folium_map)

    return folium_map

from django.contrib.gis.geoip2 import GeoIP2


# Helper functions

def get_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_geo(ip):
    geo = GeoIP2()
    country = geo.country(ip)
    city = geo.city(ip)
    lat, lon = geo.lat_lon(ip)
    return country, city, lat, lon


def get_center_coordinates(loc_lat, loc_long, dest_lat=None, dest_long=None):
    coordinates = (loc_lat, loc_long)
    if dest_lat:
        coordinates = [(loc_lat + dest_lat) / 2, (loc_long + dest_long) / 2]
    return coordinates


def get_zoom(distance):
    if distance <= 100:
        return 8
    elif 100 < distance <= 5000:
        return 4
    else:
        return 2


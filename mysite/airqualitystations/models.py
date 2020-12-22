from django.db import models


class Measurement(models.Model):
    localization = models.CharField(max_length=500)
    station = models.CharField(max_length=500)
    distance = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.localization} to {self.station} is {self.distance} km."


class Commune:
    commune_name: str
    district_name: str
    province_name: str

    def __init__(self, dict, *args, **entries):
        super().__init__(*args, **entries)
        self.commune_name = dict['communeName']
        self.district_name = dict['districtName']
        self.province_name = dict['provinceName']


class City:
    city_id: int
    name: str
    commune: Commune

    def __init__(self, dict, *args, **entries):
        super().__init__(*args, **entries)
        self.city_id = int(dict['id'])
        self.name = dict['name']
        self.commune = Commune(dict['commune'])


class Station(models.Model):
    station_id: int
    station_name: str
    latitude: float
    longitude: float
    city: City
    address_street: str

    def __init__(self, dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.station_id = int(dict['id'])
        self.station_name = dict['stationName']
        self.latitude = float(dict['gegrLat'])
        self.longitude = float(dict['gegrLon'])
        self.city = City(dict['city'])
        self.address_street = dict['addressStreet']

    def __str__(self):
        return f"{self.station_name} - {self.address_street}"

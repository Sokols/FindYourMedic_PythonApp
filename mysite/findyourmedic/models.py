from django.db import models


class Measurement(models.Model):
    location = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    distance = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Distance from {self.location} to {self.destination} is {self.distance} km."


class Commune(models.Model):
    commune_name = models.CharField(max_length=50)
    district_name = models.CharField(max_length=50)
    province_name = models.CharField(max_length=20)

    def __init__(self, dict, *args, **entries):
        super().__init__(*args, **entries)
        self.commune_name = dict['communeName']
        self.district_name = dict['districtName']
        self.province_name = dict['provinceName']


class City(models.Model):
    city_id = models.IntegerField()
    name = models.CharField(max_length=50)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE)

    def __init__(self, dict, *args, **entries):
        super().__init__(*args, **entries)
        self.city_id = dict['id']
        self.name = dict['name']
        self.commune = Commune(dict['commune'])


class Station(models.Model):
    station_id = models.IntegerField()
    station_name = models.CharField(max_length=50)
    latitude = models.CharField(max_length=10)
    longitude = models.CharField(max_length=10)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    address_street = models.CharField(max_length=50)

    def __init__(self, dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.station_id = dict['id']
        self.station_name = dict['stationName']
        self.latitude = float(dict['gegrLat'])
        self.longitude = float(dict['gegrLon'])
        self.city = City(dict['city'])
        self.address_street = dict['addressStreet']

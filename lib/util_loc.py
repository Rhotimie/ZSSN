
import requests
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="twint-1.2")

def getLocation(place):
    """
    This function takes in an address and then returns the latitude and longitude
    """
    location = geolocator.geocode(place,timeout=1000)
    if location:
        return {"lat": location.latitude, "lon": location.longitude}
    else:
        return {}


def get_country_from_gpe_entity(entity):
    """
    This function takes in an input gpe entity and then returns the latitude and longitude
    """
    try:
        geolocator = Nominatim(user_agent = "geoapiExercises")
        location = geolocator.geocode(entity)

        latitude = location.raw['lat']
        longitude = location.raw['lon']

        return {"lat": latitude, "lon": longitude}
    except:
        return {"lat": 48.1104, "lon": -1.65089}


def ip_api(ip_address):
    try:
        response = requests.get("http://ip-api.com/json/92.168.8.101")
    except:
        return {"lat": 48.1104, "lon": -1.65089}
        
    if response.status_code == 200:
        data = response.json()
        return {"lat": data['lat'], "lon": data['lon']}
    else:
        return {"lat": 48.1104, "lon": -1.65089}
    


import requests

class PhysicalLocation:
    def __init__(self, location):
        try:
            self.place_id = location["place_id"]
        except:
            self.place_id = None
        try:
            self.licence = location["licence"]
        except:
            self.licence = None
        try:
            self.osm_type = location["osm_type"]
        except:
            self.osm_type = None
        try:
            self.osm_id = location["osm_id"]
        except:
            self.osm_id = None
        try:
            self.lat = location["lat"]
        except:
            self.lat = None
        try:
            self.lon = location["lon"]
        except:
            self.lon = None
        try:
            self.display_name = location["display_name"]
        except:
            self.display_name = None
        try:
            self.address = location["address"]
        except:
            self.address = None
        try:
            self.house_number = location["address"]["house_number"]
        except:
            self.house_number = None
        try:
            self.road = location["address"]["road"]
        except:
            self.road = None
        try:
            self.town = location["address"]["town"]
        except:
            self.town = None
        try:
            self.state = location["address"]["state"]
        except:
            self.state = None
        try:
            self.postcode = location["address"]["postcode"]
        except:
            self.postcode = None
        try:
            self.country = location["address"]["country"]
        except:
            self.country = None
        try:
            self.country_code = location["address"]["country_code"]
        except:
            self.country_code = None
        try:
            self.ISO3166 = location["address"]["ISO3166-2-lvl4"]
        except:
            self.ISO3166 = None

class Geocoder:
    def __init__(self):
        self.api_url = "https://nominatim.openstreetmap.org/reverse?"

    def reverse(self, latitude, longitude, params=None):
        """Reverse geocode a latitude and longitude coordinate."""
        parameters = "&format=json"
        formatted_location = f"lat={str(latitude)}&lon={str(longitude)}"
        url = self.api_url + formatted_location + parameters
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def resolve(self, address):
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data:
                lat = data[0]['lat']
                lon = data[0]['lon']
                return lat, lon
            else:
                return -1, -1
        else:
            print("Error:", response.status_code)

def closest_dc(x, y):
    import math
    known_coordinates = {
        (39.9527237, -75.1635262): ("ZSIPV4P", "ZSIPV4MIP"),
        (41.8755616, -87.6244212): ("ZSIPV4", "ZSIPV4MI"),
        (47.6038321, -122.330062): ("ZSIPV4S", "ZSIPV4MIS")
    }

    closest_distance = math.inf
    closest_location = None

    for coordinate, location in known_coordinates.items():
        distance = math.sqrt((x - coordinate[0])**2 + (y - coordinate[1])**2)
        if distance < closest_distance:
            closest_distance = distance
            closest_location = location

    return closest_location


if __name__ == "__main__":
    geocoder = Geocoder()
    location = geocoder.reverse(41.97678587339972, -88.1881974823613)
    if location:
        print(location["address"])

    target = "Philadelphia"
    latitude, longitude = geocoder.resolve(target)
    print(f"Lat: {latitude} // Long: {longitude}")


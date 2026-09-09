import requests
from datetime import datetime
#this script essentially just requests for any earthquakes with a minimum magnitude of 2.5
#from the start point of 30 days ago to present with a limit of 10 earthquakes
url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

parameters = { #these are the parameters by which the api is following
    "format": "geojson", #gives the results in geojson format
    "minmagnitude": 2.5,
    "orderby": "time",
    "limit": 10
}

response = requests.get(url, params=parameters) #this is what initiates the request

data = response.json()

for earthquake in data["features"]: #basically a loop that says for each earthquake in "features" (where the earthquake data is stored), print its place and magnitude
    earthquake_id = earthquake["id"]
    location = earthquake["properties"]["place"]
    magnitude = earthquake["properties"]["mag"]
    time = datetime.fromtimestamp(earthquake["properties"]["time"]/1000)

print("ID:", earthquake_id)
print("Location:", location)
print("Magnitude:", magnitude)
print("Time:", time)
print()
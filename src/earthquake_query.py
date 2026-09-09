import requests
from datetime import datetime #this is just so the time actually converts into something readable when requesting time
#this script essentially just requests for any earthquakes with a minimum magnitude of 2.5
#from the start point of 30 days ago to present with a limit of 10 earthquakes
url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

parameters = { #these are the parameters by which the api is following
    "format": "geojson", #gives the results in geojson format
    "minmagnitude": 2.5, #minimum magnitude that i set
    "orderby": "time", #makes sure that the results are in order by most recent
    "limit": 10 #sets a limit of 10 results for general visibility
}

response = requests.get(url, params=parameters) #this is what initiates the request

data = response.json()

for earthquake in data["features"]: #basically a loop that says for each earthquake in "features" (where the earthquake data is stored), print its id, place, magnitude, and time
    earthquake_id = earthquake["id"] #this is what retrieves the ID of the earthquake
    location = earthquake["properties"]["place"] #^ and for location
    magnitude = earthquake["properties"]["mag"]#^ and for magnitude
    time = datetime.fromtimestamp(earthquake["properties"]["time"]/1000) #and finally the time, which it converts from a timestamp into a normal date and time
    print("ID:", earthquake_id)
    print("Location:", location)
    print("Magnitude:", magnitude)
    print("Time:", time)
    print()

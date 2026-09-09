import requests
#this script essentially just requests for any earthquakes with a minimum magnitude of 2.5
#from the start point of 30 days ago to present with a limit of 10 earthquakes
url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

parameters = { #these are the parameters by which the api is following
    "format": "geojson",
    "minmagnitude": 2.5,
    "orderby": "time",
    "limit": 10
}

response = requests.get(url, params=parameters)

data = response.json()

for earthquake in data["features"]:
    print(earthquake["properties"]["place"]) #prints the properties of each earthquake (ie location and distance from major city)
    print(earthquake["properties"]["mag"]) #prints the magnitude of each earthquake (should be a min of 2.5)
    print()


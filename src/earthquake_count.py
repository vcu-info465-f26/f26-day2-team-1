import requests

url = "https://earthquake.usgs.gov/fdsnws/event/1/count"

parameters = { #these are the parameters by which the api is following
    "minmagnitude": 2.5,
}

response = requests.get(url, params=parameters)

print("Number of earthquakes:")
print(response.text)
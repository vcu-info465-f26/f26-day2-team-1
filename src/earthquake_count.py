import requests
#this is a lot simpler it basically requests data based on my parameters and gives me a number
url = "https://earthquake.usgs.gov/fdsnws/event/1/count"

parameters = { #these are the parameters by which the api is following
    "minmagnitude": 2.5,
}

response = requests.get(url, params=parameters)

print("Number of earthquakes:")
print(response.text)
import requests
url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
parameters = {
    "format": "geojson",
    "eventid": "us7000tgb4"
}
response= requests.get(url, params=parameters)
data = response.json()

print(data.keys())
print(data["properties"].keys())
print(data)


import requests
# uses earthquake id from endpoint 1 to get more details about that specific earthquake
def get_earthquake_details(event_id):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
# eventid talks to the api about which specific earthquake to return
    parameters = {
        "format": "geojson",
        "eventid": event_id
    }
    response= requests.get(url, params=parameters)
    data = response.json()

    print(data.keys())
    print(data["properties"].keys())
    
# properties saves the earthquake info so details are easier to access
    properties = data["properties"]
# coordinates include longitude,lat,and depth
    coordinates = data["geometry"]["coordinates"]
# cherry picking the specific earthquake details we want from the response
    details = {
        "id": data["id"],
        "status": properties["status"],
        "tsunami": properties["tsunami"],
        "significance": properties["sig"],
        "stations": properties["nst"],
        "magnitude_type": properties["magType"],
        "depth_km": coordinates[2]
    }
    return details

if __name__== "__main__":
    details = get_earthquake_details("us7000tgb4")
for key, value in details.items():
    print(f"{key}:{value}")
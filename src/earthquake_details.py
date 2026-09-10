import requests

def get_earthquake_details(event_id):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    parameters = {
        "format": "geojson",
        "eventid": event_id
    }
    response= requests.get(url, params=parameters)
    data = response.json()

    print(data.keys())
    print(data["properties"].keys())
    

    properties = data["properties"]
    coordinates = data["geometry"]["coordinates"]

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
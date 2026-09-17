import json
import os
from datetime import datetime
import requests

#Create the data directory exists
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

#USGS summary query parameters
url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
parameters = {
    "format": "geojson",
    "minmagnitude": 2.5,
    "orderby": "time",
    "limit": 10,
}

#Request live API feed
response = requests.get(url, params=parameters)
response.raise_for_status()
data = response.json()

#Generate filename with (YYYY-MM-DD)
today_str = datetime.now().strftime("%Y-%m-%d")
output_path = os.path.join(DATA_DIR, f"{today_str}_earthquakes.json")

#Save the snapshot file using sort_keys=True
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, sort_keys=True)

print(f"Successfully saved {len(data.get('features', []))} events to {output_path}")

#Print summary output to verify contents in the terminal
for feature in data.get("features", []):
    eq_id = feature.get("id")
    props = feature.get("properties", {})
    place = props.get("place")
    mag = props.get("mag")
    event_time = datetime.fromtimestamp(props.get("time", 0) / 1000)
    print(f"ID: {eq_id} | Mag: {mag} | Place: {place} | Time: {event_time}")
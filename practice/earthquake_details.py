from datetime import datetime
import json
import os
import requests

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def get_earthquake_details(event_id):
  """Queries the USGS detail endpoint for a single earthquake ID."""
  parameters = {
      "format": "geojson",
      "eventid": event_id,
  }
  response = requests.get(url, params=parameters)
  response.raise_for_status()
  data = response.json()

  props = data.get("properties", {})
  coords = data.get("geometry", {}).get("coordinates", [])

  return {
      "id": data.get("id"),
      "status": props.get("status"),
      "tsunami": props.get("tsunami"),
      "significance": props.get("sig"),
      "stations": props.get("nst"),
      "magnitude_type": props.get("magType"),
      "depth_km": coords[2] if len(coords) > 2 else None,
  }


# Find earthquake IDs from the summary snapshot in data/
event_ids = []
summary_files = sorted([
    f
    for f in os.listdir(DATA_DIR)
    if f.endswith(".json") and "detail" not in f
])

if summary_files:
  latest_summary = os.path.join(DATA_DIR, summary_files[-1])
  with open(latest_summary, "r", encoding="utf-8") as f:
    summary_data = json.load(f)
    for feat in summary_data.get("features", []):
      event_ids.append(feat.get("id"))
else:
  # Fallback ID for testing if no summary file exists yet
  event_ids = ["tx2026sjbtxd"]

# Fetch detail records for each ID
detail_records = []
for eid in event_ids:
  try:
    details = get_earthquake_details(eid)
    detail_records.append(details)
    print(
        f"Fetched ID: {details['id']} | Sig: {details['significance']} |"
        f" Depth: {details['depth_km']}km | MagType:"
        f" {details['magnitude_type']}"
    )
  except Exception as e:
    print(f"Error fetching event {eid}: {e}")

# Save the details snapshot
today_str = datetime.now().strftime("%Y-%m-%d")
output_path = os.path.join(DATA_DIR, f"{today_str}_earthquake_details.json")

with open(output_path, "w", encoding="utf-8") as f:
  json.dump(detail_records, f, indent=2, sort_keys=True)

print(f"\nSuccessfully saved {len(detail_records)} records to {output_path}")
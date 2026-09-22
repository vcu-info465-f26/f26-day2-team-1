import json
from datetime import datetime
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def get_recent_earthquakes():
    """Fetch the latest earthquake summary list from USGS."""
    parameters = {
        "format": "geojson",
        "minmagnitude": 2.5,
        "orderby": "time",
        "limit": 10,
    }
    response = requests.get(USGS_URL, params=parameters, timeout=30)
    response.raise_for_status()
    return response.json()


def get_earthquake_details(event_id):
    """Fetch selected detail fields for one earthquake."""
    parameters = {"format": "geojson", "eventid": event_id}
    response = requests.get(USGS_URL, params=parameters, timeout=30)
    response.raise_for_status()

    data = response.json()
    properties = data.get("properties", {})
    coordinates = data.get("geometry", {}).get("coordinates", [])
    return {
        "id": data.get("id"),
        "status": properties.get("status"),
        "tsunami": properties.get("tsunami"),
        "significance": properties.get("sig"),
        "stations": properties.get("nst"),
        "magnitude_type": properties.get("magType"),
        "depth_km": coordinates[2] if len(coordinates) > 2 else None,
    }


def save_json(data, filename):
    """Save JSON data in the repository-level data folder."""
    output_path = DATA_DIR / filename
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=True)
    print(f"Saved: {output_path}")


def main():
    today = datetime.now().strftime("%Y-%m-%d")

    # First USGS request: recent-earthquake summary list.
    summary_data = get_recent_earthquakes()
    save_json(summary_data, f"{today}_earthquake_query.json")

    # Detail requests for each earthquake returned in the summary.
    detail_records = []
    for earthquake in summary_data.get("features", []):
        event_id = earthquake.get("id")
        if not event_id:
            print("Skipped an earthquake with no event ID.")
            continue

        try:
            detail_records.append(get_earthquake_details(event_id))
            print(f"Fetched details for {event_id}")
        except requests.RequestException as error:
            print(f"Could not fetch details for {event_id}: {error}")

    save_json(detail_records, f"{today}_earthquake_details.json")
    print(
        f"\nFetch complete: saved one summary snapshot and "
        f"{len(detail_records)} detail records."
    )


if __name__ == "__main__":
    main()

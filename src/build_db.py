import json
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = PROJECT_ROOT / "project.db"


def create_tables(connection):
    # The summary endpoint supplies the parent earthquake records. The detail
    # endpoint supplies one related detail record for each earthquake ID.
    connection.executescript(
        """
        CREATE TABLE earthquakes (
            id TEXT PRIMARY KEY,
            location TEXT,
            magnitude REAL,
            time_ms INTEGER,
            latitude REAL,
            longitude REAL
        );

        CREATE TABLE earthquake_details (
            event_id TEXT PRIMARY KEY,
            status TEXT,
            tsunami INTEGER,
            significance INTEGER,
            stations INTEGER,
            magnitude_type TEXT,
            depth_km REAL,
            FOREIGN KEY (event_id) REFERENCES earthquakes(id)
        );
        """
    )

def load_summary_snapshot(connection, snapshot):
    """Load summary features from one USGS GeoJSON response."""
    for feature in snapshot.get("features", []):
        properties = feature.get("properties", {})
        coordinates = feature.get("geometry", {}).get("coordinates", [])
        # USGS stores coordinates as [longitude, latitude, depth]. Depth is
        # already stored in earthquake_details, so only longitude/latitude go here.
        connection.execute(
            """
            INSERT OR REPLACE INTO earthquakes
                (id, location, magnitude, time_ms, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                feature.get("id"),
                properties.get("place"),
                properties.get("mag"),
                properties.get("time"),
                coordinates[1] if len(coordinates) > 1 else None,
                coordinates[0] if coordinates else None,
            ),
        )


def load_detail_snapshot(connection, records):
    """Load selected event-detail records from one snapshot."""
    for record in records:
        # Older snapshots use "id" while the database schema names this
        # foreign-key column "event_id". Both describe the same USGS event ID.
        event_id = record.get("event_id") or record.get("id")
        connection.execute(
            """
            INSERT OR REPLACE INTO earthquake_details
                (event_id, status, tsunami, significance, stations, magnitude_type, depth_km)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                record.get("status"),
                record.get("tsunami"),
                record.get("significance"),
                record.get("stations"),
                record.get("magnitude_type"),
                record.get("depth_km"),
            ),
        )

def main():
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Data folder not found: {DATA_DIR}")

    # Delete first so every run is a clean rebuild from the committed snapshots.
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    snapshots = sorted(DATA_DIR.glob("*.json"))
    if not snapshots:
        raise FileNotFoundError(f"No JSON snapshots found in {DATA_DIR}")

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        create_tables(connection)

        summary_files = []
        detail_files = []
        # Classify snapshots first: USGS summary files are GeoJSON dictionaries,
        # while our detail files are lists of selected detail records.
        for path in snapshots:
            with open(path, "r", encoding="utf-8") as file:
                snapshot = json.load(file)

            if isinstance(snapshot, dict) and "features" in snapshot:
                summary_files.append(snapshot)
            elif isinstance(snapshot, list):
                detail_files.append(snapshot)
            else:
                print(f"Skipped unrecognized JSON format: {path.name}")

        # Load every parent earthquake first, then child detail records. File names sort
        # "details" before "query", so a single pass would violate the foreign key.
        for snapshot in summary_files:
            load_summary_snapshot(connection, snapshot)
        for snapshot in detail_files:
            load_detail_snapshot(connection, snapshot)

        # These counts are printed so the team can prove a second rebuild does
        # not change the database row totals during the live demo.
        earthquake_count = connection.execute("SELECT COUNT(*) FROM earthquakes").fetchone()[0]
        detail_count = connection.execute("SELECT COUNT(*) FROM earthquake_details").fetchone()[0]
        joined_count = connection.execute(
            """SELECT COUNT(*) FROM earthquakes
               INNER JOIN earthquake_details ON earthquakes.id = earthquake_details.event_id"""
        ).fetchone()[0]

    print(
        f"Rebuilt {DATABASE_PATH.name} from {len(summary_files)} summary and "
        f"{len(detail_files)} detail snapshots."
    )
    print(f"earthquakes: {earthquake_count}")
    print(f"earthquake_details: {detail_count}")
    print(f"joined records: {joined_count}")


if __name__ == "__main__":
    main()
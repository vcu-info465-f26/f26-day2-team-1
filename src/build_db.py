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
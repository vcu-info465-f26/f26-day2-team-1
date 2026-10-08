# This file loads the earthquake data from project.db for the dashboard.

import sqlite3
from pathlib import Path

import pandas as pd


# Find the project folder and then locate project.db.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "project.db"


def load_earthquake_data():
    """
    Join the two database tables and return the data as a dataframe.
    """

    query = """
        SELECT
            e.id,
            e.location,
            e.magnitude,
            e.time_ms,
            e.latitude,
            e.longitude,
            d.depth_km,
            d.significance,
            d.stations,
            d.magnitude_type,
            d.status,
            d.tsunami,

            -- Group the earthquakes based on their depth.
            CASE
                WHEN d.depth_km < 30 THEN 'Shallow (< 30 km)'
                ELSE 'Deep (>= 30 km)'
            END AS depth_group

        FROM earthquakes AS e
        INNER JOIN earthquake_details AS d
            ON e.id = d.event_id

        -- Make sure the data we need is not missing.
        WHERE e.time_ms IS NOT NULL
          AND e.magnitude IS NOT NULL
          AND d.depth_km IS NOT NULL
          AND d.significance IS NOT NULL

        -- Put the earthquakes in order by when they happened.
        ORDER BY e.time_ms
    """

    # we run the query and store the results in a dataframe
    with sqlite3.connect(DATABASE_PATH) as connection:
        dataframe = pd.read_sql_query(query, connection)

    # USGS stores time as milliseconds, so we convert it to a readable date and time
    dataframe["event_time"] = pd.to_datetime(
        dataframe["time_ms"],
        unit="ms",
        utc=True,
    )

    return dataframe


def filter_by_magnitude(dataframe, magnitude_range):
    """
    Keep the earthquakes that fall within the magnitude range selected in the sidebar.
    """

    minimum, maximum = magnitude_range

    # Return only earthquakes within the selected magnitude range
    return dataframe[dataframe["magnitude"].between(minimum, maximum)].copy()
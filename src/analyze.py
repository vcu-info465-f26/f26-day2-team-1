"""# This file connects to the weather database and finds the highest temperature in the forecast data.
# The get_max() function returns a pandas DataFrame containing the day and maximum high temperature.
# The query selects the day along with the maximum temperature, which is not obvious because it does not explicitly match the day to the maximum value."""

import sqlite3
from pathlib import Path

import pandas as pd
DB_PATH = Path("output") / "weather.db"
def get_max():
    conn = sqlite3.connect(DB_PATH)
    hottest = pd.read_sql_query(
            "SELECT day, max(high) FROM forecast ", conn
        )
    conn.close()
    return hottest
if __name__=="__main__":
    print(get_max())
# Prepares filtered statistics and looks up extra details only when needed.

from contextlib import closing
from datetime import datetime, timezone
import json
import sqlite3
from time import monotonic

import pandas as pd


# These are the columns visitors can see in the dashboard's dataframe.
DATAFRAME_COLUMNS = {
    "event_time": "UTC event timestamp; use date(event_time) for a calendar day",
    "location": "Exact USGS location label; may be missing",
    "magnitude": "Earthquake magnitude (number)",
    "depth_km": "Depth in kilometers (number)",
    "significance": "USGS significance score (number)",
    "depth_group": "Shallow (< 30 km) or Deep (>= 30 km)",
    "status": "USGS review status; may be missing",
}


def query_dataframe(dataframe, sql):
    """Calculate an answer locally without sending the full dataframe to Groq."""
    if not isinstance(sql, str) or not sql.strip() or len(sql) > 6000:
        raise ValueError("Use a single short SELECT query.")

    # Work on a temporary copy of only the displayed, currently filtered data.
    # This never opens project.db or gives the model access to other files.
    table = dataframe[list(DATAFRAME_COLUMNS)].copy()
    table["event_time"] = table["event_time"].map(
        lambda value: value.isoformat() if not pd.isna(value) else None
    )
    with closing(sqlite3.connect(":memory:")) as connection:
        table.to_sql("earthquake_data", connection, index=False)
        connection.execute("PRAGMA query_only = ON")

        # The model writes the query, so allow reading this table and ordinary
        # calculations only. Changes, other tables, and file functions are denied.
        safe_functions = {
            "count", "sum", "avg", "min", "max", "round", "abs", "total",
            "lower", "upper", "trim", "ltrim", "rtrim", "substr", "substring",
            "instr", "length", "replace", "coalesce", "ifnull", "nullif",
            "date", "datetime", "time", "strftime", "julianday", "unixepoch",
            "typeof", "like", "glob", "row_number", "rank", "dense_rank",
        }

        def authorize(action, table_name, column_or_function, database, source):
            if action == sqlite3.SQLITE_SELECT:
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_READ and table_name == "earthquake_data":
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_FUNCTION and column_or_function in safe_functions:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        connection.set_authorizer(authorize)
        connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 16000)
        connection.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, 6000)
        connection.setlimit(sqlite3.SQLITE_LIMIT_COLUMN, 20)
        connection.setlimit(sqlite3.SQLITE_LIMIT_EXPR_DEPTH, 50)
        deadline = monotonic() + 2
        connection.set_progress_handler(lambda: int(monotonic() > deadline), 1000)

        cursor = connection.execute(sql)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchmany(21)

        # Calculations use every matching row, but only a small result is sent.
        # Tell the model if we leave rows out so it cannot mistake them for a total.
        result = {"columns": columns, "rows": [], "truncated": len(rows) > 20}
        if len(json.dumps(result, allow_nan=False)) > 8000:
            raise ValueError("Return fewer columns with shorter names.")
        for row in rows[:20]:
            result["rows"].append(list(row))
            if len(json.dumps(result, allow_nan=False)) > 8000:
                result["rows"].pop()
                result["truncated"] = True
                break
        return result


def build_chat_context(dataframe, magnitude_range, review_status):
    """Describe the current filters, chart statistics, and queryable columns."""
    # app.py has already applied both filters to this dataframe. Use those rows
    # directly so the chat and charts do not accidentally describe different data.
    # Today's date gives the model a reference for questions like "this week."
    context = {
        "today_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "filters": {
            "minimum_magnitude": float(magnitude_range[0]),
            "maximum_magnitude": float(magnitude_range[1]),
            "review_status": review_status,
        },
        "earthquake_count": len(dataframe),
        "depth_groups": [],
        "magnitude_chart_days": [],
        "queryable_table": "earthquake_data",
        "dataframe_columns": DATAFRAME_COLUMNS,
        "chart_scope": (
            "The bar chart and dataframe use all filtered earthquakes. "
            "The magnitude chart shows only the latest 15 event dates with data. "
            "All dates are UTC. These are collected snapshots, not a complete "
            "worldwide earthquake catalog."
        ),
    }

    # Return the filter details and zero count without trying to average empty data.
    if dataframe.empty:
        return context

    # These describe all matching rows, even if some dates are older than the
    # magnitude chart's 15-date window.
    context["start_date"] = dataframe["event_time"].min().strftime("%Y-%m-%d")
    context["end_date"] = dataframe["event_time"].max().strftime("%Y-%m-%d")
    context["highest_magnitude"] = float(dataframe["magnitude"].max())
    context["highest_significance"] = int(dataframe["significance"].max())

    # Uses the same averages and counts as the significance bar chart.
    comparison = dataframe.groupby("depth_group").agg(
        earthquake_count=("id", "count"),
        average_magnitude=("magnitude", "mean"),
        average_significance=("significance", "mean"),
    )
    for depth_group, row in comparison.iterrows():
        # Convert pandas values to regular Python numbers for JSON. Round the
        # averages to two decimal places, matching the values inside the bars.
        context["depth_groups"].append(
            {
                "depth_group": depth_group,
                "earthquake_count": int(row["earthquake_count"]),
                "average_magnitude": round(float(row["average_magnitude"]), 2),
                "average_significance": round(float(row["average_significance"]), 2),
            }
        )

    # Do the calculations here instead of asking the model to work through every
    # earthquake row. Sending a small table also helps stay within Groq's limits.
    # Sort the dates and keep the latest 15 with data, just like the magnitude chart.
    daily = dataframe.groupby(dataframe["event_time"].dt.strftime("%Y-%m-%d")).agg(
        earthquake_count=("id", "count"),
        highest_magnitude=("magnitude", "max"),
        average_magnitude=("magnitude", "mean"),
        average_significance=("significance", "mean"),
        highest_significance=("significance", "max"),
    ).sort_index().tail(15)

    for date, row in daily.iterrows():
        # Each entry describes one visible date, so the chat can compare days
        # without assuming there were earthquakes on dates we did not collect.
        context["magnitude_chart_days"].append(
            {
                "date": date,
                "earthquake_count": int(row["earthquake_count"]),
                "highest_magnitude": float(row["highest_magnitude"]),
                "average_magnitude": round(float(row["average_magnitude"]), 2),
                "average_significance": round(float(row["average_significance"]), 2),
                "highest_significance": int(row["highest_significance"]),
            }
        )

    return context

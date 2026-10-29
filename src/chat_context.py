# Calculates the filtered statistics supplied to the dashboard chat.

from datetime import datetime, timezone


def build_chat_context(dataframe, magnitude_range, review_status):
    """Describe the current filters and the data used by the charts."""
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
# Creates a graph showing earthquake magnitude over time

import plotly.express as px


def make_time_plot(dataframe):
    """
    Create a scatter plot of earthquake magnitude over time.
    Each point is an earthquake. Color shows whether it was shallow or deep.
    """
    # Uses earthquake data to make a scatter plot
    figure = px.scatter(
        dataframe,
        # Plot date/time on x-axis, magnitude on y-axis
        x="event_time",
        y="magnitude",
        # Separates shallow/deep earthquakes based on color
        color="depth_group",
        # Shows earthquake location when hovering over a point
        hover_name="location",

        # Extra information appears when a user hovers over a point.
        hover_data={
            "event_time": "|%b %d, %Y %H:%M UTC",
            "depth_km": ":.1f",
            "significance": True,
            "magnitude": ":.2f",
        },

        # Clear labels make the chart understandable without an explanation.
        labels={
            "event_time": "Earthquake event time",
            "magnitude": "Magnitude",
            "depth_group": "Depth group",
        },

        title="Earthquake Magnitude Over Time",
    )
    # Labels the legend so that users know what each color represents 
    figure.update_layout(legend_title_text="Depth group")
    return figure
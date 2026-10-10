# Creates a graph showing earthquake magnitude over time

import plotly.express as px


def make_time_plot(dataframe):
    """
    Create a scatter plot of earthquake magnitude over time.
    Each point is an earthquake. Color shows whether it was shallow or deep.
    """
    # Use calendar dates as ordered categories so only dates with data appear,
    # with equal spacing regardless of the number of days between events.
    plot_data = dataframe.copy()
    # Show the most recent 15 dates with data, retaining every event on them.
    event_dates = sorted(plot_data["event_time"].dt.normalize().unique())[-15:]
    date_ticks = [date.strftime("%Y-%m-%d") for date in event_dates]
    plot_data["event_date"] = plot_data["event_time"].dt.strftime("%Y-%m-%d")
    plot_data = plot_data[plot_data["event_date"].isin(date_ticks)]

    # Uses earthquake data to make a scatter plot.
    figure = px.scatter(
        plot_data,
        # Plot the calendar date on x-axis, magnitude on y-axis.
        x="event_date",
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
            "event_date": "Earthquake Date",
            "magnitude": "Magnitude",
            "depth_group": "Depth group",
        },

        title="Earthquake Magnitude Over Time",
    )
    # The shared depth key in app.py explains the colors for every chart.
    figure.update_layout(
        showlegend=False,
        font=dict(size=19),
        title_font=dict(size=25),
        hoverlabel=dict(font_size=18),
    )
    figure.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=date_ticks,
        tickfont=dict(size=15),
        title_font=dict(size=20),
        tickmode="array",
        tickvals=date_ticks,
        ticktext=[f"{date.strftime('%b')}<br>{date.day}" for date in event_dates],
    )
    # Leave breathing room above the highest visible earthquake magnitude.
    highest_magnitude = float(plot_data["magnitude"].max())
    lowest_magnitude = float(plot_data["magnitude"].min())
    magnitude_span = max(highest_magnitude - lowest_magnitude, 1.0)
    figure.update_yaxes(
        tickfont=dict(size=17),
        title_font=dict(size=20),
        range=[lowest_magnitude - magnitude_span * 0.1,
               highest_magnitude + magnitude_span * 0.2],
    )
    return figure

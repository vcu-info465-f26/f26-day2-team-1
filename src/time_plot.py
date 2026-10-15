# Creates a graph showing earthquake magnitude over time.

import plotly.express as px


def make_time_plot(dataframe):
    """
    Create a scatter plot of earthquake magnitude by event date.
    Each point is an earthquake. Color represents its depth group.
    """

    plot_data = dataframe.copy()

    # Keep the latest 15 dates with data and every earthquake on those dates.
    event_dates = sorted(
        plot_data["event_time"].dt.normalize().unique()
    )[-15:]

    date_ticks = [
        date.strftime("%Y-%m-%d")
        for date in event_dates
    ]

    plot_data["event_date"] = plot_data["event_time"].dt.strftime("%Y-%m-%d")
    plot_data = plot_data[
        plot_data["event_date"].isin(date_ticks)
    ]

    figure = px.scatter(
        plot_data,
        x="event_date",
        y="magnitude",
        color="depth_group",
        color_discrete_map={
            "Shallow (< 30 km)": "#7EC8FF",
            "Deep (>= 30 km)": "#1673D1",
        },
        hover_name="location",
        hover_data={
            "event_time": "|%b %d, %Y %H:%M UTC",
            "depth_km": ":.1f",
            "significance": True,
            "magnitude": ":.2f",
        },
        labels={
            "event_date": "Earthquake Date",
            "magnitude": "Magnitude",
            "depth_group": "Depth group",
        },
        title="Earthquake Magnitude Over Time",
    )

    figure.update_layout(
        showlegend=False,
        font=dict(size=19),
        title_font=dict(size=25),
        hoverlabel=dict(font_size=18),
    )

    # Treat dates as chronological categories to give them equal spacing.
    # This spacing represents event dates, rather than elapsed time.
    figure.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=date_ticks,
        tickfont=dict(size=15),
        title_font=dict(size=20),
        tickmode="array",
        tickvals=date_ticks,
        ticktext=[
            f"{date.strftime('%b')}<br>{date.day}"
            for date in event_dates
        ],
    )

    # Leave breathing room above and below the plotted magnitudes.
    highest_magnitude = float(plot_data["magnitude"].max())
    lowest_magnitude = float(plot_data["magnitude"].min())
    magnitude_span = max(highest_magnitude - lowest_magnitude, 1.0)

    figure.update_yaxes(
        tickfont=dict(size=17),
        title_font=dict(size=20),
        range=[
            lowest_magnitude - magnitude_span * 0.1,
            highest_magnitude + magnitude_span * 0.2,
        ],
    )

    return figure
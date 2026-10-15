# This file creates an interactive earthquake location map.

import plotly.express as px


def make_map(dataframe):
    """
    Create a full-width interactive map.

    Marker size represents magnitude.
    Marker color represents shallow versus deep earthquakes.
    """

    figure = px.scatter_map(
        dataframe,

        # Latitude and longitude place earthquakes on the map.
        lat="latitude",
        lon="longitude",

        # Marker size represents earthquake magnitude.
        size="magnitude",
        size_max=28,

        # Marker color separates shallow and deep earthquakes.
        color="depth_group",

        # Location is the main hover label.
        hover_name="location",

        # information displayed when hovering
        hover_data={
            "magnitude": ":.2f",
            "depth_km": ":.1f",
            "significance": True,
            "event_time": "|%b %d, %Y %H:%M UTC",
            "latitude": False,
            "longitude": False,
        },

        labels={
            "depth_group": "Depth group",
            "magnitude": "Magnitude",
            "depth_km": "Depth (km)",
            "significance": "USGS significance",
            "event_time": "Event time",
        },

        # map style
        map_style="carto-darkmatter",

        # map centering
        zoom=1.55,
        center={"lat": 20, "lon": 0},

        title="Locations of Earthquakes",
    )

    # map sizing
    figure.update_layout(
        height=520,
        margin={"r": 0, "t": 55, "l": 0, "b": 0},
        showlegend=False,
        font=dict(size=19),
        title_font=dict(size=25),
        hoverlabel=dict(font_size=18),
    )
    return figure
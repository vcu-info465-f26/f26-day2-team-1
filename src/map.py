# Creates an interactive earthquake location map.

import plotly.express as px


def make_map(dataframe):
    """
    Create a full-width interactive map.
    Marker size represents magnitude.
    Marker color represents depth group.
    """

    figure = px.scatter_map(
        dataframe,

        # Place earthquakes using their actual coordinates.
        lat="latitude",
        lon="longitude",

        # Larger markers represent larger magnitudes.
        size="magnitude",
        size_max=28,

        # Keep depth colors consistent with the other charts and shared key.
        color="depth_group",
        color_discrete_map={
            "Shallow (< 30 km)": "#7EC8FF",
            "Deep (>= 30 km)": "#1673D1",
        },

        hover_name="location",
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

        # Dark map tiles that do not require an API key.
        map_style="carto-darkmatter",

        # Set the initial map view.
        zoom=1.55,
        center={"lat": 20, "lon": 0},

        title="Locations of Earthquakes",
    )

    figure.update_layout(
        height=520,
        margin={"r": 0, "t": 55, "l": 0, "b": 0},
        showlegend=False,
        font=dict(size=19),
        title_font=dict(size=25),
        hoverlabel=dict(font_size=18),
    )

    return figure
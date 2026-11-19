# Creates an interactive earthquake location map.

from math import sqrt

import plotly.express as px
import requests
import streamlit as st


# Pin the public dataset version so the team uses the same mapped faults.
FAULT_DATA_URL = (
    "https://raw.githubusercontent.com/GEMScienceTools/gem-global-active-faults/"
    "56816508ad92fd6846dad1163b1c8c01376a2cd1/geojson/gem_active_faults.geojson"
)


@st.cache_data(ttl=86400, show_spinner=False)
def load_fault_lines():
    """Download once per day, keeping only the geometry needed for the overlay."""
    response = requests.get(FAULT_DATA_URL, timeout=15)
    response.raise_for_status()
    faults = response.json()
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "geometry": feature["geometry"], "properties": {}}
            for feature in faults["features"]
            if feature["geometry"]["type"] in ("LineString", "MultiLineString")
        ],
    }


def make_map(dataframe):
    """
    Create a full-width interactive map.
    Marker size represents magnitude and grows as the visitor zooms in.
    Marker color represents depth group.
    """

    # Native map layers can resize circles smoothly in the browser as zoom changes.
    # Only filtered events with usable coordinates belong in the point layer.
    map_data = dataframe.dropna(subset=["latitude", "longitude", "magnitude"])
    maximum_magnitude = (
        max(float(map_data["magnitude"].max()), 0.1) if not map_data.empty else 1
    )
    events = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row.longitude), float(row.latitude)],
                },
                "properties": {
                    "depth_group": row.depth_group,
                    # Area still represents magnitude at every zoom level.
                    "radius_scale": sqrt(max(float(row.magnitude), 0) / maximum_magnitude),
                },
            }
            for row in map_data.itertuples(index=False)
        ],
    }
    style = {
        "version": 8,
        "sources": {
            "basemap": {
                "type": "raster",
                "tiles": [
                    "https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/"
                    "World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
                ],
                "tileSize": 256,
                "attribution": (
                    'Esri, HERE, Garmin, &copy; OpenStreetMap contributors, '
                    'and the GIS user community'
                ),
            },
            "earthquakes": {"type": "geojson", "data": events},
        },
        "layers": [
            {"id": "basemap", "type": "raster", "source": "basemap"},
        ],
    }

    try:
        style["sources"]["faults"] = {
            "type": "geojson",
            "data": load_fault_lines(),
            "attribution": (
                'Faults: <a href="https://github.com/GEMScienceTools/gem-global-active-faults">'
                'GEM GAF-DB, Styron &amp; Pagani (2020)</a>, '
                '<a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>'
            ),
        }
        style["layers"].append({
            "id": "active-faults", "type": "line", "source": "faults",
            "paint": {
                "line-color": "#DDA15E",
                "line-width": ["interpolate", ["linear"], ["zoom"], 0, 0.5, 6, 1.2, 12, 1.8],
                "line-opacity": 0.6,
            },
        })
        fault_note = "Orange lines: mapped active faults · GEM GAF-DB (CC BY-SA 4.0). Coverage varies."
    except (requests.RequestException, ValueError, KeyError, TypeError):
        # A fault-data outage must not stop the earthquake map from working.
        fault_note = "Fault lines are unavailable right now. Earthquake events are still shown."

    style["layers"].append({
        "id": "earthquake-circles", "type": "circle", "source": "earthquakes",
        "paint": {
            "circle-color": [
                "match", ["get", "depth_group"],
                "Shallow (< 30 km)", "#7EC8FF", "#1673D1",
            ],
            # Interpolate in the browser; zooming makes no Groq calls or app reruns.
            # Keep dots visible at world scale and grow them more at closer views.
            "circle-radius": [
                "interpolate", ["linear"], ["zoom"],
                0, ["*", 4, ["get", "radius_scale"]],
                2, ["*", 8, ["get", "radius_scale"]],
                4, ["*", 14, ["get", "radius_scale"]],
                6, ["*", 22, ["get", "radius_scale"]],
                12, ["*", 36, ["get", "radius_scale"]],
            ],
            "circle-opacity": 0.9,
            "circle-stroke-color": "#0E1117",
            "circle-stroke-width": 0.5,
        },
    })

    figure = px.scatter_map(
        map_data,

        # Place earthquakes using their actual coordinates.
        lat="latitude",
        lon="longitude",

        # Larger markers represent larger magnitudes.
        size="magnitude",
        size_max=12,

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
        map_style=style,

        # Set the initial map view.
        zoom=1.55,
        center={"lat": 20, "lon": 0},

        title="Locations of Earthquakes",
    )

    # Keep Plotly's existing event hover details. The native circle layer above
    # draws the visible dots, so these fixed-size Plotly markers stay transparent.
    figure.update_traces(marker_opacity=0)
    figure.update_layout(
        height=760,
        margin={"r": 0, "t": 55, "l": 0, "b": 35},
        showlegend=False,
        font=dict(size=19),
        title_font=dict(size=25),
        hoverlabel=dict(font_size=18),
    )
    figure.add_annotation(
        text=fault_note,
        x=0, y=0, xref="paper", yref="paper", xanchor="left", yanchor="top",
        yshift=-8, showarrow=False, font=dict(size=12, color="#B6BBC4"),
    )

    return figure

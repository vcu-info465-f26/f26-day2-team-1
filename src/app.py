# Streamlit dashboard.
# Imports the other functions and puts everything onto one page.

import streamlit as st

# build_db.py turns committed JSON snapshots in data/ into project.db.
from build_db import main as rebuild_database

# Functions come from the other dashboard modules.
from comparison_plot import make_comparison_plot
from data_queries import filter_by_magnitude, load_earthquake_data
from time_plot import make_time_plot


# Configure browser title and allow the dashboard to use page width.
st.set_page_config(page_title="Earthquake Dashboard", layout="wide")


@st.cache_resource
def build_dashboard_database():
    """
    Build project.db once per Streamlit app session.

    project.db is ignored by Git, so the dashboard creates it locally from
    the committed JSON snapshots in data/ whenever the app starts.
    """
    rebuild_database()


@st.cache_data
def get_dashboard_data():
    """
    Load and cache the dataframe so Streamlit does not re-query the database
    every time a visitor changes the sidebar filter.
    """
    return load_earthquake_data()


# Check the database exists, then load the dashboard data.
build_dashboard_database()
dataframe = get_dashboard_data()

# Dashboard heading and explanation.
st.title("Earthquake Depth and Significance Dashboard")
st.write(
    "Explore how earthquake magnitude, depth, and USGS significance appear in "
    "our collected USGS earthquake snapshots."
)

# Find the data's real minimum and maximum magnitudes.
minimum_magnitude = float(dataframe["magnitude"].min())
maximum_magnitude = float(dataframe["magnitude"].max())

# Slider lets visitors choose magnitude range.
selected_range = st.sidebar.slider(
    "Magnitude range",
    min_value=minimum_magnitude,
    max_value=maximum_magnitude,
    value=(minimum_magnitude, maximum_magnitude),
)

# Filter the dataframe before giving it to the plots and table.
filtered_dataframe = filter_by_magnitude(dataframe, selected_range)

# Avoid error if the visitor chooses a range with no matching earthquakes.
if filtered_dataframe.empty:
    st.warning("No earthquakes match the selected magnitude range.")
else:
    # Put the two charts next to each other.
    left_column, right_column = st.columns(2)

    with left_column:
        st.plotly_chart(
            make_time_plot(filtered_dataframe),
            use_container_width=True,
        )

    with right_column:
        st.plotly_chart(
            make_comparison_plot(filtered_dataframe),
            use_container_width=True,
        )

    # Show the records behind the charts.
    st.subheader("Underlying earthquake data")
    displayed_columns = [
        "event_time",
        "location",
        "magnitude",
        "depth_km",
        "significance",
        "depth_group",
        "status",
    ]

    st.dataframe(
        filtered_dataframe[displayed_columns],
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "Data source: USGS Earthquake Catalog API. "
    "Data is built from committed snapshots in data/."
)
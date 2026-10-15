# Streamlit dashboard entry point.
# This file imports the chart and data functions, then displays them together.

import streamlit as st

# build_db.py turns committed JSON snapshots in data/ into project.db.
from build_db import main as rebuild_database

# Import dashboard modules.
from comparison_plot import make_comparison_plot
from data_queries import filter_by_magnitude, load_earthquake_data
from map_plot import make_map
from time_plot import make_time_plot


# Configure the browser tab title and use the full page width.
st.set_page_config(page_title="Earthquake Dashboard", layout="wide")

# Make regular page text, sidebar controls, and the displayed table easier to read.
st.markdown(
    """
    <style>
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] li,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] .stCaption {
            font-size: 1.2rem !important;
        }

        [data-testid="stSidebar"] {
            font-size: 1.2rem;
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p {
            font-size: 1.2rem !important;
        }

        /* Move the values and rail together below the widget label. */
        [data-testid="stSidebar"] [data-testid="stSlider"] > [role="group"] {
            padding-top: 24px !important;
        }

        [data-testid="stSidebar"] [data-testid="stSliderThumbValue"] {
            transform: translateY(-8px);
        }

        [data-testid="stDataFrame"] {
            font-size: 1.1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def build_dashboard_database():
    """
    Build project.db once per app session.

    project.db is ignored by Git, so this creates it locally from the
    committed JSON snapshots in data/.
    """
    rebuild_database()


@st.cache_data
def get_dashboard_data():
    """
    Load and cache the dataframe so the database is not queried again
    every time a visitor changes the sidebar filter.
    """
    return load_earthquake_data()


# Build the database, then load the dashboard dataframe.
build_dashboard_database()
dataframe = get_dashboard_data()

# Dashboard heading and introduction.
st.title("Earthquake Depth and Significance Dashboard")
st.write(
    "Explore how earthquake magnitude, depth, and USGS significance appear in "
    "our collected USGS earthquake snapshots."
)

# One readable, shared key for every visualization on the page.
st.markdown(
    """
    <div class="depth-key">
        <strong>Depth Key:</strong>
        <span class="shallow-dot">●</span> <strong>Shallow:</strong> &lt; 30 km deep
        <span class="deep-dot">●</span> <strong>Deep:</strong> ≥ 30 km deep
    </div>
    <style>
        .depth-key { font-size: 1.2rem; margin-bottom: 1rem; }
        .shallow-dot, .deep-dot {
            font-size: 1.35rem;
            vertical-align: -0.08em;
            margin-left: 1rem;
        }
        .shallow-dot { color: #7EC8FF; }
        .deep-dot { color: #1673D1; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Get the minimum and maximum magnitudes in the real data.
minimum_magnitude = float(dataframe["magnitude"].min())
maximum_magnitude = float(dataframe["magnitude"].max())

# Sidebar slider filters earthquakes by a selected magnitude range.
selected_range = st.sidebar.slider(
    "Magnitude Range",
    min_value=minimum_magnitude,
    max_value=maximum_magnitude,
    value=(minimum_magnitude, maximum_magnitude),
)

# Apply the selected magnitude range to all visualizations and the dataframe.
filtered_dataframe = filter_by_magnitude(dataframe, selected_range)
selected_status = st.sidebar.selectbox(
    "USGS Review Status",
    ["All", "Reviewed", "Automatic"],
)

if selected_status != "All":
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe["status"].str.lower() == selected_status.lower()
    ]

# Prevent errors when a filter produces no matching earthquakes.
if filtered_dataframe.empty:
    st.warning("No earthquakes match the selected magnitude range.")

else:
    # Put the first two charts beside each other with a clear visual gap.
    left_column, right_column = st.columns(2, gap="large")

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

    # Show the map below both charts across the full page width.
    st.plotly_chart(
        make_map(filtered_dataframe),
        use_container_width=True,
    )

    # Show the actual data records behind the visualizations.
    st.subheader("Earthquake Dataframe")

    displayed_columns = [
        "event_time",
        "location",
        "magnitude",
        "depth_km",
        "significance",
        "depth_group",
        "status",
    ]

    # Convert only the table's numeric values to text so they are left-aligned.
    # The original numeric dataframe is still used by all filters and charts.
    displayed_dataframe = filtered_dataframe[displayed_columns].copy()
    for column in ["magnitude", "depth_km", "significance"]:
        displayed_dataframe[column] = displayed_dataframe[column].map(
            lambda value: f"{value:g}"
        )

    st.dataframe(
        displayed_dataframe,
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "Data source: USGS Earthquake Catalog API. "
    "Data is built from committed snapshots in data/."
)

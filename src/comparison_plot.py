
import plotly.express as px


def make_comparison_plot(dataframe):
    """Compare average earthquake significance by depth."""

    # Get the average significance and earthquake count for each group.
    comparison = (
        dataframe.groupby("depth_group", as_index=False)
        .agg(
            average_significance=("significance", "mean"),
            earthquake_count=("id", "count"),
        )
    )

    # Create the chart comparing shallow and deep earthquakes.
    figure = px.bar(
        comparison,
        x="depth_group",
        y="average_significance",
        color="depth_group",
        text="earthquake_count",
        labels={
            "depth_group": "Depth group",
            "average_significance": "Average USGS significance",
            "earthquake_count": "Earthquake count",
        },
        title="Average USGS Significance by Earthquake Depth",
    )

    # Display the earthquake count above each bar.
    figure.update_traces(texttemplate="n=%{text}", textposition="outside")
    figure.update_layout(showlegend=False)

    return figure

import plotly.express as px


def make_comparison_plot(dataframe):
    """Compare average earthquake significance by depth."""

    # Calculate the average significance and event count for each group.
    comparison = (
        dataframe.groupby("depth_group", as_index=False)
        .agg(
            average_significance=("significance", "mean"),
            earthquake_count=("id", "count"),
        )
    )

    figure = px.bar(
        comparison,
        x="depth_group",
        y="average_significance",
        color="depth_group",
        color_discrete_map={
            "Shallow (< 30 km)": "#7EC8FF",
            "Deep (>= 30 km)": "#1673D1",
        },
        text="earthquake_count",
        labels={
            "depth_group": "Depth Group",
            "average_significance": "Significance",
            "earthquake_count": "Earthquake count",
        },
        title="Average USGS Significance by Earthquake Depth",
    )

    # Keep earthquake counts above each bar.
    figure.update_traces(
        texttemplate="n=%{text}",
        textposition="outside",
    )

    # Display each average inside its bar with a black drop shadow.
    for row in comparison.itertuples(index=False):
        figure.add_annotation(
            x=row.depth_group,
            y=row.average_significance / 2,
            text=f"{row.average_significance:.2f}",
            showarrow=False,
            xanchor="center",
            yanchor="middle",
            font=dict(
                size=34,
                color="white",
                weight=700,
                shadow="2px 2px 4px black",
            ),
        )

    figure.update_layout(
        showlegend=False,
        bargap=0.55,
        font=dict(size=19),
        title_font=dict(size=25),
        hoverlabel=dict(font_size=18),
    )

    figure.update_xaxes(
        tickfont=dict(size=17),
        title_font=dict(size=20),
    )

    # Start at zero and leave 33% headroom above the tallest bar.
    highest_significance = float(comparison["average_significance"].max())

    figure.update_yaxes(
        tickfont=dict(size=17),
        title_font=dict(size=20),
        range=[0, max(highest_significance * 1.33, 1.0)],
    )

    return figure
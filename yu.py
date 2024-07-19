positions = ["overweight", "underweight", "benchmark"]
colors = {"overweight": "mediumseagreen", "underweight": "mediumvioletred", "benchmark": "gray"}

# Create traces for overweight and underweight
for position in positions:
    df_filtered = big_df2[big_df2["Position"] == position]

    graph_trace = px.scatter(
        df_filtered,
        x="Years to Maturity",
        y=column,
        size="Size",
        hover_name="Description",
        hover_data=["CUSIP", "Position"],
        color="Position",
        color_discrete_map={
            "underweight": "mediumvioletred",
            "overweight": "mediumseagreen",
            "benchmark": "gray",
        },
        symbol="Original series",
        symbol_map=symbols_dict,
    )

    for i, trace in enumerate(graph_trace.data):
        trace.name = position.capitalize()
        trace.legendgroup = position
        if i == 0:
            trace.showlegend = False
        else:
            trace.showlegend = False

        fig.add_trace(trace)

    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        name=position.capitalize(),
        legendgroup=position,
        marker=dict(
            size=10,
            symbol='circle',
            color=colors[position],
        ),
        showlegend=True
    ))

# Create traces for each maturity
for maturity in symbols_dict.keys():
    df_filtered = big_df2[big_df2["Original series"] == maturity]

    graph_trace = px.scatter(
        df_filtered,
        x="Years to Maturity",
        y=column,
        size="Size",
        hover_name="Description",
        hover_data=["CUSIP", "Position"],
        color="Position",
        color_discrete_map={
            "underweight": "mediumvioletred",
            "overweight": "mediumseagreen",
            "benchmark": "gray",
        },
        symbol="Original series",
        symbol_map=symbols_dict,
    )

    for trace in graph_trace.data:
        trace.showlegend = False
        trace.legendgroup = maturity
        fig.add_trace(trace)

    # Add black legend item for maturity
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        name=maturity,
        legendgroup=maturity,
        marker=dict(
            size=10,
            symbol=symbols_dict[maturity],
            color='black'
        ),
        showlegend=True,
        hoverinfo='none'
    ))



    fig.update_layout(
    xaxis=dict(title=dict(text="Years to Maturity", font=dict(size=20))),
    yaxis=dict(title=dict(text=y_title, font=dict(size=20))),
    height=500,
    title="Run Date: %s" % date,
    legend=dict(
        itemsizing="constant",
        font=dict(size=18),
        orientation="v",
        yanchor="top",
        xanchor="left",
        x=1.02,
        y=1,
        groupclick="toggleitem",
        itemclick="toggleothers",
        itemdoubleclick="toggle"
    ),
    hoverlabel_font_color="white"
)
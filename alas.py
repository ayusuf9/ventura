# Create a single scatter plot for all data points
graph_trace = px.scatter(
    big_df2,
    x="Years to Maturity",
    y=column,
    size="sizes",
    hover_name="Description",
    hover_data=["CUSIP", "Position", "Original series"],
    color="Position",
    color_discrete_map={
        "underweight": "mediumvioletred",
        "overweight": "mediumseagreen",
        "benchmark": "gray",
    },
    symbol="Original series",
    symbol_map=symbols_dict,
)

# Add all traces to the figure
for trace in graph_trace.data:
    fig.add_trace(trace)

# Create legend entries for overweight and underweight
for position in ["overweight", "underweight"]:
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        name=position.capitalize(),
        legendgroup=position,
        marker=dict(
            color={"overweight": "mediumseagreen", "underweight": "mediumvioletred"}[position],
            size=10
        ),
        showlegend=True
    ))

# Create legend entries for maturities
for maturity in symbols_dict.keys():
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

# Update traces to match legend groups
for trace in fig.data:
    if trace.name in ["Overweight", "Underweight"]:
        trace.legendgroup = trace.name.lower()
    elif trace.name in symbols_dict.keys():
        trace.legendgroup = trace.name
    else:
        trace.showlegend = False

# Update layout
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

fig.update_xaxes(range=[0, 30.05])
if column == "Fed Hold %":
    fig.update_yaxes(range=[-5, 75])
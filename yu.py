# Create legend traces for each position
positions = ["overweight", "underweight", "benchmark"]
colors = {"overweight": "mediumseagreen", "underweight": "mediumvioletred", "benchmark": "gray"}

for position in positions:
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
        showlegend=True,
        hoverinfo='none'
    ))

# Create legend traces for each maturity
for maturity in symbols_dict.keys():
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        name=maturity,
        marker=dict(
            size=10,
            symbol=symbols_dict[maturity],
            color='black'
        ),
        showlegend=True,
        hoverinfo='none'
    ))
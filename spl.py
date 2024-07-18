def simplify_legend(fig):
    # Define the new legend items
    new_legend_items = [
        {"name": "overweight", "color": "mediumseagreen", "symbol": "circle"},
        {"name": "underweight", "color": "mediumvioletred", "symbol": "circle"},
        {"name": "2Y", "color": "black", "symbol": "circle"},
        {"name": "3Y", "color": "black", "symbol": "square"},
        {"name": "5Y", "color": "black", "symbol": "diamond"},
        {"name": "7Y", "color": "black", "symbol": "cross"},
        {"name": "10Y", "color": "black", "symbol": "x"},
        {"name": "20Y", "color": "black", "symbol": "star"},
        {"name": "30Y", "color": "black", "symbol": "bowtie"},
    ]

    # Hide all existing traces in the legend
    for trace in fig.data:
        trace.showlegend = False

    # Add new traces for the compressed legend
    for item in new_legend_items:
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(
                size=10,
                color=item["color"],
                symbol=item["symbol"],
            ),
            name=item["name"],
            legendgroup=item["name"],
            showlegend=True
        ))

    return fig

# After creating your figure, apply the simplified legend
fig = simplify_legend(fig)

# Update the layout to position the legend and ensure it's horizontal
fig.update_layout(
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
        itemsizing='constant',
        itemclick="toggleothers",
        itemdoubleclick="toggle"
    )
)
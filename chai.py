def create_compressed_figure(big_df2, column, symbols_dict):
    color_map = {
        'overweight': 'mediumseagreen',
        'underweight': 'mediumvioletred',
        'benchmark': 'gray'
    }

    fig = go.Figure()

    # Create traces for data points
    for position in color_map.keys():
        for maturity, symbol in symbols_dict.items():
            df_filtered = big_df2[(big_df2['Position'] == position) & (big_df2['Original series'] == maturity)]
            
            if not df_filtered.empty:
                fig.add_trace(go.Scatter(
                    x=df_filtered['Years to Maturity'],
                    y=df_filtered[column],
                    mode='markers',
                    marker=dict(
                        size=df_filtered['sizes'],
                        color=color_map[position],
                        symbol=symbol,
                    ),
                    name=f"{position} - {maturity}",
                    legendgroup=f"{position} + {maturity}",
                    showlegend=False,
                    hovertemplate=(
                        "Description: %{customdata[0]}<br>"
                        "CUSIP: %{customdata[1]}<br>"
                        "Position: %{customdata[2]}<br>"
                        "Years to Maturity: %{x}<br>"
                        f"{column}: %{{y}}<br>"
                        "Maturity: {maturity}"
                    ).format(maturity=maturity),
                    customdata=df_filtered[['Description', 'CUSIP', 'Position']].values,
                ))

    # Add compressed legend items
    legend_items = [
        ("overweight", "circle", "mediumseagreen"),
        ("underweight", "circle", "mediumvioletred"),
    ] + [(maturity, symbol, "black") for maturity, symbol in symbols_dict.items()]

    for name, symbol, color in legend_items:
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color, symbol=symbol),
            name=name,
            legendgroup=name,
            showlegend=True
        ))

    return fig

# In your update_scatter_plot function, update the layout:
fig.update_layout(
    xaxis=dict(title=dict(text="Years to Maturity", font=dict(size=20))),
    yaxis=dict(title=dict(text=y_title, font=dict(size=20))),
    height=500,
    title="Run Date: %s" % date,
    legend=dict(
        itemsizing="constant",
        font=dict(size=16),
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
        itemclick="toggle",
        itemdoubleclick="toggle",
        traceorder="normal"
    ),
    hoverlabel_font_color="white",
    margin=dict(r=150)  # Add right margin to accommodate the legend
)

# Add this function to your callbacks
@app.callback(
    Output("scatter-plot", "figure"),
    Input("scatter-plot", "restyleData"),
    State("scatter-plot", "figure")
)
def update_visibility(restyle_data, figure):
    if restyle_data is not None:
        for trace in figure['data']:
            if trace['showlegend']:  # This is a legend item
                visibility = trace['visible']
                name = trace['name']
                # Update visibility of corresponding data traces
                for data_trace in figure['data']:
                    if not data_trace['showlegend'] and (name in data_trace['legendgroup']):
                        data_trace['visible'] = visibility
    return figure
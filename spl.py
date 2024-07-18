@dashapp.callback(
    [
        Output("scatter-plot", "figure"),
        Output("download-data", "href"),
        Output("download-data", "download"),
        Output("summary_table", "data"),
        Output("table_title", "children"),
    ],
    [State("scatter-plot", "figure"), State("download-data", "href")],
    Input("port_ddn", "value"),
    Input("scatter-plot", "relayoutData"),
    Input("y_value_ddn", "value")
)
def update_scatter_plot(figure_obj, data, key, relay_data, column):
    # ... (keep the existing code up to the point where the figure is created)

    graph_trace = px.scatter(
        big_df2,
        x="Years to Maturity",
        y=column,
        size="sizes",
        hover_name="Description",
        hover_data=["CUSIP", "Position"],
        color="Position",
        color_discrete_map={
            "underweight": "mediumvioletred",
            "overweight": "mediumseagreen",
            "benchmark": "gray",
        },
        title=key,
        symbol="Original series",
        symbol_map=symbols_dict,
    )

    fig = go.Figure()
    fig.add_traces(list(graph_trace.data))

    # ... (keep other figure updates)

    # Replace utils.compress_legend with this new function
    def simplify_legend(fig):
        # Get unique positions and original series
        positions = big_df2['Position'].unique()
        original_series = big_df2['Original series'].unique()

        # Create a trace for each position (overweight, underweight, benchmark)
        for position in positions:
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=10, color=graph_trace.data[0].marker.color),
                name=position,
                legendgroup=position,
                showlegend=True
            ))

        # Create a trace for each original series (2Y, 3Y, 5Y, etc.)
        for series in original_series:
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=10, symbol=symbols_dict[series], color='gray'),
                name=series,
                legendgroup=series,
                showlegend=True
            ))

        # Hide individual traces from legend but keep them in the plot
        for trace in fig.data[:-len(positions)-len(original_series)]:
            trace.showlegend = False

        return fig

    # Apply the new legend simplification
    fig = simplify_legend(fig)

    fig.update_layout(
        legend=dict(
            itemsizing="constant",
            font=dict(size=16),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            itemclick="toggleothers",
            itemdoubleclick="toggle"
        ),
        hoverlabel_font_color="white",
    )

    # ... (keep the rest of the function as is)

    return [fig, csv_string, "data.csv", table_data, krd]
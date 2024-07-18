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

    def simplify_legend(fig):
        # Get unique positions and original series
        positions = big_df2['Position'].unique()
        original_series = big_df2['Original series'].unique()

        # Create a dictionary to store traces for each position and series
        legend_traces = {}

        # Group traces by position and series
        for trace in fig.data:
            position = trace.name.split(' - ')[0] if ' - ' in trace.name else trace.name
            series = trace.name.split(' - ')[1] if ' - ' in trace.name else ''
            
            if position not in legend_traces:
                legend_traces[position] = {}
            
            if series not in legend_traces[position]:
                legend_traces[position][series] = trace
            
            trace.showlegend = False

        # Add grouped traces to the figure
        for position, series_traces in legend_traces.items():
            for series, trace in series_traces.items():
                new_trace = trace.copy()
                new_trace.showlegend = True
                new_trace.name = f"{position} - {series}" if series else position
                new_trace.legendgroup = position
                fig.add_trace(new_trace)

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
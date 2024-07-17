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
    # ... (keep all the existing code up to the graph_trace creation)

    graph_trace = px.scatter(
        big_df2,
        x="Years to Maturity",
        y=column,
        size="size",
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

    # NEW: Modify trace names to include both Position and Original series
    for trace in graph_trace.data:
        position = trace.name
        symbol = trace.marker.symbol
        trace.name = f"{position} - {symbol}"
        trace.legendgroup = position

    try:
        fig.add_traces(list(graph_trace.data))
    except Exception as e:
        fig.add_trace(go.Scatter(visible=False, showlegend=False))

    if column == "Fed Hold %":
        fig.update_yaxes(range=[-5, 75])

    if column == "CMT RVS":
        y_title = "Basis Points From Fair Value"
    else:
        y_title = str(column)

    fig.update_layout(
        xaxis=dict(title=dict(text="Years to Maturity", font=dict(size=20))),
        yaxis=dict(title=dict(text=y_title, font=dict(size=20))),
        height=500,
        title="Run Date: %s" % date,
    )
    fig.update_xaxes(range=[0, 30.05])

    csv_string = big_df2.to_csv(index=False, encoding="utf-8")
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    if key == "ALL":
        table_data = None

    # Keep the compress_legend call as it's important for your plot's appearance
    utils.compress_legend(
        fig,
        "overweight",
        "underweight",
        "mediumseagreen",
        "mediumvioletred",
        symbols_dict,
    )

    # NEW: Update legend configuration after compress_legend
    fig.update_layout(
        legend=dict(
            itemsizing="constant",
            font=dict(size=16),
            orientation="h",
            x=1,
            y=1,
            itemclick="toggle",
            itemdoubleclick="toggleothers",
        ),
        hoverlabel_font_color="white",
    )

    return [fig, csv_string, "data.csv", table_data, krd]
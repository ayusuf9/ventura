dcc.Checklist(
    id='position-filter',
    options=[
        {'label': 'Underweight', 'value': 'underweight'},
        {'label': 'Overweight', 'value': 'overweight'},
        {'label': 'Benchmark', 'value': 'benchmark'}
    ],
    value=['underweight', 'overweight', 'benchmark'],  # All selected by default
    inline=True
)

@dashapp.callback(
    [
        Output("scatter-plot", "figure"),
        Output("download-data", "href"),
        Output("download-data", "download"),
        Output("summary_table", "data"),
        Output("table_title", "children"),
    ],
    [
        State("scatter-plot", "figure"),
        State("download-data", "href"),
        Input("port_ddn", "value"),
        Input("scatter-plot", "relayoutData"),
        Input("y_value_ddn", "value"),
        Input("position-filter", "value")  # New input
    ]
)


def update_scatter_plot(figure_obj, data, key, relay_data, column, position_filter):
    # ... (previous code remains the same)

    # Filter the DataFrame based on selected positions
    big_df2_filtered = big_df2[big_df2['Position'].isin(position_filter)]

    # Use the filtered DataFrame for plotting
    graph_trace = px.scatter(
        big_df2_filtered,  # Use filtered DataFrame
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

    # ... (rest of the function remains the same)

    # Update the CSV string with filtered data
    csv_string = big_df2_filtered.to_csv(index=False, encoding="utf-8")
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)

    # ... (rest of the function remains the same)




    # How about this ....



    def update_scatter_plot(figure_obj, data, key, relay_data, column):
        trigger_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
        date = data_loader.big_df2_dict["ALL"]["run_date"].values[0]
        auto_in = False
        krd = "KRD" if key != "ALL" else None

        # Keep your existing logic for handling relay_data, etc.
        
        # ... (keep your existing data loading and preprocessing logic)

        big_df2 = data_loader.big_df2_dict[key]
        # ... (keep any other data preparation steps)

        # Replace your px.scatter() call and subsequent figure modifications with this new code:
        traces = []
        for position in ['underweight', 'overweight', 'benchmark']:
            df_position = big_df2[big_df2['Position'] == position]
            trace = go.Scatter(
                x=df_position["Years to Maturity"],
                y=df_position[column],
                mode='markers',
                marker=dict(
                    size=df_position["sizes"],
                    symbol=df_position["Original series"].map(symbols_dict),
                    color={"underweight": "mediumvioletred", "overweight": "mediumseagreen", "benchmark": "gray"}[position],
                ),
                name=position.capitalize(),
                hovertemplate=(
                    "<b>%{hovertext}</b><br>"
                    "CUSIP: %{customdata[0]}<br>"
                    "Position: %{customdata[1]}<br>"
                    "Years to Maturity: %{x:.2f}<br>"
                    f"{column}: %{{y:.2f}}"
                ),
                hovertext=df_position["Description"],
                customdata=df_position[["CUSIP", "Position"]],
            )
            traces.append(trace)

        fig = go.Figure(data=traces)

        fig.update_layout(
            xaxis=dict(title=dict(text="Years to Maturity", font=dict(size=20))),
            yaxis=dict(title=dict(text=y_title, font=dict(size=20))),
            height=500,
            title="Run Date: %s" % date,
            legend=dict(
                itemsizing="constant",
                font=dict(size=16),
                orientation="h",
                x=1,
                y=1,
            ),
            hoverlabel_font_color="white",
        )

        fig.update_xaxes(range=[0, 30.05])
        if column == "Fed Hold %":
            fig.update_yaxes(range=[-5, 75])

        # Keep your existing code for creating csv_string, table_data, etc.
        csv_string = big_df2.to_csv(index=False, encoding="utf-8")
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
        
        # ... (keep any other necessary logic)

        return [fig, csv_string, "data.csv", table_data, krd]
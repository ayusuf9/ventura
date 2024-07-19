@dashapp.callback(
    [
        Output("scatter-plot", "figure"),
        Output("download-data", "href"),
        Output("download-data", "download"),
        Output("summary_table", "data"),
        Output("table_title", "children"),
    ],
    [State("scatter-plot", "figure"), State("download-data", "href")],
    [
        Input("port_ddn", "value"),
        Input("scatter-plot", "relayoutData"),
        Input("y_value_ddn", "value"),
    ],
)
def update_scatter_plot(figure_obj, data, key, relay_data, column):
    trigger_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    date = data_loader.big_df2_dict["All"]["run_date"].values[0]
    auto_in = False
    krd = "KRD" if key != "All" else None

    if relay_data is not None:
        auto_in = "autosize" in relay_data.keys()
    if "scatter-plot" in trigger_id and not auto_in:
        big_df2 = data_loader.big_df2_dict[key]
        correct_range = False
        try:
            correct_range = (
                "xaxis.range[0]" in relay_data.keys()
                or "yaxis.range[0]" in relay_data.keys()
            )
        except:
            pass

        if not correct_range:
            table_data, table_columns = utils.create_summary_table(big_df2, key)
            if key == "All":
                table_data = None
            return [figure_obj, data, "data.csv", table_data, krd]

        else:
            new_df = big_df2.copy()
            if "xaxis.range[0]" in relay_data.keys():
                new_df = new_df.loc[
                    new_df["Years to Maturity"] > relay_data["xaxis.range[0]"]
                ]
                new_df = new_df.loc[
                    new_df["Years to Maturity"] < relay_data["xaxis.range[1]"]
                ]
            if "yaxis.range[0]" in relay_data.keys():
                new_df = new_df.loc[new_df[column] > relay_data["yaxis.range[0]"]]
                new_df = new_df.loc[new_df[column] < relay_data["yaxis.range[1]"]]
            adc = new_df["Active Duration Contribution_Individual"].sum()
            adc = round(adc, 4)

            table_data, table_columns = utils.create_summary_table(new_df, key)
            if key == "All":
                table_data = None
            return [figure_obj, data, "data.csv", table_data, krd]

    else:
        fig = go.Figure()
        big_df2 = data_loader.big_df2_dict[key]
        big_df2 = big_df2.sort_values("Original series")
        table_data, table_columns = utils.create_summary_table(big_df2, key)
        annotation_text = ""
        if key == "All":
            grouped_df = big_df2.groupby("CUSIP")
            result = grouped_df.apply(
                lambda x: np.sum(
                    x["Active Duration Contribution"]
                    * x["portfolioNAVComputedNotional"]
                )
                / np.sum(x["portfolioNAVComputedNotional"])
            )
            result_abs = result.abs().reset_index(name="AvgActiveDur")
            big_df2 = big_df2.merge(result_abs, on="CUSIP", how="left")
            big_df2["AvgActiveDur"] = big_df2["AvgActiveDur"].round(3)
            size = "AvgActiveDur"
            annotation_text = f'Total ADC : {str(round(big_df2["Active Duration Contribution"].sum(), 4))}'
        else:
            size = "ADC Abs"
            annotation_text = f'Total ADC : {str(round(big_df2["Active Duration Contribution_Individual"].sum(), 4))}'

        df_rename_values = {
            2.0: "2Y", 3.0: "3Y", 5.0: "5Y", 7.0: "7Y",
            10.0: "10Y", 20.0: "20Y", 30.0: "30Y",
        }
        symbols_dict = {
            "2Y": "circle", "3Y": "square", "5Y": "diamond",
            "7Y": "cross", "10Y": "x", "20Y": "star", "30Y": "bowtie",
        }
        big_df2["Original series"] = big_df2["Original series"].apply(
            lambda x: df_rename_values.get(x, x)
        )

        max_size, min_size = 15, 2
        big_df2['normalized_size'] = (big_df2[size] - big_df2[size].min()) / (big_df2[size].max() - big_df2[size].min())
        big_df2['Size'] = big_df2['normalized_size'] * (max_size - min_size) + min_size

        bench = [benchmark.split("/")[1] for benchmark in data_loader.ddn_options_list if benchmark != "All"]
        if bench:
            big_df2.loc[np.isin(big_df2["indportname"], bench), "Position"] = "benchmark"

        graph_trace = px.scatter(
            big_df2,
            x="Years to Maturity",
            y=column,
            size="Size",
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
            title=key,
        )

        fig.add_traces(list(graph_trace.data))

        # Modify traces for correct legend display
        for trace in fig.data:
            trace.showlegend = False

        # Add custom legend items
        colors = {"underweight": "mediumvioletred", "overweight": "mediumseagreen", "benchmark": "gray"}
        for position in ["underweight", "overweight", "benchmark"]:
            fig.add_trace(go.Scatter(
                x=[None], y=[None], mode="markers",
                marker=dict(size=10, color=colors[position]),
                name=position.capitalize(),
                legendgroup=position,
                showlegend=True
            ))

        if column == "Fed Hold %":
            fig.update_yaxes(range=[-5, 75])

        y_title = "Basis Points From Fair Value" if column == "CMT RVS" else str(column)
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
            hoverlabel_font_color="white",
        )

        fig.update_xaxes(range=[0, 30.05])
        csv_string = big_df2.to_csv(index=False, encoding="utf-8")
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
        if key == "All":
            table_data = None

        return [fig, csv_string, "data.csv", table_data, krd]
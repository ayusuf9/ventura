import dash
import urllib
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from support_functions.load_data import LoadData
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from support_functions import utils
from controls import QH_APPDATA_BUCKET_NAME, S3_RESOURCE
from dash import ctx

global data_loader
prefix = "appdata/users/dlqs/riskvalspline/output_"

def remove_duplicates(dicts):
    unique_dicts = []
    seen = set()

    for d in dicts:
        key = (d["hovertext"], d["marker.size"])
        
        if key not in seen:
            unique_dicts.append(d)
            seen.add(key)
    
    return unique_dicts

def register_callbacks(dashapp):
    @dashapp.callback(
        Output("date_ddn", "options"),
        Output("date_ddn", "value"),
        Input("url", "href"),
        Input("back_btn", "n_clicks"),
        Input("next_btn", "n_clicks"),
        State("date_ddn", "options"),
        State("date_ddn", "value"),
    )
    def load_dates(url, back_clicks, next_clicks, date_options, date_value):
        if len(date_options) > 0 and date_value is not None:
            length = len(date_options)
            index = date_options.index(date_value)
            factor = 0
            if "back_btn" == ctx.triggered_id:
                factor = 1
            elif "next_btn" == ctx.triggered_id:
                factor = -1
            index += factor
            index %= length
            return date_options, date_options[index]
        
        my_bucket = S3_RESOURCE.Bucket(QH_APPDATA_BUCKET_NAME)
        
        all_runs = []
        for run in my_bucket.objects.filter(Prefix="appdata/users/dlqs/riskvalspline"):
            if len(run.key.split("_")) > 1:
                key = run.key.split("_")[1]
                key = key.split(".")[0]
                all_runs.append(key)
        all_runs.sort(reverse=True)
        all_runs.pop(0)
        
        return [all_runs, all_runs[0]]

    @dashapp.callback(
        Output("port_ddn", "options"),
        Output("port_ddn", "value"),
        Output("ports_count", "children"),
        Input("date_ddn", "value"),
        State("port_ddn", "value"),
    )
    def update_data(date_value, current_port):
        global data_loader
        
        filename = prefix + date_value + ".json"
        
        data_loader = LoadData(Key=filename)
        
        if current_port not in data_loader.ddn_options_list:
            current_port = "ALL"
            ports_count_msg = "Ports Count: " + str(len(data_loader.ddn_options_list))
        
        return [data_loader.ddn_options, current_port, ports_count_msg]

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
        trigger_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
        date = data_loader.big_df2_dict["ALL"]["run_date"].values[0]
        auto_in = False
        krd = "KRD" if key != "ALL" else None

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
                if key == "ALL":
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
                if key == "ALL":
                    table_data = None

                return [figure_obj, data, "data.csv", table_data, krd]
        else:
            fig = go.Figure()
            big_df2 = data_loader.big_df2_dict[key]
            big_df2 = big_df2.sort_values("Original series")
            table_data, table_columns = utils.create_summary_table(big_df2, key)
            annotation_text = ""
            if key == "ALL":
                grouped_df = big_df2.groupby("CUSIP")
                result = grouped_df.apply(
                    lambda x: np.sum(
                        x["Active Duration Contribution"]
                        * x["PortfolioNAVComputedNotional"]
                    )
                    / np.sum(x["PortfolioNAVComputedNotional"])
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
                2.0: "2Y",
                3.0: "3Y",
                5.0: "5Y",
                7.0: "7Y",
                10.0: "10Y",
                20.0: "20Y",
                30.0: "30Y",
            }

            symbols_dict = {
                "2Y": "circle",
                "3Y": "square",
                "5Y": "diamond",
                "7Y": "cross",
                "10Y": "x",
                "20Y": "star",
                "30Y": "bowtie",
            }

            big_df2["Original series"] = big_df2["Original series"].apply(
                lambda x: df_rename_values[x] if x in df_rename_values.keys() else x
            )

            def normalize_and_scale(df, column, min_value, max_value):
                df['normalized'] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
                df['sizes'] = df['normalized'] * (max_value - min_value) + min_value
                return df
            
            big_df2 = normalize_and_scale(big_df2, size, 5, 18)

            bench = []

            for benchmark in data_loader.ddn_options_list:
                if benchmark == "All":
                    continue
                bench.append(benchmark.split("/")[1])
            print(bench)

            if bench is not None:
                big_df2.loc[np.isin(big_df2["indportname"], bench), "Position"] = (
                    "benchmark"
                )

            # Split data by categories
            overweight_df = big_df2[big_df2["Position"] == "overweight"]
            underweight_df = big_df2[big_df2["Position"] == "underweight"]
            benchmark_df = big_df2[big_df2["Position"] == "benchmark"]

            # Create separate traces for each category
            fig.add_trace(go.Scatter(
                x=overweight_df["Years to Maturity"],
                y=overweight_df[column],
                mode='markers',
                name='Overweight',
                marker=dict(color="mediumseagreen", size=overweight_df["sizes"]),
                hovertext=overweight_df["Description"],
                hoverinfo="text"
            ))

            fig.add_trace(go.Scatter(
                x=underweight_df["Years to Maturity"],
                y=underweight_df[column],
                mode='markers',
                name='Underweight',
                marker=dict(color="mediumvioletred", size=underweight_df["sizes"]),
                hovertext=underweight_df["Description"],
                hoverinfo="text"
            ))

            fig.add_trace(go.Scatter(
                x=benchmark_df["Years to Maturity"],
                y=benchmark_df[column],
                mode='markers',
                name='Benchmark',
                marker=dict(color="gray", size=benchmark_df["sizes"]),
                hovertext=benchmark_df["Description"],
                hoverinfo="text"
            ))

            # Update layout
            fig.update_layout(
                title=key,
                xaxis_title="Years to Maturity",
                yaxis_title=column,
                legend_title="Position",
                height=500,
                title_text=f"Run Date: {date}",
                legend=dict(
                    itemsizing="constant",
                    font=dict(size=16),
                    orientation="h",
                    x=1,
                    y=1,
                    itemclick="toggleothers",
                    itemdoubleclick="toggle"
                ),
                hoverlabel=dict(font_color="white")
            )

            csv_string = big_df2.to_csv(index=False, encoding="utf-8")
            csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)

            return [fig, csv_string, "data.csv", table_data, krd]


import dash
import urllib
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State
from dash import ctx

# Assume these imports are correctly set up in your environment
from support_functions.load_data import LoadData
from controls import QH_APPDATA_BUCKET_NAME, S3_RESOURCE
from support_functions import utils

global data_loader

prefix = "appdata/users/dlqs/riskvalspline/output_"

def create_compressed_legend(fig):
    # Define the new legend items
    legend_items = [
        {"name": "overweight", "color": "mediumseagreen", "symbol": "circle"},
        {"name": "underweight", "color": "mediumvioletred", "symbol": "circle"},
        {"name": "2Y", "color": "gray", "symbol": "circle"},
        {"name": "3Y", "color": "gray", "symbol": "square"},
        {"name": "5Y", "color": "gray", "symbol": "diamond"},
        {"name": "7Y", "color": "gray", "symbol": "cross"},
        {"name": "10Y", "color": "gray", "symbol": "x"},
        {"name": "20Y", "color": "gray", "symbol": "star"},
        {"name": "30Y", "color": "gray", "symbol": "bowtie"},
    ]

    # Create a mapping of original trace names to new legend groups
    trace_to_group = {}
    for trace in fig.data:
        if ' - ' in trace.name:
            position, maturity = trace.name.split(' - ')
            trace_to_group[trace.name] = (position, maturity)
        else:
            trace_to_group[trace.name] = (trace.name, '')

    # Update existing traces
    for trace in fig.data:
        position, maturity = trace_to_group[trace.name]
        trace.legendgroup = position if position in ['overweight', 'underweight'] else maturity
        trace.showlegend = False

    # Add new traces for the compressed legend
    for item in legend_items:
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=item["color"], symbol=item["symbol"]),
            name=item["name"],
            legendgroup=item["name"],
            showlegend=True
        ))

    # Update layout for legend
    fig.update_layout(
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            itemsizing='constant',
            itemclick="toggle",
            itemdoubleclick="toggle"
        )
    )

    return fig

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
                2.0: "2Y", 3.0: "3Y", 5.0: "5Y", 7.0: "7Y",
                10.0: "10Y", 20.0: "20Y", 30.0: "30Y",
            }

            symbols_dict = {
                "2Y": "circle", "3Y": "square", "5Y": "diamond",
                "7Y": "cross", "10Y": "x", "20Y": "star", "30Y": "bowtie",
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

            if bench is not None:
                big_df2.loc[np.isin(big_df2["indportname"], bench), "Position"] = "benchmark"

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

            fig.add_traces(list(graph_trace.data))

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
            
            # Apply the new legend compression
            fig = create_compressed_legend(fig)

            csv_string = big_df2.to_csv(index=False, encoding="utf-8")
            csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
            if key == "ALL":
                table_data = None

            fig.update_layout(
                hoverlabel_font_color="white",
            )

            return [fig, csv_string, "data.csv", table_data, krd]

    # Add any other callbacks you need here

# This is typically how you would set up your Dash app
app = dash.Dash(__name__)
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
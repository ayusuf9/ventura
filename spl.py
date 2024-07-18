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

def create_compressed_legend(fig, big_df2):
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

    # Clear existing traces
    fig.data = []

    # Create traces for each combination of position and maturity
    for item in legend_items:
        if item['name'] in ['overweight', 'underweight']:
            df_filtered = big_df2[big_df2['Position'] == item['name']]
            for maturity in ['2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']:
                df_maturity = df_filtered[df_filtered['Original series'] == maturity]
                fig.add_trace(go.Scatter(
                    x=df_maturity['Years to Maturity'],
                    y=df_maturity[column],
                    mode='markers',
                    marker=dict(
                        size=df_maturity['sizes'],
                        color=item['color'],
                        symbol=symbols_dict[maturity],
                    ),
                    name=f"{item['name']} - {maturity}",
                    legendgroup=item['name'],
                    showlegend=False,
                    hovertemplate=(
                        "Description: %{customdata[0]}<br>"
                        "CUSIP: %{customdata[1]}<br>"
                        "Position: %{customdata[2]}<br>"
                        "Years to Maturity: %{x}<br>"
                        f"{column}: %{{y}}"
                    ),
                    customdata=df_maturity[['Description', 'CUSIP', 'Position']],
                ))
        else:
            df_filtered = big_df2[big_df2['Original series'] == item['name']]
            fig.add_trace(go.Scatter(
                x=df_filtered['Years to Maturity'],
                y=df_filtered[column],
                mode='markers',
                marker=dict(
                    size=df_filtered['sizes'],
                    color=df_filtered['Position'].map({
                        'overweight': 'mediumseagreen',
                        'underweight': 'mediumvioletred',
                        'benchmark': 'gray'
                    }),
                    symbol=item['symbol'],
                ),
                name=item['name'],
                legendgroup=item['name'],
                showlegend=False,
                hovertemplate=(
                    "Description: %{customdata[0]}<br>"
                    "CUSIP: %{customdata[1]}<br>"
                    "Position: %{customdata[2]}<br>"
                    "Years to Maturity: %{x}<br>"
                    f"{column}: %{{y}}"
                ),
                customdata=df_filtered[['Description', 'CUSIP', 'Position']],
            ))

    # Add legend traces
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
    # ... (keep your existing callbacks for date and port dropdowns)

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
        global data_loader
        
        trigger_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
        date = data_loader.big_df2_dict["ALL"]["run_date"].values[0]
        auto_in = False
        krd = "KRD" if key != "ALL" else None

        if relay_data is not None:
            auto_in = "autosize" in relay_data.keys()
        if "scatter-plot" in trigger_id and not auto_in:
            # ... (keep your existing code for handling relayout)
            pass
        else:
            fig = go.Figure()
            big_df2 = data_loader.big_df2_dict[key]
            big_df2 = big_df2.sort_values("Original series")
            table_data, table_columns = utils.create_summary_table(big_df2, key)
            annotation_text = ""
            
            # ... (keep your existing data processing code)

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

            # ... (keep your existing normalization and benchmark code)

            # Apply the new legend compression
            fig = create_compressed_legend(fig, big_df2)

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
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

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
                hover_text = df_filtered.apply(
                    lambda row: f"Description: {row.get('Description', 'N/A')}<br>"
                                f"CUSIP: {row.get('CUSIP', 'N/A')}<br>"
                                f"Position: {row['Position']}<br>"
                                f"Years to Maturity: {row['Years to Maturity']:.2f}<br>"
                                f"{column}: {row[column]:.2f}<br>"
                                f"Maturity: {maturity}",
                    axis=1
                )

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
                    legendgroup=position,
                    showlegend=False,
                    text=hover_text,
                    hoverinfo='text',
                    visible=True
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
            showlegend=True,
            visible=True
        ))

    return fig

def update_scatter_plot(figure_obj, data, key, relay_data, column):
    # ... (previous code remains the same)

    fig = create_compressed_figure(big_df2, column, symbols_dict)

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
        margin=dict(r=150)
    )

    return [fig, csv_string, "data.csv", table_data, krd]

def register_callbacks(app):
    @app.callback(
        Output("scatter-plot", "figure"),
        Input("scatter-plot", "restyleData"),
        State("scatter-plot", "figure")
    )
    def update_visibility(restyle_data, figure):
        if restyle_data and restyle_data[0].get('visible') is not None:
            visibility = restyle_data[0]['visible'][0]
            trace_index = restyle_data[1][0]
            clicked_trace = figure['data'][trace_index]
            
            if clicked_trace['showlegend']:
                clicked_name = clicked_trace['name']
                
                for i, trace in enumerate(figure['data']):
                    if not trace['showlegend']:
                        if clicked_name in ['overweight', 'underweight', 'benchmark']:
                            if trace['legendgroup'] == clicked_name:
                                figure['data'][i]['visible'] = visibility
                        elif clicked_name in trace['name']:
                            figure['data'][i]['visible'] = visibility

        return figure

    # ... (other callbacks)

# Set up the Dash app
app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Graph(id='scatter-plot')
])

register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
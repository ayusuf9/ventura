def create_compressed_figure(big_df2, column, symbols_dict):
    color_map = {
        'overweight': 'mediumseagreen',
        'underweight': 'mediumvioletred',
        'benchmark': 'gray'
    }

    fig = go.Figure()

    # Create a trace for each combination of Position and Original series
    for position in color_map.keys():
        for maturity in symbols_dict.keys():
            df_filtered = big_df2[(big_df2['Position'] == position) & (big_df2['Original series'] == maturity)]
            
            if not df_filtered.empty:
                hover_text = df_filtered.apply(
                    lambda row: f"Description: {row['Description']}<br>"
                                f"CUSIP: {row['CUSIP']}<br>"
                                f"Position: {row['Position']}<br>"
                                f"Years to Maturity: {row['Years to Maturity']}<br>"
                                f"{column}: {row[column]}<br>"
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
                        symbol=symbols_dict[maturity],
                    ),
                    name=f"{position} - {maturity}",
                    legendgroup=f"{position} - {maturity}",
                    showlegend=True,
                    text=hover_text,
                    hoverinfo='text'
                ))

    return fig



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
    # ... (keep the existing code up to the point where fig is created)

    fig = create_compressed_figure(big_df2, column, symbols_dict)

    # ... (keep the rest of the existing code)

    fig.update_layout(
        legend=dict(
            itemsizing="constant",
            font=dict(size=16),
            orientation="v",
            yanchor="top",
            xanchor="left",
            x=1.02,
            y=1,
            itemclick="toggle",
            itemdoubleclick="toggle"
        ),
        hoverlabel_font_color="white",
    )

    return [fig, csv_string, "data.csv", table_data, krd]
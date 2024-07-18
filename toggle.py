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
                # Create hover text
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
                    legendgroup=f"{position} + {maturity}",
                    showlegend=False,
                    text=hover_text,
                    hoverinfo='text'
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
            showlegend=True
        ))

    return fig
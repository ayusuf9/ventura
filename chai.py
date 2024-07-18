def create_compressed_figure(big_df2, column, symbols_dict):
    color_map = {
        'overweight': 'mediumseagreen',
        'underweight': 'mediumvioletred',
        'benchmark': 'gray'
    }

    fig = go.Figure()

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
                    legendgroup=position,
                    showlegend=False,
                    text=hover_text,
                    hoverinfo='text'
                ))

    # Add compressed legend items
    for position, color in color_map.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color, symbol='circle'),
            name=position,
            legendgroup=position,
            showlegend=True
        ))

    for maturity, symbol in symbols_dict.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color='gray', symbol=symbol),
            name=maturity,
            legendgroup=maturity,
            showlegend=True
        ))

    return fig
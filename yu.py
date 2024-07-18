def create_compressed_figure(big_df2, column, symbols_dict, size_column):
    color_map = {
        'overweight': 'mediumseagreen',
        'underweight': 'mediumvioletred',
        'benchmark': 'gray'
    }

    fig = go.Figure()

    # Normalize and scale sizes
    min_size, max_size = 5, 18
    if size_column in big_df2.columns:
        big_df2['normalized'] = (big_df2[size_column] - big_df2[size_column].min()) / (big_df2[size_column].max() - big_df2[size_column].min())
        big_df2['sizes'] = big_df2['normalized'] * (max_size - min_size) + min_size
    else:
        print(f"Warning: {size_column} not found in DataFrame. Using default size.")
        big_df2['sizes'] = 10  # Default size if the column is not found

    # Create traces for each combination of Position and Original series
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
                                f"Maturity: {maturity}<br>"
                                f"{size_column}: {row.get(size_column, 'N/A')}",
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

    # Add legend items for positions
    for position, color in color_map.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color, symbol='circle'),
            name=position.capitalize(),
            legendgroup=position,
            showlegend=True
        ))

    # Add legend items for maturities
    for maturity, symbol in symbols_dict.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color='black', symbol=symbol),
            name=maturity,
            legendgroup=maturity,
            showlegend=True
        ))

    return fig
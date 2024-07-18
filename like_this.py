def normalize_and_scale(values, min_size, max_size):
    if len(values) > 0:
        normalized = (values - values.min()) / (values.max() - values.min())
        return normalized * (max_size - min_size) + min_size
    else:
        return []

# Apply sizing to the entire dataset
if key == "All":
    size_column = "AvgActiveDur"
else:
    size_column = "ADC Abs"

big_df2["sizes"] = normalize_and_scale(big_df2[size_column], 5, 18)

# Create traces for overweight and underweight
for position in ["overweight", "underweight"]:
    df_filtered = big_df2[big_df2["Position"] == position]

    fig.add_trace(go.Scatter(
        x=df_filtered["Years to Maturity"],
        y=df_filtered[column],
        mode="markers",
        name=position.capitalize(),
        legendgroup=position,
        marker=dict(
            size=df_filtered["sizes"],
            color=colors[position],
            symbol=df_filtered["Original series"].map(symbols_dict)
        ),
        hovertemplate=(
            "Description: %{hovertext}<br>"
            "CUSIP: %{customdata[0]}<br>"
            "Position: %{customdata[1]}<br>"
            "Years to Maturity: %{x}<br>"
            f"{column}: %{{y}}<br>"
            "Maturity: %{customdata[2]}"
        ),
        hovertext=df_filtered["Description"],
        customdata=df_filtered[["CUSIP", "Position", "Original series"]]
    ))

# Create traces for each maturity
for maturity in symbols_dict.keys():
    df_filtered = big_df2[big_df2["Original series"] == maturity]
    
    # Add invisible trace for colored data points
    fig.add_trace(go.Scatter(
        x=df_filtered["Years to Maturity"],
        y=df_filtered[column],
        mode="markers",
        name=maturity,
        legendgroup=maturity,
        marker=dict(
            size=df_filtered["sizes"],
            symbol=symbols_dict[maturity],
            color=df_filtered["Position"].map(colors)
        ),
        hovertemplate=(
            "Description: %{hovertext}<br>"
            "CUSIP: %{customdata[0]}<br>"
            "Position: %{customdata[1]}<br>"
            "Years to Maturity: %{x}<br>"
            f"{column}: %{{y}}<br>"
            "Maturity: %{customdata[2]}"
        ),
        hovertext=df_filtered["Description"],
        customdata=df_filtered[["CUSIP", "Position", "Original series"]],
        showlegend=False
    ))

    # Add visible trace for black legend icon
    fig.add_trace(go.Scatter(
        x=[None], 
        y=[None],
        mode="markers", 
        name=maturity,
        legendgroup=maturity,
        marker=dict(
            size=10,
            symbol=symbols_dict[maturity],
            color='black'
        ),
        showlegend=True,
        hoverinfo='none'
    ))

# ... (rest of the code remains the same)
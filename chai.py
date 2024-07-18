fig = go.Figure()

positions = ["overweight", "underweight", "benchmark"]
colors = {"overweight": "mediumseagreen", "underweight": "mediumvioletred", "benchmark": "gray"}

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
        customdata=df_filtered[["CUSIP", "Position", "Original series"]]
    ))

# Update layout
fig.update_layout(
    xaxis=dict(title=dict(text="Years to Maturity", font=dict(size=20))),
    yaxis=dict(title=dict(text=y_title, font=dict(size=20))),
    height=500,
    title="Run Date: %s" % date,
    legend=dict(
        itemsizing="constant",
        font=dict(size=18),
        orientation="h",
        y=-0.2,
        x=0,
        groupclick="toggleitem"
    ),
    hoverlabel_font_color="white"
)

fig.update_xaxes(range=[0, 30.05])
if column == "Fed Hold %":
    fig.update_yaxes(range=[-5, 75])
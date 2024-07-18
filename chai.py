for maturity in symbols_dict.keys():
    for position in ["overweight", "underweight", "benchmark"]:
        df_filtered = big_df2[(big_df2["Original series"] == maturity) & (big_df2["Position"] == position)]
        fig.add_trace(go.Scatter(
            x=df_filtered["Years to Maturity"],
            y=df_filtered[column],
            mode="markers",
            name=f"{maturity} - {position}",
            legendgroup=maturity,
            marker=dict(
                size=df_filtered["sizes"],
                symbol=symbols_dict[maturity],
                color=color_discrete_map[position]
            ),
            hovertemplate=(
                "Description: %{hovertext}<br>"
                "CUSIP: %{customdata[0]}<br>"
                "Position: %{customdata[1]}<br>"
                "Years to Maturity: %{x}<br>"
                f"{column}: %{{y}}"
            ),
            hovertext=df_filtered["Description"],
            customdata=df_filtered[["CUSIP", "Position"]]
        ))



        fig.update_layout(
    legend=dict(
        itemsizing="constant",
        font=dict(size=18),
        orientation="h",
        x=0,
        y=-0.2,
        groupclick="toggleitem"
    ),
    hoverlabel_font_color="white",
    legend_tracegroupgap=5
)
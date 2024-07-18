def update_scatter_plot(figure_obj, data, key, relay_data, column):
    # ... (keep the beginning of the function as is)

    def normalize_and_scale(df, column, min_value, max_value):
        if column in df.columns:
            df['normalized'] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
            df['sizes'] = df['normalized'] * (max_value - min_value) + min_value
        else:
            df['sizes'] = (max_value + min_value) / 2  # Default size if column doesn't exist
        return df

    fig = go.Figure()

    big_df2 = data_loader.big_df2_dict[key]
    big_df2 = big_df2.sort_values("Original series")
    table_data, table_columns = utils.create_summary_table(big_df2, key)
    annotation_text = ""
    if key == "All":
        grouped_df = big_df2.groupby("CUSIP")
        result = grouped_df.apply(
            lambda x: np.sum(
                x["Active Duration Contribution"]
                * x["portfolioNAVComputedNotional"]
            )
            / np.sum(x["portfolioNAVComputedNotional"])
        )
        result_abs = result.abs().reset_index(name="AvgActiveDur")
        big_df2 = big_df2.merge(result_abs, on="CUSIP", how="left")
        big_df2["AvgActiveDur"] = big_df2["AvgActiveDur"].round(3)
        size_column = "AvgActiveDur"
        annotation_text = f'Total ADC : {str(round(big_df2["Active Duration Contribution"].sum(), 4))}'
    else:
        size_column = "ADC Abs"
        annotation_text = f'Total ADC : {str(round(big_df2["Active Duration Contribution_Individual"].sum(), 4))}'

    # Apply normalize_and_scale here, after size_column is defined
    big_df2 = normalize_and_scale(big_df2, size_column, 5, 18)

    # ... (rest of the function remains the same, including creating traces)

    # When creating traces, use the 'sizes' column
    for position in ["overweight", "underweight"]:
        df_filtered = big_df2[big_df2["Position"] == position]
        fig.add_trace(go.Scatter(
            # ...
            marker=dict(
                size=df_filtered["sizes"],
                # ... (other marker properties)
            ),
            # ...
        ))

    for maturity in symbols_dict.keys():
        df_filtered = big_df2[big_df2["Original series"] == maturity]
        fig.add_trace(go.Scatter(
            # ...
            marker=dict(
                size=df_filtered["sizes"],
                # ... (other marker properties)
            ),
            # ...
        ))

    # ... (rest of the function remains the same)
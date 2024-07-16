import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import streamlit as st

@st.cache_data
def run_rolling_corr_calc(df_universe, df_dependent, dependent_variable_name,
                          run_rolling_corr=True, rolling_windows=[1,3,5,7]):
    
    def process_chunk(chunk, dependent_series, windows):
        results = {}
        for col in chunk.columns:
            corr_results = {}
            for window in windows:
                corr = chunk[col].rolling(window=window*52).corr(dependent_series)
                corr_results[window] = corr
            results[col] = corr_results
        return results

    dependent_series = df_dependent[dependent_variable_name]
    chunk_size = 100  # Adjust based on your system's capabilities
    
    with ProcessPoolExecutor() as executor:
        futures = []
        for i in range(0, df_universe.shape[1], chunk_size):
            chunk = df_universe.iloc[:, i:i+chunk_size]
            futures.append(executor.submit(process_chunk, chunk, dependent_series, rolling_windows))
        
        results = {}
        for future in as_completed(futures):
            results.update(future.result())

    df_timeseries_dict = {year: pd.DataFrame() for year in rolling_windows}
    df_stats_dict = {year: pd.DataFrame() for year in rolling_windows}

    for var, corr_data in results.items():
        for year, corr_series in corr_data.items():
            df_timeseries_dict[year][var] = corr_series
            
            stats = pd.Series({
                'SEDOL': var.split('_')[0],
                'Attribute': '_'.join(var.split('_')[1:]),
                'Quantile 25%': corr_series.quantile(0.25),
                'Mean': corr_series.mean(),
                'Median': corr_series.median(),
                'Quantile 75%': corr_series.quantile(0.75),
                'Latest Value': corr_series.iloc[-1]
            })
            df_stats_dict[year][var] = stats

    for year in rolling_windows:
        df_timeseries_dict[year] = df_timeseries_dict[year].replace([-np.inf, np.inf], np.nan)
        df_timeseries_dict[year] = df_timeseries_dict[year].dropna(how='all', axis=1).dropna(how='all', axis=0)
        
        df_stats_dict[year] = df_stats_dict[year].T
        df_stats_dict[year] = df_stats_dict[year].replace([-np.inf, np.inf], np.nan)
        df_stats_dict[year] = df_stats_dict[year].dropna(how='all', axis=0)
        df_stats_dict[year].index.name = "Variable Name"
        df_stats_dict[year] = df_stats_dict[year].reset_index()

    df_timeseries = pd.concat(df_timeseries_dict.values(), keys=rolling_windows, axis=1)
    df_stats = pd.concat(df_stats_dict.values(), keys=rolling_windows)

    return [df_timeseries, df_stats]






## the other

from concurrent.futures import ProcessPoolExecutor, as_completed

df_timeseries, df_stats = run_rolling_corr_calc(df_universe, df_dependent, dependent_variable_name, rolling_windows=[1,3,5,7])

# Flatten the multi-index of df_stats
df_stats = df_stats.reset_index()
df_stats.columns = ['Rolling Window', 'Variable Name'] + list(df_stats.columns[2:])

noneditable_columns = list(df_stats.columns)
df_stats["plot"] = False
df_stats = df_stats.set_index(['Rolling Window', 'Variable Name'])
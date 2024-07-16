



import pandas as pd
import numpy as np
import multiprocessing as mp
import streamlit as st

def process_chunk(args):
    chunk, dependent_series, windows = args
    try:
        results = {}
        for col in chunk.columns:
            corr_results = {}
            for window in windows:
                corr = chunk[col].rolling(window=window*52).corr(dependent_series)
                corr_results[window] = corr
            results[col] = corr_results
        return results
    except Exception as e:
        return f"Error processing chunk: {str(e)}"

@st.cache_data
def run_rolling_corr_calc(df_universe, df_dependent, dependent_variable_name,
                          run_rolling_corr=True, rolling_windows=[1,3,5,7]):
    
    dependent_series = df_dependent[dependent_variable_name]
    chunk_size = 50  # Reduced chunk size for stability
    
    pool = mp.Pool(processes=mp.cpu_count())
    
    chunks = [df_universe.iloc[:, i:i+chunk_size] for i in range(0, df_universe.shape[1], chunk_size)]
    args_list = [(chunk, dependent_series, rolling_windows) for chunk in chunks]
    
    results = {}
    for result in pool.imap_unordered(process_chunk, args_list):
        if isinstance(result, dict):
            results.update(result)
        else:
            print(result)  # Print any error messages
    
    pool.close()
    pool.join()

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
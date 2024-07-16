import os
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

def run_rolling_corr_calc(df_universe, df_dependent, dependent_variable_name,
                          run_rolling_corr=True, rolling_windows=[1,3,5,7],
                          cache_dir='cache'):
    
    # Create a cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    # Create a unique cache key based on input parameters
    cache_key = f"{dependent_variable_name}_{run_rolling_corr}_{'-'.join(map(str, rolling_windows))}"
    timeseries_cache_path = os.path.join(cache_dir, f"{cache_key}_timeseries.parquet")
    stats_cache_path = os.path.join(cache_dir, f"{cache_key}_stats.parquet")
    
    # Check if cached results exist
    if os.path.exists(timeseries_cache_path) and os.path.exists(stats_cache_path):
        # Load cached results
        df_timeseries = pd.read_parquet(timeseries_cache_path)
        df_stats = pd.read_parquet(stats_cache_path)
        return [df_timeseries, df_stats]
    
    # If not cached, run the original function
    start_ind = 0
    end_ind = 2500

    df_timeseries_dict = dict()
    df_stats_dict = dict()
    for year in rolling_windows:
        df_timeseries_dict[f"{year}"] = []
        df_stats_dict[f"{year}"] = []

    for i in range(0, round(df_universe.shape[1]/2500)+1):
        if start_ind < df_universe.shape[1]:
            df_independent = df_universe.iloc[:, start_ind:end_ind]

            independent_variable_names = list(df_independent.columns)
            if dependent_variable_name in independent_variable_names:
                independent_variable_names.remove(dependent_variable_name)
                df_temp = df_independent
            else:
                df_temp = pd.merge(df_dependent, df_independent, left_index=True, right_index=True)

        results = []
        for independent_variable_name in independent_variable_names:
            result = get_correlation(df_temp, dependent_variable_name, independent_variable_name, run_rolling_corr, rolling_windows)
            results.append(result)

        for year in rolling_windows:
            dict_timeseries = [item["Time Series"] for item in results]
            list_timeseries = [item[f"{year} Rolling Corr"] for item in dict_timeseries]
            df_results_timeseries = pd.concat(list_timeseries, axis=1)
            df_timeseries_dict[f"{year}"].append(df_results_timeseries)

            dict_stats = [item["Stats"] for item in results]
            list_stats = [item[f"{year} Rolling Corr"] for item in dict_stats]
            df_stats = pd.concat(list_stats)
            df_stats_dict[f"{year}"].append(df_stats)

        start_ind += 2500
        end_ind += 2500
        if start_ind >= df_universe.shape[1]:
            break

    for year in rolling_windows:
        df_timeseries = pd.concat(df_timeseries_dict[f"{year}"], axis=1)
        df_timeseries = df_timeseries.replace([-np.inf, np.inf], np.nan)
        df_timeseries = df_timeseries.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df_timeseries.index.name = "Variable Name"
        df_timeseries = df_timeseries.reset_index()

        df_stats = pd.concat(df_stats_dict[f"{year}"])
        df_stats = df_stats.replace([-np.inf, np.inf], np.nan)
        df_stats = df_stats.dropna(how='all', axis=0)
        df_stats.index.name = "Variable Name"
        df_stats = df_stats.reset_index()

    # Save results to parquet files
    df_timeseries.to_parquet(timeseries_cache_path, index=False)
    df_stats.to_parquet(stats_cache_path, index=False)

    return [df_timeseries, df_stats]
import multiprocessing
from itertools import repeat
import pandas as pd
import numpy as np
import streamlit as st

# Dummy get_correlation function for demonstration
def get_correlation(df_temp, dependent_variable_name, independent_variable_name, run_rolling_corr, rolling_windows):
    return {
        "Time Series": {f"{year} Rolling Corr": pd.DataFrame() for year in rolling_windows},
        "Stats": {f"{year} Rolling Corr": pd.DataFrame() for year in rolling_windows}
    }

@st.cache_data
def run_rolling_corr_calc(df_universe, df_dependent, dependent_variable_name,
                          run_rolling_corr=True, rolling_windows=[1, 3, 5, 7]):
    
    start_ind = 0
    end_ind = 2500

    df_timeseries_dict = dict()
    df_stats_dict = dict()
    for year in rolling_windows:
        df_timeseries_dict[f"{year}"] = []
        df_stats_dict[f"{year}"] = []

    for i in range(0, round(df_universe.shape[1] / 2500) + 1):
        if start_ind < df_universe.shape[1]:
            df_independent = df_universe.iloc[:, start_ind:end_ind]

            independent_variable_names = list(df_independent.columns)
            if dependent_variable_name in independent_variable_names:
                independent_variable_names.remove(dependent_variable_name)
                df_temp = df_independent
            else:
                df_temp = pd.merge(df_dependent, df_independent, left_index=True, right_index=True)

            multi_process_on = True  # Change this to True to enable multiprocessing

            if multi_process_on:
                multiprocess_params = zip(repeat(df_temp), repeat(dependent_variable_name), independent_variable_names,
                                          repeat(run_rolling_corr), repeat(rolling_windows))
                num_cpu = multiprocessing.cpu_count() - 2
                with multiprocessing.Pool(num_cpu) as pool:
                    results = pool.starmap(get_correlation, multiprocess_params)
            else:
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
        else:
            break

    final_timeseries_dict = {}
    final_stats_dict = {}

    for year in rolling_windows:
        df_timeseries = pd.concat(df_timeseries_dict[f"{year}"], axis=1)
        df_timeseries = df_timeseries.replace([-np.inf, np.inf], np.nan)
        df_timeseries = df_timeseries.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df_timeseries.index.name = "Variable Name"
        df_timeseries = df_timeseries.reset_index()
        final_timeseries_dict[f"{year}"] = df_timeseries

        df_stats = pd.concat(df_stats_dict[f"{year}"])
        df_stats = df_stats.replace([-np.inf, np.inf], np.nan)
        df_stats = df_stats.dropna(how='all', axis=0)
        df_stats.index.name = "Variable Name"
        df_stats = df_stats.reset_index()
        final_stats_dict[f"{year}"] = df_stats

    return [final_timeseries_dict, final_stats_dict]

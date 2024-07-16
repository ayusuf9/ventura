def save_all_dependent_variables(df_universe, df_dependent, dependent_variables, cache_dir='all_variables_cache'):
    results = {}
    rolling_windows = [1,3,5,7]  # Fixed rolling windows

    for dependent_variable in dependent_variables:
        print(f"Processing: {dependent_variable}")
        
        df_timeseries, df_stats = run_rolling_corr_calc(
            df_universe=df_universe,
            df_dependent=df_dependent,
            dependent_variable_name=dependent_variable,
            run_rolling_corr=True,
            rolling_windows=rolling_windows,
            cache_dir=cache_dir
        )
        
        # Store the results in a dictionary
        results[dependent_variable] = (df_timeseries, df_stats)
    
    return results

# Usage
df_universe = ...  # Your universe dataframe
df_dependent = ...  # Your dependent dataframe
dependent_variables = list(df_dependent.columns)  # Use all columns in df_dependent as dependent variables

all_results = save_all_dependent_variables(df_universe, df_dependent, dependent_variables)





def load_cached_variable_results(dependent_variable, cache_dir='all_variables_cache'):
    rolling_windows = [1,3,5,7]  # Must match the rolling windows used in saving
    cache_key = f"{dependent_variable}_{True}_{'-'.join(map(str, rolling_windows))}"
    timeseries_cache_path = os.path.join(cache_dir, f"{cache_key}_timeseries.parquet")
    stats_cache_path = os.path.join(cache_dir, f"{cache_key}_stats.parquet")
    
    if os.path.exists(timeseries_cache_path) and os.path.exists(stats_cache_path):
        df_timeseries = pd.read_parquet(timeseries_cache_path)
        df_stats = pd.read_parquet(stats_cache_path)
        return df_timeseries, df_stats
    else:
        print(f"No cached results found for {dependent_variable}")
        return None, None

# Usage
dependent_variable = 'your_variable_name'
df_timeseries, df_stats = load_cached_variable_results(dependent_variable)
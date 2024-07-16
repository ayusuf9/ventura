import pandas as pd
import numpy as np
import pickle
import os
from functools import lru_cache

@lru_cache(maxsize=None)
def calculate_and_cache_correlations(df_universe, df_dependent, dependent_variable_name, rolling_windows):
    results = {}
    for window in rolling_windows:
        [df_timeseries, df_stats] = run_rolling_corr_calc(
            df_universe,
            df_dependent,
            dependent_variable_name,
            rolling_windows=[window]
        )
        results[window] = {
            'timeseries': df_timeseries,
            'stats': df_stats
        }
    
    # Save results to disk
    with open('correlation_results.pkl', 'wb') as f:
        pickle.dump(results, f)
    
    return results

def load_cached_correlations():
    if os.path.exists('correlation_results.pkl'):
        with open('correlation_results.pkl', 'rb') as f:
            return pickle.load(f)
    return None






import streamlit as st

# Calculate and cache correlations (run this once, preferably in a separate script)
# rolling_windows = [1, 3, 5, 7]
# all_correlations = calculate_and_cache_correlations(df_universe, df_dependent, dependent_variable_name, tuple(rolling_windows))

# In the Streamlit app
@st.cache_data
def get_cached_correlations():
    return load_cached_correlations()

def main():
    all_correlations = get_cached_correlations()
    
    if all_correlations is None:
        st.error("Cached correlation data not found. Please run the calculation script first.")
        return

    with st.container():
        rolling_wind = st.selectbox("Select Rolling Window", [1, 3, 5, 7], index=3)
        
        df_timeseries = all_correlations[rolling_wind]['timeseries']
        df_stats = all_correlations[rolling_wind]['stats']

        noneditable_columns = list(df_stats.columns)
        df_stats["Plot"] = False
        df_stats.index = df_stats["Variable Name"]
        df_stats = df_stats.drop("Variable Name", axis=1)

        df_timeseries = (
            df_timeseries
            .rename(columns={'Variable Name': 'pricingDate'})
            .set_index('pricingDate')
        )

        years_options = ['1 Year', '3 Years', '5 Years', '7 Years', 'Max']
        selected_years = st.selectbox('Select the number of years:', years_options, index=4)

        # Display results
        st.write("Statistics:")
        st.dataframe(df_stats)
        
        st.write("Time Series:")
        st.line_chart(df_timeseries)

if __name__ == "__main__":
    main()
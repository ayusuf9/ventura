import numpy as np

def normalize_and_scale(values, min_size, max_size, exponent=0.5):
    if len(values) > 0:
        min_val, max_val = values.min(), values.max()
        if min_val == max_val:
            return np.full(len(values), (min_size + max_size) / 2)
        normalized = (values - min_val) / (max_val - min_val)
        # Apply non-linear scaling
        normalized = normalized ** exponent
        return normalized * (max_size - min_size) + min_size
    else:
        return []

# Apply sizing to the entire dataset
if key == "All":
    size_column = "AvgActiveDur"
else:
    size_column = "ADC Abs"

big_df2["sizes"] = normalize_and_scale(big_df2[size_column].abs(), 5, 25, exponent=0.5)
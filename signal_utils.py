"""Compute a rolling-mean-based binary trading signal.

Calculates a rolling mean of the 'close' column and generates a binary signal
where 1 means close is above the rolling mean (bullish) and 0 means at or
below (or insufficient history).

For the initial (window - 1) rows where the rolling mean is NaN due to
insufficient data, the signal defaults to 0 ("no signal") rather than
producing a false positive.
"""

import pandas as pd


def compute_signal(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """Compute rolling mean and binary signal on the 'close' column.

    Args:
        df: DataFrame containing at least a 'close' column.
        window: Rolling window size for the mean calculation.

    Returns:
        A new DataFrame with 'rolling_mean' and 'signal' columns added.
    """
    df = df.copy()

    # Compute rolling mean; first (window - 1) rows will be NaN
    df["rolling_mean"] = df["close"].rolling(window=window).mean()

    # Rows with insufficient history (NaN rolling_mean) default to a
    # "no signal" (0) state rather than a false positive.
    df["signal"] = 0
    mask = df["rolling_mean"].notna() & (df["close"] > df["rolling_mean"])
    df.loc[mask, "signal"] = 1

    # Ensure signal is integer type
    df["signal"] = df["signal"].astype(int)

    return df

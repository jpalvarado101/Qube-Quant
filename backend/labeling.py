import pandas as pd
import numpy as np

def label_outcomes(df: pd.DataFrame, horizon_days: int = 5, threshold: float = 0.01) -> pd.Series:
    df = df.sort_values('date')
    close = df['adj_close'] if 'adj_close' in df.columns else df['close']
    fut_ret = close.shift(-horizon_days) / close - 1.0
    labels = np.where(fut_ret > threshold, 2, np.where(fut_ret < -threshold, 0, 1))
    return pd.Series(labels, index=df.index)

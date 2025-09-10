import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator

THRESH = 0.002  # 0.2% threshold

def make_labels(df: pd.DataFrame, threshold: float = THRESH) -> pd.Series:
    ret1 = df['Close'].pct_change().shift(-1)
    y = ret1.copy()
    y[:] = 0
    y[ret1 > threshold] = 1
    y[ret1 < -threshold] = -1
    return y.dropna()

def make_features(df: pd.DataFrame) -> pd.DataFrame:
    feats = pd.DataFrame(index=df.index)
    feats['ret1'] = df['Close'].pct_change()
    feats['sma5'] = df['Close'].rolling(5).mean() / df['Close'] - 1
    feats['sma20'] = df['Close'].rolling(20).mean() / df['Close'] - 1
    feats['rsi14'] = RSIIndicator(df['Close'], window=14).rsi() / 100.0
    feats['vol_z'] = (np.log1p(df['Volume']) - np.log1p(df['Volume']).rolling(20).mean()) / (np.log1p(df['Volume']).rolling(20).std() + 1e-6)
    feats = feats.replace([np.inf, -np.inf], np.nan).dropna()
    return feats

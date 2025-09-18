import pandas as pd
import ta

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values('date').copy()
    close = df['adj_close'] if 'adj_close' in df.columns else df['close']

    # RSI
    df['rsi_14'] = ta.momentum.RSIIndicator(close=close, window=14).rsi()

    # MACD
    macd = ta.trend.MACD(close=close)
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()

    # EMAs
    df['ema_20'] = ta.trend.EMAIndicator(close=close, window=20).ema_indicator()
    df['ema_50'] = ta.trend.EMAIndicator(close=close, window=50).ema_indicator()

    # Returns
    df['ret_1d'] = close.pct_change(1)
    df['ret_5d'] = close.pct_change(5)

    # ATR
    df['vol_atr'] = ta.volatility.AverageTrueRange(
        high=df['high'], low=df['low'], close=close, window=14
    ).average_true_range()

    return df

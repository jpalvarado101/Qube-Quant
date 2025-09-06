import numpy as np
import pandas as pd

def equity_curve(actions: np.ndarray, prices: np.ndarray, cost=0.0005) -> pd.Series:
    pos = 0
    eq = [1.0]
    for t in range(1, len(prices)):
        a = actions[t-1]
        target = {0:pos,1:1,2:-1}[a]
        if target != pos:
            eq[-1] -= cost
            pos = target
        ret = pos * (prices[t]/prices[t-1]-1.0)
        eq.append(eq[-1] * (1+ret))
    return pd.Series(eq)

def metrics_from_equity(eq: pd.Series) -> dict:
    rets = eq.pct_change().dropna()
    sharpe = float((rets.mean() / (rets.std()+1e-9)) * (252**0.5))
    maxdd = float(((eq.cummax()-eq)/eq.cummax()).max())
    return {"final": float(eq.iloc[-1]), "sharpe": sharpe, "maxdd": maxdd}
# from fastapi import FastAPI
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from stable_baselines3 import PPO
# import numpy as np
# import pandas as pd
# import requests, uuid, os
# from .db import SessionLocal
# from .data import load_prices, make_features
# from .sentiment import score_headlines
# from .envs.trading_env import SimpleTradingEnv
# from .evaluate import equity_curve, metrics_from_equity
# app = FastAPI()

# class TrainIn(BaseModel):
#     run_id: str
#     symbols: list[str]
#     start: str
#     end: str
#     algo: str = "PPO"
#     alpha_sent: float = 0.5
#     window: int = 64
# API_URL = os.getenv("API_URL", "http://api:8000")
# @app.post("/train")
# async def train(body: TrainIn):
#     db: Session = SessionLocal()
#     # For simplicity: single symbol
#     sym = body.symbols[0]
#     df = load_prices(db, sym, body.start, body.end)
#     # Placeholder: no real news ingestion here; set sent=0, could be extended to query News table
#     sent_series = pd.Series(0.0, index=df.index)
#     feats = make_features(df, alpha_sent=body.alpha_sent,sent_series=sent_series)
#     aligned = df.loc[feats.index]
#     X = feats.values.astype(np.float32)
#     prices = aligned['c'].values.astype(np.float32)
#     env = SimpleTradingEnv(features=X, prices=prices)
#     model = PPO("MlpPolicy", env, verbose=0)
#     model.learn(total_timesteps=50_000)
#     # Rollout for signals
#     obs, _ = env.reset()
#     actions = []
#     for _ in range(len(prices)-1):
#         a, _ = model.predict(obs, deterministic=True)
#         actions.append(int(a))
#         obs, r, done, trunc, info = env.step(int(a))
#         if done or trunc: 
#             break
#     import datetime as dt
#     ts = aligned['ts'] if 'ts' in aligned.columns else aligned.index
#     signals = pd.DataFrame({"ts": ts[1:len(actions)+1], "action": actions,    "price": aligned['c'].values[1:len(actions)+1]})
#     eq = equity_curve(np.array(actions), prices)
#     m = metrics_from_equity(eq)
#     # Save to API tables
#     from sqlalchemy import text
#     q_run = text("UPDATE runs SET status='finished', finished_at=now(),    metrics_json=:m WHERE id=:rid")
#     db.execute(q_run, {"m": m, "rid": body.run_id}); db.commit()
#     for _, r in signals.iterrows():
#         db.execute(text("""
#         INSERT INTO
#         signals(run_id,symbol,ts,action,confidence,price,pnl_1d,pnl_5d)
#         VALUES(:run,:sym,:ts,:a,0.0,:p,NULL,NULL)
#         """), {"run": body.run_id, "sym": sym, "ts": r['ts'], "a":
#         int(r['action']), "p": float(r['price'])})
#     db.commit(); db.close()
#     # Optional webhook
#     try:
#         requests.post(f"{API_URL}/webhooks/train-complete", json={"run_id":body.run_id}, timeout=2)
#     except Exception:
#         pass
#     return {"ok": True, "metrics": m}
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np, pandas as pd
import yfinance as yf
from .sentiment import score_headlines
from .indicators import rsi

app = FastAPI()

class AnalyzeIn(BaseModel):
    symbol: str
    alpha_sent: float = 0.5

@app.post("/analyze")
async def analyze(body: AnalyzeIn):
    sym = body.symbol.upper()
    hist = yf.download(sym, period="365d", interval="1d", auto_adjust=True)
    if hist.empty:
        raise HTTPException(400, detail="No price data")
    df = hist.reset_index().rename(columns=str.lower)
    df['ret1']  = df['close'].pct_change().fillna(0)
    df['vol20'] = df['close'].pct_change().rolling(20).std().bfill()
    df['rsi14'] = rsi(df['close']).bfill()/100.0
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    df['macd'] = (macd - signal)

    try:
        news = yf.Ticker(sym).news or []
        titles = [n.get('title','') for n in news][-50:]
    except Exception:
        titles = []
    sent, p_pos, p_neg = score_headlines(titles)
    sent *= body.alpha_sent

    rsi_term  = (df['rsi14'].iloc[-1] - 0.5) * 2
    macd_term = float(np.tanh(df['macd'].iloc[-1] / (df['close'].iloc[-1]*1e-4 + 1e-9)))
    tech_score  = 0.6*rsi_term + 0.4*macd_term
    final_score = 0.7*tech_score + 0.3*sent
    tau = 0.15
    action = 1 if final_score >  tau else 2 if final_score < -tau else 0
    confidence = float(1/(1+np.exp(-4*abs(final_score))))

    return {
        "symbol": sym,
        "price": float(df['close'].iloc[-1]),
        "action": action,
        "action_label": {0:"HOLD",1:"BUY",2:"SELL"}[action],
        "confidence": round(confidence*100, 2),
        "components": {
            "tech_score": round(float(tech_score),4),
            "sentiment":  round(float(sent),4),
            "final_score":round(float(final_score),4)
        }
    }

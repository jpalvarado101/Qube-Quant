from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session
from stable_baselines3 import PPO
import numpy as np
import pandas as pd
import requests, uuid, os
from .db import SessionLocal
from .data import load_prices, make_features
from .sentiment import score_headlines
from .envs.trading_env import SimpleTradingEnv
from .evaluate import equity_curve, metrics_from_equity
app = FastAPI()

class TrainIn(BaseModel):
    run_id: str
    symbols: list[str]
    start: str
    end: str
    algo: str = "PPO"
    alpha_sent: float = 0.5
    window: int = 64
API_URL = os.getenv("API_URL", "http://api:8000")
@app.post("/train")
async def train(body: TrainIn):
    db: Session = SessionLocal()
    # For simplicity: single symbol
    sym = body.symbols[0]
    df = load_prices(db, sym, body.start, body.end)
    # Placeholder: no real news ingestion here; set sent=0, could be extended to query News table
    sent_series = pd.Series(0.0, index=df.index)
    feats = make_features(df, alpha_sent=body.alpha_sent,sent_series=sent_series)
    aligned = df.loc[feats.index]
    X = feats.values.astype(np.float32)
    prices = aligned['c'].values.astype(np.float32)
    env = SimpleTradingEnv(features=X, prices=prices)
    model = PPO("MlpPolicy", env, verbose=0)
    model.learn(total_timesteps=50_000)
    # Rollout for signals
    obs, _ = env.reset()
    actions = []
    for _ in range(len(prices)-1):
        a, _ = model.predict(obs, deterministic=True)
        actions.append(int(a))
        obs, r, done, trunc, info = env.step(int(a))
    if done or trunc: break
    import datetime as dt
    ts = aligned['ts'] if 'ts' in aligned.columns else aligned.index
    signals = pd.DataFrame({"ts": ts[1:len(actions)+1], "action": actions,    "price": aligned['c'].values[1:len(actions)+1]})
    eq = equity_curve(np.array(actions), prices)
    m = metrics_from_equity(eq)
    # Save to API tables
    from sqlalchemy import text
    q_run = text("UPDATE runs SET status='finished', finished_at=now(),
    metrics_json=:m WHERE id=:rid")
    db.execute(q_run, {"m": m, "rid": body.run_id}); db.commit()
    for _, r in signals.iterrows():
        db.execute(text("""
        INSERT INTO
        signals(run_id,symbol,ts,action,confidence,price,pnl_1d,pnl_5d)
        VALUES(:run,:sym,:ts,:a,0.0,:p,NULL,NULL)
        """), {"run": body.run_id, "sym": sym, "ts": r['ts'], "a":
        int(r['action']), "p": float(r['price'])})
    db.commit(); db.close()
    # Optional webhook
    try:
        requests.post(f"{API_URL}/webhooks/train-complete", json={"run_id":body.run_id}, timeout=2)
    except Exception:
        pass
    return {"ok": True, "metrics": m}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
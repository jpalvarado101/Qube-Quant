import pickle
import pandas as pd
from sqlalchemy.orm import Session
from .models import Feature, Ticker, ModelMeta

ACTION_MAP = {0: "SELL", 1: "HOLD", 2: "BUY"}

def latest_model(session: Session) -> ModelMeta:
    return session.query(ModelMeta).order_by(ModelMeta.created_at.desc()).first()

def prepare_latest_features(session: Session, symbol: str):
    t = session.query(Ticker).filter(Ticker.symbol==symbol).one()
    fr = session.query(Feature).filter(Feature.ticker_id==t.id).order_by(Feature.date.desc()).first()
    if not fr:
        raise RuntimeError("No features present. Run train/feature build.")
    row = {k: getattr(fr,k) for k in ['rsi_14','macd','macd_signal','ema_20','ema_50','ret_1d','ret_5d','vol_atr']}
    return fr.date, row

def predict_action(session: Session, symbol: str):
    mm = latest_model(session)
    if not mm:
        raise RuntimeError("No model available. Train one first.")
    with open(mm.path, 'rb') as f:
        obj = pickle.load(f)
    model = obj['model']
    feats = obj['features']
    as_of, row = prepare_latest_features(session, symbol)
    X = pd.DataFrame([row])[feats]
    probs = model.predict_proba(X)[0]
    cls = int(probs.argmax())
    return {
        'symbol': symbol,
        'as_of': str(as_of),
        'action': ACTION_MAP[cls],
        'confidence': float(probs[cls])
    }

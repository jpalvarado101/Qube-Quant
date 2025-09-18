import os
import pickle
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from .models import Price, Feature, Label, ModelMeta, Ticker, Base
from .db import engine
from .indicators import compute_indicators
from .labeling import label_outcomes
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from xgboost import XGBClassifier

Base.metadata.create_all(engine)

FEATURE_COLS = ["rsi_14","macd","macd_signal","ema_20","ema_50","ret_1d","ret_5d","vol_atr"]

def build_feature_table(session: Session, ticker_id: int):
    rows = session.query(Price).filter(Price.ticker_id==ticker_id).all()
    if not rows:
        return None
    df = pd.DataFrame([{
        'date': r.date,
        'open': r.open,
        'high': r.high,
        'low': r.low,
        'close': r.close,
        'adj_close': r.adj_close,
        'volume': r.volume
    } for r in rows]).sort_values('date')
    df = compute_indicators(df)
    for _, r in df.iterrows():
        f = Feature(
            ticker_id=ticker_id,
            date=r['date'],
            rsi_14=None if pd.isna(r['rsi_14']) else float(r['rsi_14']),
            macd=None if pd.isna(r['macd']) else float(r['macd']),
            macd_signal=None if pd.isna(r['macd_signal']) else float(r['macd_signal']),
            ema_20=None if pd.isna(r['ema_20']) else float(r['ema_20']),
            ema_50=None if pd.isna(r['ema_50']) else float(r['ema_50']),
            ret_1d=None if pd.isna(r['ret_1d']) else float(r['ret_1d']),
            ret_5d=None if pd.isna(r['ret_5d']) else float(r['ret_5d']),
            vol_atr=None if pd.isna(r['vol_atr']) else float(r['vol_atr'])
        )
        session.merge(f)
    session.commit()

def build_labels(session: Session, ticker_id: int, horizon_days=5, threshold=0.01):
    rows = session.query(Price).filter(Price.ticker_id==ticker_id).all()
    df = pd.DataFrame([{'date': r.date, 'close': r.close, 'adj_close': r.adj_close, 'high': r.high, 'low': r.low} for r in rows]).sort_values('date')
    y = label_outcomes(df, horizon_days, threshold)
    for (d, a) in zip(df['date'], y):
        if pd.isna(a):
            continue
        session.merge(Label(ticker_id=ticker_id, date=d, action=int(a), horizon_days=horizon_days, threshold=threshold))
    session.commit()

def train_supervised(session: Session, horizon_days=5, threshold=0.01, model_dir="/models"):
    os.makedirs(model_dir, exist_ok=True)
    tickers = session.query(Ticker).all()
    frames = []
    for t in tickers:
        build_feature_table(session, t.id)
        build_labels(session, t.id, horizon_days, threshold)
        f_rows = session.query(Feature).filter(Feature.ticker_id==t.id).all()
        l_rows = session.query(Label).filter(Label.ticker_id==t.id, Label.horizon_days==horizon_days, Label.threshold==threshold).all()
        if not f_rows or not l_rows:
            continue
        fdf = pd.DataFrame([{**{'ticker_id': fr.ticker_id, 'date': fr.date}, **{c:getattr(fr,c) for c in FEATURE_COLS}} for fr in f_rows])
        ldf = pd.DataFrame([{'ticker_id': lr.ticker_id, 'date': lr.date, 'action': lr.action} for lr in l_rows])
        df = fdf.merge(ldf, on=['ticker_id','date']).dropna()
        if not df.empty:
            frames.append(df)
    if not frames:
        raise RuntimeError("No training data available. Did you run ingest?")
    data = pd.concat(frames).sort_values(['ticker_id','date'])
    X = data[FEATURE_COLS]
    y = data['action']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = XGBClassifier(n_estimators=400, max_depth=4, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, objective='multi:softprob', num_class=3)
    model.fit(X_train, y_train)
    print(classification_report(y_test, model.predict(X_test)))
    from datetime import datetime
    path = os.path.join(model_dir, f"xgb_h{horizon_days}_t{threshold:.3f}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pkl")
    with open(path, 'wb') as f:
        pickle.dump({'model': model, 'features': FEATURE_COLS, 'meta': {'horizon_days': horizon_days, 'threshold': threshold}}, f)
    mm = ModelMeta(created_at=datetime.utcnow(), model_type='xgboost_classifier', horizon_days=horizon_days, threshold=threshold, path=path)
    session.add(mm)
    session.commit()
    return path

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models

def upsert_tickers(db: Session, tickers: list[tuple[str, str]]):
    existing = {t.symbol for t in db.execute(select(models.Ticker)).scalars()}
    for sym, cat in tickers:
        if sym not in existing:
            db.add(models.Ticker(symbol=sym, category=cat))
    db.commit()

def insert_candles(db: Session, df: pd.DataFrame, symbol: str):
    rows = []
    for idx, row in df.iterrows():
        def safe_float(val):
            # handle Series or scalar
            if hasattr(val, 'item'):
                val = val.item()
            return 0.0 if pd.isna(val) else float(val)

        rows.append(models.Candle(
            symbol=symbol,
            date=idx.date(),
            open=safe_float(row['Open']),
            high=safe_float(row['High']),
            low=safe_float(row['Low']),
            close=safe_float(row['Close']),
            volume=safe_float(row['Volume']),
        ))
    if rows:
        db.bulk_save_objects(rows, return_defaults=False)
        db.commit()

def load_ohlcv(db: Session, symbol: str) -> pd.DataFrame:
    q = select(models.Candle).where(models.Candle.symbol == symbol).order_by(models.Candle.date)
    rows = db.execute(q).scalars().all()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame([{
        'Date': pd.Timestamp(r.date),  # convert to Timestamp
        'Open': r.open,
        'High': r.high,
        'Low': r.low,
        'Close': r.close,
        'Volume': r.volume,
    } for r in rows]).set_index('Date')
    return df
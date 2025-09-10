# backend/app/crud.py
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models


def upsert_tickers(db: Session, tickers: list[tuple[str, str]]):
# tickers: [(symbol, category), ...]
    existing = {t.symbol for t in db.execute(select(models.Ticker)).scalars()}
    for sym, cat in tickers:
        if sym not in existing:
            db.add(models.Ticker(symbol=sym, category=cat))
    db.commit()


def insert_candles(db: Session, df: pd.DataFrame, symbol: str):
# df index is date, has columns: Open, High, Low, Close, Volume
    rows = []
    for idx, row in df.iterrows():
        rows.append(models.Candle(
            symbol=symbol,
            date=idx.date(),
            open=float(row['Open']),
            high=float(row['High']),
            low=float(row['Low']),
            close=float(row['Close']),
            volume=float(row['Volume']) if not pd.isna(row['Volume']) else 0.0,
            ))
    db.bulk_save_objects(rows, return_defaults=False)
    db.commit()


def load_ohlcv(db: Session, symbol: str) -> pd.DataFrame:
    q = select(models.Candle).where(models.Candle.symbol == symbol).order_by(models.Candle.date)
    rows = db.execute(q).scalars().all()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame([{
    'Date': r.date,
    'Open': r.open,
    'High': r.high,
    'Low': r.low,
    'Close': r.close,
    'Volume': r.volume,
    } for r in rows]).set_index('Date')
    return df
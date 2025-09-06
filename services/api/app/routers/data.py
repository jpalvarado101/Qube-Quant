from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pandas import DataFrame
import pandas as pd
import yfinance as yf
from dateutil import parser
from ..db import get_db
from ..models import Price


router = APIRouter(prefix="/data", tags=["data"])


@router.post("/sync/prices")
def sync_prices(symbol: str, start: str, end: str, db: Session = Depends(get_db)):
    df: DataFrame = yf.download(symbol, start=start, end=end, interval="1d", auto_adjust=True)
    df = df.reset_index().rename(columns=str.lower)
    rows = []
    for _, r in df.iterrows():
        rows.append(Price(symbol=symbol, ts=parser.parse(str(r['date'])), o=float(r['open']), h=float(r['high']), l=float(r['low']), c=float(r['close']), v=float(r['volume'])))
        db.bulk_save_objects(rows)
        db.commit()
    return {"inserted": len(rows)}
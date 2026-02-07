from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..database import get_db
from .. import crud, models
from ..schemas import PredictRequest, PredictResponse
from ..ml import predict_symbol

# router = APIRouter(prefix="/predict", tags=["predict"])
router = APIRouter(tags=["predict"])


@router.post("")
def predict(req: PredictRequest, db: Session = Depends(get_db)) -> PredictResponse:
    sym = req.symbol.upper()
    df = crud.load_ohlcv(db, sym)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data for symbol; ingest first")
    signal, p = predict_symbol(sym, df)
    return PredictResponse(symbol=sym, signal=signal, probability=p)


@router.get("/candles")
def candles(symbol: str = Query(..., min_length=1), limit: int = Query(200, ge=10, le=5000), db: Session = Depends(get_db)):
    sym = symbol.upper()
    df = crud.load_ohlcv(db, sym)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data for symbol; ingest first")
    df = df.tail(limit)
    data = []
    for idx, row in df.iterrows():
        data.append({
            "time": int(idx.timestamp()),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
        })
    return data


@router.get("/latest")
def latest(db: Session = Depends(get_db)):
    subq = (
        select(models.Candle.symbol, func.max(models.Candle.date).label("max_date"))
        .group_by(models.Candle.symbol)
        .subquery()
    )
    stmt = (
        select(models.Candle.symbol, models.Candle.date, models.Candle.close)
        .join(
            subq,
            (models.Candle.symbol == subq.c.symbol) & (models.Candle.date == subq.c.max_date),
        )
        .order_by(models.Candle.symbol)
    )
    rows = db.execute(stmt).all()
    return [
        {"symbol": sym, "date": dt.isoformat(), "close": float(close)}
        for sym, dt, close in rows
    ]

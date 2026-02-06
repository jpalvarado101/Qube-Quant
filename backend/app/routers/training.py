from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from .. import models, crud
from ..ml import train_symbol
from ..schemas import TrainRequest

router = APIRouter(tags=["train"])

@router.post("/")
def train(payload: TrainRequest = Body(default=TrainRequest()), db: Session = Depends(get_db)):
    symbols = payload.symbols
    if not symbols:
        symbols = [t.symbol for t in db.execute(select(models.Ticker)).scalars().all()]
        if not symbols:
            symbols = [r[0] for r in db.execute(select(models.Candle.symbol).distinct()).all()]
    results = []
    for sym in symbols:
        df = crud.load_ohlcv(db, sym)
        if df.empty:
            results.append({"symbol": sym, "status": "no_data"})
            continue
        results.append(train_symbol(sym, df))
    return {"results": results}
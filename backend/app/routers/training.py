from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from .. import models, crud
from ..ml import train_symbol
from ..schemas import TrainRequest

router = APIRouter(tags=["train"])

TRAIN_STATUS = {
    "status": "idle",  # idle | running | done | error
    "current": 0,
    "total": 0,
    "message": "",
}

@router.post("/")
def train(payload: TrainRequest = Body(default=TrainRequest()), db: Session = Depends(get_db)):
    TRAIN_STATUS.update({"status": "running", "current": 0, "total": 0, "message": ""})
    symbols = payload.symbols
    if not symbols:
        symbols = [t.symbol for t in db.execute(select(models.Ticker)).scalars().all()]
        if not symbols:
            symbols = [r[0] for r in db.execute(select(models.Candle.symbol).distinct()).all()]
    TRAIN_STATUS["total"] = len(symbols)
    results = []
    try:
        for i, sym in enumerate(symbols, start=1):
            TRAIN_STATUS.update({"current": i, "message": sym})
            df = crud.load_ohlcv(db, sym)
            if df.empty:
                results.append({"symbol": sym, "status": "no_data"})
                continue
            results.append(train_symbol(sym, df))
        TRAIN_STATUS.update({"status": "done", "message": "complete"})
    except Exception as e:
        TRAIN_STATUS.update({"status": "error", "message": str(e)})
        raise
    return {"results": results}


@router.get("/status")
def train_status():
    return TRAIN_STATUS

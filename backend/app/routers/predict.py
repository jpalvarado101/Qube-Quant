from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud
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

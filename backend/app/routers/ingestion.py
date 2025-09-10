from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import yfinance as yf
from ..database import get_db, Base, engine
from ..schemas import IngestRequest
from .. import crud

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/init")
def init_db():
    Base.metadata.create_all(bind=engine)
    return {"status": "ok"}

@router.post("/yahoo")
def ingest_from_yahoo(req: IngestRequest, db: Session = Depends(get_db)):
    symbols = [s.upper() for s in req.symbols]
    for sym in symbols:
        df = yf.download(sym, start=req.start, end=req.end, progress=False, auto_adjust=False)
        if df.empty:
            continue
        crud.insert_candles(db, df, sym)
    return {"status": "ok", "symbols": symbols}

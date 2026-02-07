from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import yfinance as yf
from ..database import get_db, Base, engine
from ..schemas import IngestRequest
from .. import crud

# router = APIRouter(prefix="/ingest", tags=["ingest"])
router = APIRouter(tags=["ingest"])


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


@router.get("/validate")
def validate_symbol(symbol: str):
    sym = symbol.strip().upper()
    if not sym:
        return {"symbol": sym, "valid": False, "reason": "empty", "name": None}
    try:
        df = yf.download(sym, period="5d", progress=False, auto_adjust=False)
        if df.empty:
            return {"symbol": sym, "valid": False, "reason": "not_found", "name": None}
        name = None
        try:
            info = yf.Ticker(sym).info
            name = info.get("shortName") or info.get("longName")
        except Exception:
            name = None
        return {"symbol": sym, "valid": True, "reason": "ok", "name": name}
    except Exception as e:
        return {"symbol": sym, "valid": False, "reason": str(e), "name": None}

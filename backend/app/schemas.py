from pydantic import BaseModel
from datetime import date

class IngestRequest(BaseModel):
    symbols: list[str]
    start: date | None = None
    end: date | None = None

class TrainRequest(BaseModel):
    symbols: list[str] | None = None  # default: all

class PredictRequest(BaseModel):
    symbol: str

class PredictResponse(BaseModel):
    symbol: str
    signal: str  # BUY/HOLD/SELL
    probability: float | None = None

from pydantic import BaseModel

class PredictRequest(BaseModel):
    symbol: str

class PredictResponse(BaseModel):
    symbol: str
    as_of: str
    action: str  # BUY | HOLD | SELL
    confidence: float

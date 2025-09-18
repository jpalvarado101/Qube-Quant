from fastapi import FastAPI, HTTPException
from .db import SessionLocal, engine
from .models import Base
from .schemas import PredictRequest, PredictResponse
from .predict import predict_action

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Buy/Sell/Hold API")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        db = SessionLocal()
        out = predict_action(db, req.symbol.upper())
        db.close()
        return out
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

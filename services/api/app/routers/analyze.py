from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os, requests

router = APIRouter(prefix="/analyze", tags=["analyze"])
WORKER = os.getenv("WORKER_URL", "http://worker:8001")

class AnalyzeReq(BaseModel):
    symbol: str
    alpha_sent: float = 0.5

@router.post("")
async def analyze(req: AnalyzeReq):
    try:
        r = requests.post(f"{WORKER}/analyze", json=req.model_dump(), timeout=60)
        if r.status_code != 200:
            raise HTTPException(r.status_code, detail=r.text)
        return r.json()
    except requests.RequestException as e:
        raise HTTPException(502, detail=f"Worker unavailable: {e}")

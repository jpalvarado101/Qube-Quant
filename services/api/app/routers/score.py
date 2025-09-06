from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/score", tags=["score"])


class ScoreReq(BaseModel):
    features: list[float]


@router.post("")
async def score(req: ScoreReq):
    # Placeholder: return a dummy action
    return {"action": 0, "confidence": 0.0}
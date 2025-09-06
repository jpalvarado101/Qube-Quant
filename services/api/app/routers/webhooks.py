from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class TrainComplete(BaseModel):
    run_id: str


@router.post("/train-complete")
async def train_complete(body: TrainComplete):
    # placeholder for integrations/notifications
    return {"ok": True}
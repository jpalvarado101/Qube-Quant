from fastapi import APIRouter, BackgroundTasks
from ..schemas import TrainReq, TrainResp
from ..jobs import start_training_job
import uuid


router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/train", response_model=TrainResp)
async def train(req: TrainReq, bg: BackgroundTasks):
    run_id = str(uuid.uuid4())
    bg.add_task(start_training_job, run_id, req.model_dump())
    return {"run_id": run_id, "status": "queued"}
from pydantic import BaseModel
from typing import List, Optional


class TrainReq(BaseModel):
    symbols: List[str]
    start: str
    end: str
    algo: str = "PPO"
    alpha_sent: float = 0.5
    window: int = 64


class TrainResp(BaseModel):
    run_id: str
    status: str
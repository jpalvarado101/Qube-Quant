import uuid, json, os, requests
from datetime import datetime
from sqlalchemy.orm import Session
from .models import Run
from .db import SessionLocal


WORKER_URL = os.getenv("WORKER_URL", "http://worker:8001/train")


def start_training_job(run_id: str, payload: dict):
    # Persist run as queued
    db: Session = SessionLocal()
    run = Run(id=run_id, status="queued", algo=payload.get("algo"), params_json=payload, started_at=datetime.utcnow())
    db.add(run); db.commit()
    try:
        requests.post(WORKER_URL, json={"run_id": run_id, **payload}, timeout=5)
    except Exception:
        run.status = "failed"; db.commit()
    finally:
        db.close()
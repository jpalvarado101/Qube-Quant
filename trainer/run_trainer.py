# trainer/run_trainer.py
import os
import time
import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from backend_like.models import Base, Ticker, Candle
from backend_like.crud import load_ohlcv
from backend_like.ml import train_symbol


# --- lightweight “vendor-in” of backend bits to keep image small ---
# In a real repo, you would make a shared package instead.


# Minimal inlined modules
class Backend:
    def __init__(self):
        from sqlalchemy.orm import declarative_base
        self.Base = declarative_base()


# For brevity, re-use backend/app model definitions in a real shared wheel.
# Here, we assume the trainer container shares the same source tree via COPY or a small package.


# Simpler approach: shell out by calling the API. We’ll just loop-sleep here as a placeholder.


if __name__ == "__main__":
# This file is deliberately minimal; training is exposed via API /train route.
# Use this container later for scheduled retrains or Celery worker.
    print("Trainer idle. Trigger training via POST /train on the API.")
    while True:
        time.sleep(3600)
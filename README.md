# Buy / Sell / Hold – Streamlit + FastAPI + SQLite + (optional Gym RL)

## Quickstart (manual train once, then Docker run)

1) **Conda env (local):**
```bash
conda create -n buy-sell-hold python=3.11 -y
conda activate buy-sell-hold
pip install -r backend/requirements.txt
```

2) **Use SQLite**: copy `.env.example` to `.env` and keep:
```
DATABASE_URL=sqlite:///./data/market.db
API_URL=http://localhost:8000
```

3) **Init DB tables:**
```bash
python -c "from backend.db import engine; from backend.models import Base; Base.metadata.create_all(engine)"
```

4) **Ingest history (FAANG+ default):**
```bash
python -c "from backend.db import SessionLocal; from backend.ingest import fetch_and_store; s=SessionLocal(); fetch_and_store(s); s.close()"
```

5) **Train model → saves under ./models/**
```bash
python -c "from backend.db import SessionLocal; from backend.train import train_supervised; s=SessionLocal(); print(train_supervised(s, model_dir='./models')); s.close()"
```

6) **Run with Docker (backend + Streamlit):**
```bash
docker compose up --build
```
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:8501

7) **Predict via API (example):**
```bash
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"symbol":"AAPL"}'
```

> Educational use only. No financial advice.

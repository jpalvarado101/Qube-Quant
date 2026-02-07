# Qube-Quant

**AI-Driven Market Forecasting Dashboard**  
Qube-Quant is a dashboard for ingesting market data, training per-ticker models, and serving buy/hold/sell signals through a REST API and a responsive web UI.

---

## Demo Video

YouTube: https://youtu.be/TVGM4UomvNU

[![Demo Video](https://img.youtube.com/vi/TVGM4UomvNU/0.jpg)](https://youtu.be/TVGM4UomvNU)

---

## Features

- Yahoo Finance ingestion (historical OHLCV)
- Per-ticker ML training and saved models
- Prediction API with confidence score
- Candlestick chart and latest price list
- Quick ticker shortcuts + custom ticker validation
- Dark/light mode UI
- Dockerized backend, frontend, and database

---

## Repository Structure

- `backend/` API server (FastAPI)
- `frontend/` Web app (React + Tailwind)
- `trainer/` Training container (idle by default)
- `volumes/models/` Saved ML model artifacts
- `docker-compose.yml` Service definitions
- `README.md`

---

## Quick Start (Docker)

### Requirements

- Docker & Docker Compose

### Steps

1. Create an environment file:

```bash
cp .env.example .env
```

2. Start everything:

```bash
docker compose up --build
```

3. Open:

- Backend API: `http://localhost:8000`
- Frontend UI: `http://localhost:5173`

To stop and remove containers:

```bash
docker compose down
```

To wipe the database volume:

```bash
docker compose down -v
```

---

## Local Development (Optional)

### Backend (Python)

```bash
python -m venv .venv
.venv/Scripts/activate   # Windows PowerShell
pip install -r backend/requirements.txt
```

### Frontend (Node)

```bash
cd frontend
npm install
npm run dev
```

---

## Notes

- Models are saved in `volumes/models/` after training.
- The "Update All" action re-ingests all default + custom tickers.
- Validation uses Yahoo Finance; some tickers require suffixes (e.g., `.TO`).

---

## Disclaimer

This project is for educational and demonstration purposes only and does not constitute financial advice. No guarantees are made about accuracy or profitability. Use at your own risk.

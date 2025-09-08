# qube-trader

Dockerized full‑stack RL trading skeleton with FastAPI, Angular, Postgres, Redis, Stable‑Baselines3, FinBERT sentiment.

## Quick start

1. Copy `.env.example` to `.env` and adjust if needed.
2. `docker compose build`
3. `docker compose up` (first run will download ML models; it can take a while)
4. Open http://localhost:4200 for UI, http://localhost:8000/docs for API.

## First run

- Trigger data sync and a demo train from the UI or:
- `curl -X POST http://localhost:8000/data/sync/prices?symbol=AAPL&start=2018-01-01&end=2024-12-31`
- `curl -X POST http://localhost:8000/train -H 'Content-Type: application/json' -d '{"symbols":["AAPL"],"start":"2018-01-01","end":"2024-12-31","algo":"PPO","alpha_sent":0.5,"window":64}'`

## Notes

- Sentiment uses FinBERT locally (CPU ok). You can later switch to provider APIs.
- RL env is simple and intended as a baseline you can extend.

## License

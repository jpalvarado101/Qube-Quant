from fastapi import FastAPI
from .routers import data, runs, score, webhooks, analyze


app = FastAPI(title="qube-trader API")
app.include_router(data.router)
app.include_router(runs.router)
app.include_router(score.router)
app.include_router(webhooks.router)
app.include_router(analyze.router)
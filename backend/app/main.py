from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import ingestion, training, predict

app = FastAPI(title="Stock Signal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion.router)
app.include_router(training.router)
app.include_router(predict.router)

@app.get("/")
def root():
    return {"ok": True}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import ingestion, training, predict

app = FastAPI(title="Stock Signal API")

# List of allowed origins (add more if needed)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # Add production frontend URL here when deployed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Only allow specified origins
    allow_credentials=True,
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)

# Include your routers
app.include_router(ingestion.router, prefix="/ingest")
app.include_router(training.router, prefix="/train")
app.include_router(predict.router, prefix="/predict")

@app.get("/")
def root():
    return {"ok": True}

# Qube‑Quant

**AI‑Driven Market Forecasting Framework**  
Qube‑Quant is a modular system for training, evaluating, and deploying machine learning models that forecast financial markets using historical data.

This project provides tools for:
- Data ingestion and preprocessing
- Model training and evaluation
- Live forecasting via API
- Interactive frontend visualization

---

## Features

- Train and evaluate time series forecasting models
- REST API for serving predictions
- Frontend dashboard for visualization and interaction
- Docker support for easy development and deployment

---

## Repository Structure
├── backend/ // API server (Python/Flask, FastAPI, or similar)
├── frontend/ // Web app (React/TS)
├── trainer/ // Training scripts and model pipelines
├── volumes/models/ // Persisted trained models
├── data/ // Market data CSVs
├── .env.example // Environment variables template
├── docker-compose.yml// Service definitions
└── README.md


---

## Quick Start

### Requirements

- Docker & Docker Compose  
- Python 3.9+ for local development

---

## Configuration

1. Copy the sample environment file:

```bash
cp .env.example .env
```
2. Edit .env to set your data paths, model parameters, and API keys.

3. Ensure your dataset (e.g., CSV price history) is accessible to the training pipeline.


Development Setup
Using Docker

Build and start services:

```bash
docker compose up --build
```
Backend API: http://localhost:8000
Frontend UI: http://localhost:3000

To stop and remove containers:
```bash
docker compose down
```



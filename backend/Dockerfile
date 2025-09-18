FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential curl ca-certificates  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Provide code (compose will also mount)
COPY . /app

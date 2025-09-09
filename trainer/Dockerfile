# trainer/Dockerfile
FROM python:3.11-slim
WORKDIR /trainer
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY run_trainer.py ./
CMD ["python", "run_trainer.py"]
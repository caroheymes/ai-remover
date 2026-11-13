FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PORT=8080

WORKDIR /app

RUN pip install --no-cache-dir fastapi>=0.115.0 uvicorn>=0.30.0 requests>=2.31.0

COPY core/ ./core/
COPY evals/ ./evals/
COPY api.py ./api.py

EXPOSE 8080

CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"]

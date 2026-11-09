FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    BAND_ENABLED=false

COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

COPY safeo_backend ./safeo_backend

EXPOSE 8000

CMD ["sh", "-c", "uvicorn safeo_backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

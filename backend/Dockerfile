FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
# Rebuild the knowledge index on start (small corpus), then serve.
CMD ["sh", "-c", "python -m app.services.ingest && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

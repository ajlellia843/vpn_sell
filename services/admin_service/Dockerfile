FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY shared/ /app/shared/
RUN pip install --no-cache-dir /app/shared

COPY services/admin_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/admin_service/app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

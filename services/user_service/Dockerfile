FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY shared/ /app/shared/
RUN pip install --no-cache-dir /app/shared

COPY services/user_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/user_service/app/ ./app/
COPY services/user_service/alembic.ini ./alembic.ini
COPY services/user_service/alembic/ ./alembic/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

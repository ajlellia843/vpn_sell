FROM python:3.12-slim

WORKDIR /app

COPY shared/ /app/shared/
RUN pip install --no-cache-dir /app/shared

COPY services/bot_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/bot_service/app/ ./app/

CMD ["python", "-m", "app.main"]

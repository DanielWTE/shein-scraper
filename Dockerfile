FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps chromium

COPY . .

RUN mkdir -p output && chmod 777 output

ENV PYTHONUNBUFFERED=1

CMD ["python3", "main.py", "menu"]
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev git

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
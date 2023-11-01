FROM python:3.10-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN chown -R www-data:www-data /tmp && chown -R www-data:www-data /var/log

COPY ./requirements.txt ./requirements.txt

RUN apt-get update \
    && apt-get install -y vim build-essential cron \
    && pip install -r /code/requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY . .
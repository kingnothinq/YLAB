FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY app/*.env /code/
COPY app/*.py /code/app/
COPY db/*.py /code/db/
COPY requirements.txt /code/

WORKDIR /code

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir
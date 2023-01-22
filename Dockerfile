FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /app

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

COPY ./main.py /app

CMD [ "python", "./main.py" ]
FROM python:3.7-slim-buster

WORKDIR /opt/

COPY server/requirements.txt .
RUN pip install -r requirements.txt

COPY server .

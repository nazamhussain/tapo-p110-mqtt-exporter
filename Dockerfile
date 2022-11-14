FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/London

RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir PyP100 paho-mqtt pyyaml

LABEL creator="Nazam Hussain"
LABEL description="Tapo P110 - Energy Usage Exporter"

WORKDIR /exporter

COPY ca.crt .
COPY start.sh .
COPY exporter.py .
COPY devices.yaml .

ENTRYPOINT ["/bin/sh", "-c", "/exporter/start.sh"]

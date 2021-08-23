# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY ./sdk/eventhub ./sdk/eventhub

WORKDIR /app/sdk/eventhub/azure-eventhub
RUN python3 setup.py install

WORKDIR /app/sdk/eventhub/azure-eventhub-checkpointstoreblob
RUN python3 setup.py install

WORKDIR /app/sdk/eventhub/azure-eventhub-checkpointstoreblob-aio
RUN python3 setup.py install

WORKDIR /app/sdk/eventhub/azure-eventhub/stress
RUN pip3 install -r dev_requirement.txt

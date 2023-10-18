FROM mcr.microsoft.com/cbl-mariner/base/python:3

RUN yum update -y

WORKDIR /app

COPY ./scripts /app/stress/scripts

WORKDIR /app/stress/scripts
RUN pip install -r dev_requirements.txt

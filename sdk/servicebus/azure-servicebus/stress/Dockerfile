FROM mcr.microsoft.com/cbl-mariner/base/python:3

RUN yum update -y && yum install -y ca-certificates

WORKDIR /app

COPY ./scripts /app/stress/scripts

WORKDIR /app/stress/scripts
RUN pip install -r dev_requirements.txt

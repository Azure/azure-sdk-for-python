# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.8
FROM mcr.microsoft.com/dotnet/runtime:5.0.9-focal
ARG PYTHON_VERSION
RUN apt-get update
RUN apt-get install software-properties-common git --yes
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt install python${PYTHON_VERSION}-venv -y

RUN python${PYTHON_VERSION} -m venv ./venv
ENV VIRTUAL_ENV /venv
ENV PATH /venv/bin:$PATH

COPY ./scripts /app/stress/scripts

WORKDIR /app/stress/scripts
RUN pip3 install -r dev_requirement.txt

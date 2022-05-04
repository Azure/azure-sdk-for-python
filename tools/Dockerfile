FROM mcr.microsoft.com/dotnet/sdk:5.0.407-focal
LABEL authors="zikalino,scbedd"

RUN apt-get update
RUN apt-get install -y git curl gnupg vim python3 python3-pip git software-properties-common apt-transport-https wget python3-venv nodejs npm libunwind-dev

# install autorest
RUN npm install -g autorest
RUN npm install -g n
RUN n 10.15.0

RUN pip3 install wheel

# clone repos
RUN git clone https://github.com/Azure/azure-rest-api-specs.git --single-branch --depth 1
RUN git clone https://github.com/Azure/azure-sdk-for-python.git --single-branch --depth 1

# setup virtual env
RUN cd /azure-sdk-for-python; python3 -m venv env3.7
ENV VIRTUAL_ENV /azure-sdk-for-python/env3.7
ENV PATH /azure-sdk-for-python/env3.7/bin:$PATH

# run setup
RUN cd /azure-sdk-for-python; python ./scripts/dev_setup.py

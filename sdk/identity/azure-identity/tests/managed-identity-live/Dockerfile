# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
ARG PYTHON_VERSION=3.9

# docker can't tell when the repo has changed and will therefore cache this layer
FROM mcr.microsoft.com/dotnet/runtime:5.0.9-focal as repo
RUN apt-get update
RUN apt-get install -y git 
RUN git clone https://github.com/Azure/azure-sdk-for-python --single-branch --depth 1 /azure-sdk-for-python

FROM mcr.microsoft.com/dotnet/runtime:5.0.9-focal
ARG PYTHON_VERSION
RUN apt-get update
RUN apt-get install software-properties-common git --yes
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt install python${PYTHON_VERSION}-venv -y

COPY --from=repo /azure-sdk-for-python/sdk/identity /sdk/identity
COPY --from=repo /azure-sdk-for-python/sdk/core/azure-core /sdk/core/azure-core
COPY --from=repo /azure-sdk-for-python/sdk/keyvault/azure-keyvault-secrets /sdk/keyvault/azure-keyvault-secrets

RUN python${PYTHON_VERSION} -m venv ./venv
ENV VIRTUAL_ENV /venv
ENV PATH /venv/bin:$PATH

WORKDIR /sdk/identity/azure-identity/tests/managed-identity-live
RUN  pip install --no-cache-dir -r requirements.txt
CMD [ "pytest", "-rs", "-v", "--log-level=DEBUG" ]

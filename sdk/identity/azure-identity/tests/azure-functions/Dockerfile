# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# docker can't tell when the repo has changed and will therefore cache this layer

# internal users should provide MCR registry to build via 'docker build . --build-arg REGISTRY="mcr.microsoft.com/mirror/docker/library/"'
# public OSS users should simply leave this argument blank or ignore its presence entirely
ARG REGISTRY=""

FROM ${REGISTRY}alpine:3.14 as repo
RUN apk --no-cache add git
RUN git clone https://github.com/Azure/azure-sdk-for-python --single-branch --depth 1 /azure-sdk-for-python


FROM mcr.microsoft.com/azure-functions/python:3.0

COPY --from=repo /azure-sdk-for-python/sdk/identity /sdk/identity
COPY --from=repo /azure-sdk-for-python/sdk/core/azure-core /sdk/core/azure-core
COPY --from=repo /azure-sdk-for-python/sdk/keyvault/azure-keyvault-secrets /sdk/keyvault/azure-keyvault-secrets
WORKDIR /sdk/identity/azure-identity/tests/managed-identity-live
RUN pip install --no-cache-dir -r ../managed-identity-live/requirements.txt azure-functions

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY . /home/site/wwwroot

# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# docker can't tell when the repo has changed and will therefore cache this layer

# public OSS users should make this an empty string: 'docker build . --build-arg REGISTRY=""'
ARG REGISTRY="mcr.microsoft.com/mirror/docker/library/"

FROM ${REGISTRY}alpine:3.16 AS repo
RUN apk --no-cache add git
RUN git clone https://github.com/Azure/azure-sdk-for-python --single-branch --depth 1 /azure-sdk-for-python


FROM mcr.microsoft.com/mirror/docker/library/python:3.11-slim

COPY --from=repo /azure-sdk-for-python/sdk/identity /sdk/identity
COPY --from=repo /azure-sdk-for-python/sdk/core/azure-core /sdk/core/azure-core
COPY app.py /app.py
RUN pip install --no-cache-dir /sdk/identity/azure-identity /sdk/core/azure-core aiohttp azure-storage-blob

CMD [ "sleep", "infinity" ]

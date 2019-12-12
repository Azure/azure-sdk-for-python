# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
ARG PYTHON_TAG=2.7

# clone the repo in a separate stage so the build host can cache it
FROM alpine/git as clone
RUN git clone https://github.com/Azure/azure-sdk-for-python --single-branch --branch master --depth 1 /azure-sdk-for-python


FROM python:${PYTHON_TAG}
COPY --from=clone /azure-sdk-for-python /azure-sdk-for-python
# install prerelease azure-identity's dev requirements (in particular, prerelease azure-core)
WORKDIR /azure-sdk-for-python/sdk/identity/azure-identity
RUN pip install -r dev_requirements.txt

# copy the test app, install its requirements (in particular, prerelease azure-identity)
WORKDIR /test
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "pytest", "-v", "-s", "--log-level=DEBUG" ]

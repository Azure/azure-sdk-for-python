# Azure AI Model Inference client library tests for Python

The instructions below are for running tests locally against the live service.

## Prerequisites

Follow the comments in the `tests.env` file in this folder, to set up an AI Foundry project with the
appropriate AI models deployed. Then populate all the environment variables there, and sign in on the console
using "az login --tenant <tenant-id>".

## Setup

- Clone or download this sample repository.
- Open a command prompt window in the folder `sdk\ai\azure-ai-inference`.
- If you want to run tests against the latest published client library, install it by running:
   ```bash
   pip install -r dev_requirements.txt
   pip install azure-ai-inference
   ```
- If you want to run tests against a locally built client library:
    - First build the wheel:
        ```bash
        pip install wheel
        pip install -r dev_requirements.txt
        python setup.py bdist_whee
        ```
    - Then install the resulting local wheel (update version `1.0.0b2` to the current one):
        ```bash
        pip install dist\azure_ai_inference-1.0.0b2-py3-none-any.whl --user --force-reinstall
        ```

## Set environment variables

In addition to the ones in `tests.env`, the following additional environment values **must be** defined,
although not used. Assign any value to them:

```bash
set AI_TENANT_ID=not-used
set AI_CLIENT_ID=not-used
set AI_CLIENT_SECRET=not-used
```

## Configure test proxy

Configure the test proxy to run live service tests without recordings:

```bash
set AZURE_TEST_RUN_LIVE=true
set AZURE_SKIP_LIVE_RECORDING=true
set PROXY_URL=http://localhost:5000
set AZURE_TEST_USE_CLI_AUTH=true
```

## Run tests

To run all tests, type:

```bash
pytest
```

## Additional information

See [test documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md)
for additional information, including how to set proxy recordings and run tests using recordings.

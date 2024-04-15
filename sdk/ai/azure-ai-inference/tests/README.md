# Azure AI Model Inference client library tests for Python

The instructions below are for running tests locally, on a Windows machine, against the live service.

## Prerequisites

The live tests were written against the AI models mentioned below. You will need to deploy them in [Azure AI Studio](https://ai.azure.com/) and have the endpoint and key for each one of them.

- TBD (fro chat completion tests)
- TBD (for embedding tests)
- TBD (for image generation tests)

## Setup

* Clone or download this sample repository.
* Open a command prompt window in the folder `sdk\ai\azure-ai-inference`.
* If you want to run tests against the latest published client library, install it by running:
   ```bash
   pip install azure-ai-inference
   ```
* If you want to run tests against a locally built client library:
    * First build the wheel:
        ```bash
        pip install wheel
        pip install -r dev_requirements.txt
        python setup.py bdist_wheel
        ```
    * Then install the resulting local wheel (update version `1.0.0b1` to the current one):
        ```bash
        pip install dist\azure_ai_inference-1.0.0b1-py3-none-any.whl --user --force-reinstall
        ```

## Set environment variables

The tests read endpoints and keys from environemt variables. See the [Set environment variables](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/samples/README.md#set-environment-variables) section in the samples README.md file for the full list of environment variables that need to be set for all tests to pass.

In addition, the following environment values **must be** defined, although not used. Assign any value to them:
```
set AI_TENANT_ID=not-used
set AI_CLIENT_ID=not-used
set AI_CLIENT_SECRET=not-used
```

## Configure test proxy

Configure the test proxy to run live service tests without recordings:
```
set AZURE_TEST_RUN_LIVE=true
set AZURE_SKIP_LIVE_RECORDING=true
```

## Run tests

To run all tests, type:
```
pytest
```

## Additional information

See [test documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md) for additional information, including how to set proxy recordings and run tests using recordings.
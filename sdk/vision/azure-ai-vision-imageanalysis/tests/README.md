# Azure Image Analysis client library tests for Python

## Running tests locally, on a Windows PC, against the live service

### Prerequisites

See [Prerequisites](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/README.md#prerequisites). Create an Azure resource in one of the GPU-supported regions, otherwise some of the tests will fail.

### Setup

* Clone or download this sample repository.
* Open a command prompt window in the folder `sdk\vision\azure-ai-vision-imageanalysis`.
* If you want to run tests against the latest public Image Analysis client library, install it by running:
   ```bash
   pip install azure-ai-vision-imageanalysis
   ```
* If you want to run tests against a locally built Image Analysis client library:
    * First build the wheel:
        ```bash
        pip install wheel
        pip install -r dev_requirements.txt
        python setup.py bdist_wheel
        ```
    * Then install the resulting local wheel (update version `1.0.0b1` to the current one):
        ```bash
        pip install dist\azure_ai_vision_imageanalysis-1.0.0b1-py3-none-any.whl --user --force-reinstall
        ```

### Set environment variables

See [Set environment variables](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/README.md#set-environment-variables).

In addition, the following environment values **must be** defined, although not used. Assign any value to them:

```cmd
set VISION_TENANT_ID=not-used
set VISION_CLIENT_ID=not-used
set VISION_CLIENT_SECRET=not-used
```

### Log in to Azure

Install the Azure CLI and run `az login`, so tests that use Entra ID authentication can pass.

### Configure test proxy

Configure the test proxy to run live service tests without recordings:

```cmd
set AZURE_TEST_RUN_LIVE=true
set AZURE_SKIP_LIVE_RECORDING=true
```

### Run tests

To run all tests, type:

```cmd
pytest
```

### Additional information

See [test documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md) for additional information, including how to set proxy recordings and run tests using recordings.
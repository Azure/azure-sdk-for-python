# Azure Image Analysis client library tests for Python

## Running tests locally, on a Windows PC, against the live service

### Prerequisites

See [Prerequisites](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/README.md#prerequisites). Create an Azure resource in one of the GPU-supported regions, otherwise some of the tests will fail.

### Setup

1. Clone or download this sample repository.
1. Open a command prompt window in the folder `sdk\vision\azure-ai-vision-imageanalysis`.
1. build the Image Analysis client library for Python:
    ```bash
    pip install wheel 
    pip install -r dev_requirements.txt
    python setup.py bdist_wheel
    ```
1. Install the resulting local Image Analysis client library package (updated the version number `1.0.0b1` to the current one):
    ```bash
    pip install dist\azure_ai_vision_imageanalysis-1.0.0b1-py3-none-any.whl --user --force-reinstall
    ```


### Set environment variables

See [Set environment variables](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/README.md#set-environment-variables).

### Configure test proxy

Configure the test proxy to run live service tests without recordings:
```
set AZURE_TEST_RUN_LIVE=true
set AZURE_SKIP_LIVE_RECORDING=true
```

### Run tests

To run all tests, type:
```
pytest
```

### Additional information

See [test documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md) for additional information, including how to set proxy recordings and run tests using recordings.
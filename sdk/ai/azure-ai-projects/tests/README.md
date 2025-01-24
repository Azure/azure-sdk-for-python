# Azure AI Project client library tests for Python

The instructions below are for running tests locally, on a Windows machine, against the live service using a local build of the client library.

## Build and install the client library

- Clone or download this sample repository.
- Open a command prompt window in the folder `sdk\ai\azure-ai-projects`
- Install development dependencies:
    ```bash
    pip install -r dev_requirements.txt
    ```
- Build the package:
    ```bash
    pip install wheel
    python setup.py bdist_wheel
    ```
- Install the resulting wheel (update version `1.0.0b5` to the current one):
    ```bash
    pip install dist\azure_ai_projects-1.0.0b5-py3-none-any.whl --user --force-reinstall
    ```

## Log in to Azure

```bash
az login
```

## Setup up environment variables

Edit the file `azure_ai_projects_tests.env` located in the folder above. Follow the instructions there on how to set up Azure AI Foundry projects to be used for testing, and enter appropriate values for the environment variables used for the tests you want to run.

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

To run tests in a particular folder (`tests\connections` for example):

```bash
pytest tests\connections
```

## Additional information

See [test documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md) for additional information, including how to set proxy recordings and run tests using recordings.

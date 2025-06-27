# Azure AI Project client library tests for Python

The instructions below are for running tests locally, on a Windows machine, against the live service using a local build of the client library.

## Build and install the client library

- Clone or download this sample repository.
- Open a command prompt window in the folder `sdk\ai\azure-ai-projects`
- Install development dependencies:
    ```bash
    pip install -r dev_requirements.txt
    ```
- Install package from sources:
    ```bash
    pip install -e .
    ```

## Log in to Azure

```bash
az login
```

## Setup up environment variables

Copy the file `azure_ai_projects_tests.template.env` (located in the above folder), and save it as file named `azure_ai_projects_tests.env`.
Enter appropriate values for the environment variables used for the tests you want to run.

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

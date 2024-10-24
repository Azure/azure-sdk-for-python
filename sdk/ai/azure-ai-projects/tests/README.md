# Azure AI Project client library tests for Python

The instructions below are for running tests locally, on a Windows machine, against the live service.

## Build and install the client library

- Clone or download this sample repository.
- Open a command prompt window in the folder `sdk\ai\azure-ai-projects`
- If you want to run tests against the latest published client library, install it by running:
   ```bash
   pip install azure-ai-projects
   ```
- If you want to run tests against a locally built client library:
    - First build the wheel:
        ```bash
        pip install wheel
        pip install -r dev_requirements.txt
        python setup.py bdist_wheel
        ```
    - Then install the resulting local wheel (update version `1.0.0b1` to the current one):
        ```bash
        pip install dist\azure_ai_project-1.0.0b1-py3-none-any.whl --user --force-reinstall
        ```

## Log in to Azure

```bash
az login
```

## Setup for running tests in the `agents` folder

```bash
set PROJECT_CONNECTION_STRING_AGENTS_TESTS=<your_connection_string>
```

## Setup for running tests in the `evaluations` folder

## Setup for running tests in the `connections` and `inference` folders

You need an Azure AI Project that has the following:

TODO

Copy the `Project connection string` from the Azure AI Studio and set the following environment variable:

```bash
set AZURE_AI_PROJECTS_CONNECTIONS_TEST_PROJECT_CONNECTION_STRING=<your_connection_string>
set AZURE_AI_PROJECTS_CONNECTIONS_TEST_MODEL_DEPLOYMENT_NAME=<your-azure-openai-model-deployment-name>
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

To run tests in a particular folder (`tests\connections` for example):

```bash
python tests\connections
```

## Additional information

See [test documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md) for additional information, including how to set proxy recordings and run tests using recordings.
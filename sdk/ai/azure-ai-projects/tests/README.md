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
        pip install dist\azure_ai_projects-1.0.0b1-py3-none-any.whl --user --force-reinstall
        ```

## Log in to Azure

```bash
az login
```

## Setup for running tests in the `agents` folder

**Note:** The environment variables required by the test are defined in `agentClientPreparer`. **It is important project name to be the part of environment variable!** For example, the project is `azure_ai_projects` and the variable may be called `azure_ai_projects_connection_string`. The variables without `azure_ai_projects` substrings will be ignored according to logic of `EnvironmentVariableLoader`. The values of these variables will be supplied to kwargs of the unit tests, decorated by `EnvironmentVariableLoader` function.

```bash
set AZURE_AI_PROJECTS_CONNECTION_STRING=<your_connection_string>
set AZURE_AI_PROJECTS_DATA_PATH=<your_blob_containing_product_info_1.md_from_samples>
```

## Setup for running tests in the `evaluations` folder

## Setup for running tests in the `connections` and `inference` folders

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

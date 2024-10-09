# copied from azure-ai-inference TODO update

# Azure AI Assistants client library tests for Python

The instructions below are for running tests locally, on a Windows machine, against the live service.

## Prerequisites

The live tests were written against the AI models mentioned below. You will need to deploy a gpt-4o model in the Azure OpenAI Studio, and have the endpoint and key for it:

- `gpt-4o` on Azure OpenAI (AOAI), for assistants tests

## Setup

- Clone or download this sample repository.
- Open a command prompt window in the folder `sdk\ai\azure-ai-assistants`.
- If you want to run tests against the latest published client library, install it by running:
   ```bash
   pip install azure-ai-assistants
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

Here is the list of environment variables used by the tests:

```bash
# For assistants, including tools
set AZURE_AI_ASSISTANTS_ENDPOINT=https://<endpoint-name>.openai.azure.com/
set AZURE_AI_ASSISTANTS_KEY=<32-char-api-key>
```

In addition, the following environment values **must be** defined, although not used. Assign any value to them:

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

See [test documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md) for additional information, including how to set proxy recordings and run tests using recordings.
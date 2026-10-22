# Azure AI Agents Smoke Test for Python

This directory contains the **live-service and recorded tests** for the Azure AI Agents client library.

## Getting started

These instructions assume you are working on Windows, have
Python 3.9 or later, and want to run the tests against **live service
end-points** using a locally built wheel.

### Clone and prepare the SDK repo

```bash
git clone https://github.com/Azure/azure-sdk-for-python.git
cd azure-sdk-for-python/sdk/ai/azure-ai-agents
```

### Install development dependencies

```bash
pip install -r dev_requirements.txt
```

### Build and install the library locally

```bash
pip install wheel
python setup.py bdist_wheel
pip install dist/azure_ai_agents-*.whl --force-reinstall --user
```

### Authenticate to Azure

```bash
az login
```

### Set required environment variables

Edit **`azure_ai_agents_tests.env`** one level above this folder and populate
it with the IDs / endpoints of the Azure AI Foundry project you will test
against.

## Key concepts

* **Live vs Recorded tests** by default tests run through the test-proxy so
  recordings can be created/replayed.  
  Set the variables below to force **live** execution:

  
```bash
  set AZURE_TEST_RUN_LIVE=true
  set AZURE_SKIP_LIVE_RECORDING=true
  set PROXY_URL=http://localhost:5000
  set AZURE_TEST_USE_CLI_AUTH=true
```


* **Authentication** tests rely on `DefaultAzureCredential`.  
  When `AZURE_TEST_USE_CLI_AUTH=true`, the credential falls back to the Azure
  CLI token obtained via `az login`.

## Examples

Run **all** tests:

```bash
pytest
```

Run a **single** test file:

```bash
pytest tests/test_agents_basic.py
```

Run tests **with HTTP logging**:

```bash
pytest -s -o log_cli=true -o log_cli_level=INFO
```

## Troubleshooting

| Symptom | Fix |
| ------- | ---- |
| `azure.core.exceptions.ClientAuthenticationError` | Ensure `az login` was executed and the correct subscription is selected. |
| Resource not found | Verify the endpoint / project IDs in `azure_ai_agents_tests.env`. |
| Tests appear to hang | Make sure the **test-proxy** is running or unset `PROXY_URL`. |

Enable debug logging to get raw HTTP traces:

```bash
set AZURE_LOG_LEVEL=debug
```

## Next steps

1. Review the test documentation to learn about the proxy recorder and test matrix.  
2. Explore the main package README for feature-level samples and usage
   guidance.

## Contributing

We welcome pull requests that add new scenarios, improve coverage, or refine
the test infrastructure. Follow the same contribution guidelines as the main
repo:

1. Fork the repository and create a feature branch.  
2. Write or update tests **and** recordings.  
3. Ensure `pytest` passes and `python -m pip install .` still succeeds.  
4. Submit a PR and sign the CLA when prompted.
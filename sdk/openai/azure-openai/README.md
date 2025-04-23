# Azure OpenAI testing placeholder

 > Note: This is not a real package. Its purpose is to run tests/validate Azure OpenAI endpoints with the official [Python SDK](https://github.com/openai/openai-python).

## Prequisites

- Python >= 3.9
- pip install -r dev_requirements.txt

## How to run tests

You can run the tests using pytest. The tests are located in the `tests` directory.

- To run all tests, use the following command:
```bash
pytest tests
```
- To run a specific test file, use the following command:
```bash
pytest tests/test_file.py
```
- To run a specific test, use the following command:
```bash
pytest tests/test_file.py -k test_name
```

## How to write a test

- Test configuration is found in `conftest.py`. This contains the variables that control the API versions we test against, the models we use, and the Azure OpenAI resources we use.
- The `configure` decorator is used to configure the client and necessary kwargs for the test. It takes care of setting up the client and passing the necessary parameters to the test function. The client built is based on the api_type passed in `pytest.mark.parametrize`.
- `build_kwargs` in `conftest.py` is used to build the kwargs for the test. It is where the model name should be set for the test. Any new test file requires that it's kwargs are configured to include which model name to use for Azure vs. OpenAI (due to sometimes different names used between Azure and OpenAI depending on what the deployment was called for Azure).
- Anatomy of a test explained below.


```python
import pytest
import openai

from devtools_testutils import AzureRecordedTestCase # we don't record but this gives us access to nice helpers
from conftest import (
    GPT_4_AZURE,  # Maps to Azure resource with gpt-4* model deployed
    GPT_4_OPENAI, # Maps to OpenAI testing with gpt-4* model
    configure,    # Configures the client and necessary kwargs for the test
    PREVIEW,      # Maps to the latest preview version of the API
    STABLE,       # Maps to the latest stable version of the API
)

@pytest.mark.live_test_only  # test is live only
class TestFeature(AzureRecordedTestCase):  
    @configure  # creates the client and passes through the kwargs to the test
    @pytest.mark.parametrize(  # parametrizes the test to run with Azure and OpenAI clients
        "api_type, api_version",
        [(GPT_4_AZURE, PREVIEW), (GPT_4_OPENAI, "v1")]  # list[tuple(api_type, api_version), ...]
    )
    def test_responses(self, client: openai.AzureOpenAI | openai.OpenAI, api_type, api_version, **kwargs):
        # call the API feature(s) to test
        response = client.responses.create(
            input="Hello, how are you?",
            **kwargs,  # model is passed through kwargs
        )

        # test response assertions
        assert response.id is not None
        assert response.created_at is not None
        assert response.model
        assert response.object == "response"
        assert response.status in ["completed", "incomplete", "failed", "in_progress"]
        assert response.usage.input_tokens is not None
        assert response.usage.output_tokens is not None
```

## Other testing info

- [Live pipeline](https://dev.azure.com/azure-sdk/internal/_build?definitionId=6157) and [weekly pipeline](https://dev.azure.com/azure-sdk/internal/_build?definitionId=6158) for testing Azure OpenAI endpoints.
- Tests for each feature should run against the latest stable (if supported) and preview version of Azure OpenAI.
- Parity testing with non-Azure OpenAI is done on a weekly basis in weekly pipeline.
- Tests are live only, there are no recordings/playback for tests.
- By default uses Entra ID to authenticate the Azure client.
- Test pipeline configuration and environment variables found in [tests.yml](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/openai/tests.yml).

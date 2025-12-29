## Recorded sample tests

Use recorded tests to validate samples with `SyncSampleExecutor` and `AsyncSampleExecutor`. Tests run the sample code, fail on exceptions, and can optionally validate captured `print` output through LLM instructions.

### Prerequisites
- In `.env`, set the variables required by your samples plus `AZURE_TEST_RUN_LIVE=true` and `AZURE_SKIP_LIVE_RECORDING=false` when capturing recordings. CI playback typically uses `AZURE_TEST_RUN_LIVE=false` and `AZURE_SKIP_LIVE_RECORDING=true`.
- Provide sanitized defaults via `servicePreparer` so recordings do not leak secrets.

### Sync example
```python
import pytest
import os
from devtools_testutils import recorded_by_proxy, AzureRecordedTestCase, RecordedTransport
from test_base import servicePreparer
from sample_executor import SyncSampleExecutor, get_sample_paths, SamplePathPasser
from test_samples_helpers import agent_tools_instructions, get_sample_environment_variables_map

class TestSamples(AzureRecordedTestCase):
    @servicePreparer()
    @pytest.mark.parametrize(
        "sample_path",
        get_sample_paths(
            "agents/tools",
            samples_to_skip=[
                "sample_agent_bing_custom_search.py",
                "sample_agent_bing_grounding.py",
                "sample_agent_browser_automation.py",
                "sample_agent_fabric.py",
                "sample_agent_mcp_with_project_connection.py",
                "sample_agent_openapi_with_project_connection.py",
                "sample_agent_to_agent.py",
            ],
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_tools_samples(self, sample_path: str, **kwargs) -> None:
        env_var_mapping = get_sample_environment_variables_map()
        executor = SyncSampleExecutor(self, sample_path, env_var_mapping, **kwargs)
        executor.execute()
        executor.validate_print_calls_by_llm(
            instructions=agent_tools_instructions,
            project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        )        
```

### Async example
```python
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
import os
from devtools_testutils import AzureRecordedTestCase, RecordedTransport
from test_base import servicePreparer
from sample_executor import AsyncSampleExecutor, get_async_sample_paths, SamplePathPasser
from test_samples_helpers import agent_tools_instructions, get_sample_environment_variables_map

class TestSamplesAsync(AzureRecordedTestCase):

    @servicePreparer()
    @pytest.mark.parametrize(
        "sample_path",
        get_async_sample_paths(
            "agents/tools",
            samples_to_skip=[
                "sample_agent_mcp_with_project_connection_async.py",
            ],
        ),
    )
    @SamplePathPasser()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_tools_samples_async(self, sample_path: str, **kwargs) -> None:
        env_var_mapping = get_sample_environment_variables_map()
        executor = AsyncSampleExecutor(self, sample_path, env_var_mapping, **kwargs)
        await executor.execute_async()
        await executor.validate_print_calls_by_llm(
            instructions=agent_tools_instructions,
            project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        )
```

### Key pieces
- `@servicePreparer()`: Supplies sanitized environment variables for playback (often via `EnvironmentVariableLoader`). Use an empty string as the prefix if your variables do not share one.
- Example:
```python
import functools
from devtools_testutils import EnvironmentVariableLoader

servicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "azure_ai_projects_tests",
    azure_ai_projects_tests_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    azure_ai_projects_tests_model_deployment_name="gpt-4o",
    # add other sanitized vars here
)
```
- `@pytest.mark.parametrize`: Drives one test per sample file. Use `samples_to_test` or `samples_to_skip` with `get_sample_paths` / `get_async_sample_paths`.
- `@SamplePathPasser`: Forwards the sample path to the recorder decorators.
- `recorded_by_proxy` / `recorded_by_proxy_async`: Wrap tests for recording/playback. Include `RecordedTransport.HTTPX` when samples use httpx in addition to the default `RecordedTransport.AZURE_CORE`.
- `get_sample_environment_variables_map`: Map test env vars to the names expected by samples. Pass `{}` if you already export the sample variables directly. Example:
```python
def get_sample_environment_variables_map(operation_group: str | None = None) -> dict[str, str]:
    return {
        "AZURE_AI_PROJECT_ENDPOINT":  "azure_ai_projects_tests_project_endpoint",
        "AZURE_AI_MODEL_DEPLOYMENT_NAME": "azure_ai_projects_tests_model_deployment_name",
        # add other mappings as needed
    }
```
- `execute` / `execute_async`: Run the sample; any exception fails the test.
- `validate_print_calls_by_llm`: Optionally validate captured print output with LLM instructions and an explicit `project_endpoint` (and optional `model`).

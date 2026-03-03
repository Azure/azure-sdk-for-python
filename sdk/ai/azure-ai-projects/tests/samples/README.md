# Recorded sample tests

Use recorded tests to validate samples with `SyncSampleExecutor` and `AsyncSampleExecutor`. Tests run the sample code, fail on exceptions, and can optionally validate captured `print` output through LLM instructions.

## Prerequisites

- In `.env`, set the variables required by your samples plus `AZURE_TEST_RUN_LIVE=true` and `AZURE_SKIP_LIVE_RECORDING=false` when capturing recordings. CI playback typically uses `AZURE_TEST_RUN_LIVE=false` and `AZURE_SKIP_LIVE_RECORDING=true`.
- Provide sanitized defaults via `servicePreparer` so recordings do not leak secrets. All mandatory environment variables used by the tests/samples must be specified in `servicePreparer` (as sanitized values) so playback can run without access to real secrets.

**VS Code tip (record a single sample):** Open the **Testing** tab, expand the pytest tree to find the specific sample test case (for example, one parameterized case for a particular `sample_path`), then right-click it and choose **Run Test** (or **Debug Test**). Make sure your `.env` (or your test run environment) includes `AZURE_TEST_RUN_LIVE=true` and `AZURE_SKIP_LIVE_RECORDING=false` so that run captures a new recording for just that sample.

## Sample test logging

Optionally enable logging to capture sample execution results in log files (useful for monitoring and alerting):

```bash
# In .env - uncomment to enable logging
SAMPLE_TEST_ERROR_LOG=<sample_filename>_errors_<timestamp>.log
SAMPLE_TEST_FAILED_LOG=<sample_filename>_failed_<timestamp>.log
SAMPLE_TEST_PASSED_LOG=<sample_filename>_success_<timestamp>.log
```

Log types:

- **`SAMPLE_TEST_ERROR_LOG`**: Sample crashed with an exception during execution
- **`SAMPLE_TEST_FAILED_LOG`**: Sample ran successfully but LLM validation failed (incorrect output)
- **`SAMPLE_TEST_PASSED_LOG`**: Sample ran successfully and LLM validation passed (correct output)

Logs are written to the system's temp directory with the specified filename format. Each log includes the sample path, status/error details, exception traceback (for errors), and all captured print statements.

## Sync example

```python
import pytest
from devtools_testutils import recorded_by_proxy, AzureRecordedTestCase, RecordedTransport
from test_base import servicePreparer
from sample_executor import SyncSampleExecutor, get_sample_paths, SamplePathPasser
from test_samples_helpers import agent_tools_instructions, get_sample_env_vars

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
        env_vars = get_sample_env_vars(kwargs)
        executor = SyncSampleExecutor(
            self,
            sample_path,
            env_vars=env_vars,
            **kwargs,
        )
        executor.execute()
        executor.validate_print_calls_by_llm(
            instructions=agent_tools_instructions,
            project_endpoint=kwargs["azure_ai_project_endpoint"],
        )        
```

## Async example

```python
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import AzureRecordedTestCase, RecordedTransport
from test_base import servicePreparer
from sample_executor import AsyncSampleExecutor, get_async_sample_paths, SamplePathPasser
from test_samples_helpers import agent_tools_instructions, get_sample_env_vars

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
        env_vars = get_sample_env_vars(kwargs)
        executor = AsyncSampleExecutor(
            self,
            sample_path,
            env_vars=env_vars,
            **kwargs,
        )
        await executor.execute_async()
        await executor.validate_print_calls_by_llm_async(
            instructions=agent_tools_instructions,
            project_endpoint=kwargs["azure_ai_project_endpoint"],
        )
```

## Key pieces

- `@servicePreparer()`: A custom helper you create for your test suite. It supplies sanitized environment variables for playback (often via `EnvironmentVariableLoader`). The name is up to you; these examples call it `servicePreparer` by convention.
- Example:

```python
import functools
from devtools_testutils import EnvironmentVariableLoader

servicePreparer = functools.partial(
    EnvironmentVariableLoader,
        "",
        azure_ai_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
        azure_ai_model_deployment_name="gpt-4o",
    # add other sanitized vars here
)
```

- If all your test environment variables share a prefix (for example `azure_ai_projects_tests`), pass that prefix as the second positional
    argument to `EnvironmentVariableLoader` and include the prefix on the keys you provide.  For example:

```python
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
- `execute` / `execute_async`: Run the sample; any exception fails the test.
- `validate_print_calls_by_llm` / `validate_print_calls_by_llm_async`: Optionally validate captured print output with LLM instructions and an explicit `project_endpoint` (and optional `model`).
- `kwargs` in the test function: A dictionary with environment variables in key and value pairs.

## Optional test environment variables mapping

If you need to remap the values provided by your fixtures to the environment-variable names the sample expects, build an `env_vars` dictionary and pass it to the sample executors. When your fixtures already supply sample-ready names/values, you can omit `env_vars`.

```python
env_vars = {
    "AZURE_AI_PROJECT_ENDPOINT": kwargs["TEST_AZURE_AI_PROJECT_ENDPOINT"],
    "AZURE_AI_MODEL_DEPLOYMENT_NAME": kwargs["TEST_AZURE_AI_MODEL_DEPLOYMENT_NAME"],
}
executor = SyncSampleExecutor(self, sample_path, env_vars=env_vars, **kwargs)
```

## Optional environment variables

To run the “hero path” of a sample, your `@servicePreparer` should provide all mandatory environment variables.
If a sample supports optional environment variables (for optional features/paths), use `@additionalSampleTests` to generate additional recorded test cases with those optional variables set.

```python
from sample_executor import AdditionalSampleTestDetail, additionalSampleTests

@servicePreparer()
@additionalSampleTests(
    [
        AdditionalSampleTestDetail(
            sample_filename="sample_agent_computer_use.py",
            env_vars={"COMPUTER_USE_MODEL_DEPLOYMENT_NAME": "sanitized_model"},
            test_id="computer_use",
        ),
        AdditionalSampleTestDetail(
            sample_filename="sample_agent_computer_use.py",
            env_vars={
                "COMPUTER_USE_MODEL_DEPLOYMENT_NAME": "sanitized_model",
                "SOME_FLAG": "true",
            },
            test_id="sample_agent_computer_use_with_flag",
        ),
    ]
)
@pytest.mark.parametrize(
    "sample_path",
    get_sample_paths(
        "agents/tools",
        samples_to_skip=[],
    ),
)
@SamplePathPasser()
@recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
def test_agent_tools_samples(self, sample_path: str, **kwargs) -> None:
    ...
```

Notes:

- `AdditionalSampleTestDetail.env_vars` is a mapping of **sample env-var name** -> **sanitized playback value**.
  - Live/recording (`AZURE_TEST_RUN_LIVE=true`): reads the real value from your environment (for example, from `.env`) and sanitizes it to the provided playback value.
  - Playback (`AZURE_TEST_RUN_LIVE=false`): sets each key to the provided playback value.
- `AdditionalSampleTestDetail.test_id` customizes the parameter id used for that variant.
  - If omitted, the id is auto-generated from the sample filename and env-var keys (for example, `sample_agent_computer_use-[COMPUTER_USE_MODEL_DEPLOYMENT_NAME]`).
  - If provided, it becomes the full parameter id for that variant (no filename prefix).
  - If the auto-generated id makes the recording file path too long (most commonly on Windows), the recording file may fail to generate; set a short `test_id` (and keep it unique across all parametrized cases).
- In VS Code's **Testing** tab, these show up as additional parameterized cases for the same test, using the parameter id.

## Allowing LLM validation failures

LLM validation may produce false alarms when it doesn't understand sample output well enough, incorrectly flagging correct samples as failed. To keep the CI pipeline green while monitoring these validation issues, you can specify samples that are allowed to pass despite LLM validation failures.

Define an allowlist at the top of your test file:

```python
# Samples that are allowed to pass even when LLM validation fails
ALLOWED_LLM_VALIDATION_FAILURES = {
    "sample_agent_basic.py",
    "sample_workflow_multi_agent.py",
}
```

Pass the allowlist to the executor:

```python
executor = SyncSampleExecutor(
    self,
    sample_path,
    allowed_llm_validation_failures=ALLOWED_LLM_VALIDATION_FAILURES,
    **kwargs,
)
```

Behavior:

- **Samples in the allowlist:** Pass the test even when LLM validation fails. A warning message is printed to the console, and a failed report is still generated (if `SAMPLE_TEST_FAILED_LOG` is configured in `.env`).
- **Samples not in the allowlist:** Fail the test when LLM validation fails (existing behavior).
- **All samples:** Execution errors (exceptions) always fail the test, regardless of the allowlist.

This allows you to dismiss false alarms from LLM validation while keeping the CI pipeline green. Failed reports are still generated for monitoring purposes.

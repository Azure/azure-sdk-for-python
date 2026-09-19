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

## Set up test resources

Most tests target a manually-configured Foundry project. The Voice Agents realtime live tests
(`tests\agents\test_voice_agent_realtime_livetest*.py`, and `test_voice_agent_*.py` under
`tests\agents\`) can instead have their Foundry account/project provisioned automatically using
`test-resources.bicep` (located in the above folder) and the
[test resource scripts](https://github.com/Azure/azure-sdk-for-python/tree/main/eng/common/TestResources),
e.g.:

```powershell
../../../eng/common/TestResources/New-TestResources.ps1 -ServiceDirectory ai -Location westus2
```

This provisions a Cognitive Services `AIServices` account with a default project and grants the
test principal the built-in *Foundry User* role, then prints a `FOUNDRY_PROJECT_ENDPOINT` value to
add to your `.env` file (the live tests authenticate with Azure AD via `DefaultAzureCredential`,
so no API key is needed). The live tests use a service-hosted realtime model
(`VoiceModelType.MANAGED`), so no project deployment is needed -- set
`FOUNDRY_VOICE_AGENT_MODEL` to a managed model identifier such as `gpt-realtime` (see
`azure.ai.projects.models.VoiceModelType` for the managed-vs-self-deployed distinction).
`-Location westus2` is required -- without it, the account is created in the resource group's
default location, which may not support the managed model in managed mode (observed as a
`bad_request: Model 'gpt-realtime' is not supported in managed mode in this region` error).

## Live-test CI pipeline

`tests.yml` (in this package's root directory) wires the same `test-resources.bicep` into an
Azure Pipelines live-test stage (`archetype-sdk-tests.yml`), scoped to `azure-ai-projects` and
filtered to only the tests marked `@pytest.mark.live_test_only`
(`tests/agents/test_voice_agent_realtime_livetest.py`). The rest of the package's tests aren't
included, since they depend on additional resources/connections this template doesn't provision
(telephony phone numbers, fine-tuning jobs, hosted-agent images, Bing/SharePoint/GitHub
connections, ...), and some (telephony) place real phone calls. As with any new `tests.yml`, an
actual Azure DevOps pipeline definition pointing at this file still needs to be created by the
engineering-systems team before it runs in CI.

The async counterpart (`test_voice_agent_realtime_livetest_async.py`, marked
`@pytest.mark.live_test_only_async`) is deliberately excluded from this pipeline for now:
azure-core's aiohttp transport doesn't decompress Brotli (`Content-Encoding: br`) responses as of
azure-core 1.41.0, and the Foundry service responds with `br`-encoded bodies, which breaks these
async tests in CI. They can still be run locally against an environment with a Brotli-capable
aiohttp body helper. Once azure-core adds Brotli support (or another workaround is adopted) and
the async tests are verified to pass unattended, update `tests.yml`'s `TestMarkArgument` to
include them again.

## Setup up environment variables

Copy the file `.env.template` (located in the above folder), and save it as file named `.env`.
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

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
`test-resources.json` (located in the above folder) and the
[test resource scripts](https://github.com/Azure/azure-sdk-for-python/tree/main/eng/common/TestResources),
e.g.:

```powershell
../../eng/common/TestResources/New-TestResources.ps1 -ServiceDirectory ai
```

This provisions a Cognitive Services `AIServices` account with a default project and grants the
test principal the built-in *Foundry User* role, then prints `FOUNDRY_PROJECT_ENDPOINT` and
`FOUNDRY_PROJECT_API_KEY` values to add to your `.env` file. A realtime-capable voice model (for
example `gpt-realtime`) still needs to be deployed to the project manually -- its deployment name
goes in `FOUNDRY_VOICE_MODEL_NAME` -- since model deployment isn't automated by this template.

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

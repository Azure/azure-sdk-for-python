# Microsoft Azure SDK for Python

This is the Microsoft Azure Edgeactions Management Client Library.
This package has been tested with Python 3.10+.
For a more complete view of Azure libraries, see the [azure sdk python release](https://aka.ms/azsdk/python/all).

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Prerequisites

- Python 3.10+ is required to use this package.
- [Azure subscription](https://azure.microsoft.com/free/)

### Install the package

```bash
pip install azure-mgmt-edgeactions
pip install azure-identity
```

### Authentication

By default, [Microsoft Entra](https://learn.microsoft.com/entra/fundamentals/what-is-entra) token authentication depends on correct configuration of the following environment variables.

- `AZURE_CLIENT_ID` for Azure client ID.
- `AZURE_TENANT_ID` for Azure tenant ID.
- `AZURE_CLIENT_SECRET` for Azure client secret.

In addition, Azure subscription ID can be configured via environment variable `AZURE_SUBSCRIPTION_ID`.

With above configuration, client can be authenticated by following code:

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.edgeactions import EdgeActionsMgmtClient
import os

sub_id = os.getenv("AZURE_SUBSCRIPTION_ID")
client = EdgeActionsMgmtClient(credential=DefaultAzureCredential(), subscription_id=sub_id)
```

## Examples

Code samples for this package can be found at:
- [Search Edgeactions Management](https://docs.microsoft.com/samples/browse/?languages=python&term=Getting%20started%20-%20Managing&terms=Getting%20started%20-%20Managing) on docs.microsoft.com
- [Azure Python Mgmt SDK Samples Repo](https://aka.ms/azsdk/python/mgmt/samples)


## Troubleshooting

### Running contributor tests

Install the package and its test dependencies in a virtual environment, following the
[Python SDK testing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md).
Run the following from `sdk\edgeactions\azure-mgmt-edgeactions` in PowerShell:

```powershell
python -m pip install -r dev_requirements.txt
python -m pip install -e .
$env:AZURE_TEST_RUN_LIVE = "false"
python -m pytest tests -q
```

`test_edgeactions_contract.py` uses synthetic HTTP responses for both synchronous and asynchronous
clients. It checks the stable API version, request bodies, paging, delete polling, and
service-error propagation without Azure credentials, a test proxy, or cloud resources.
These tests do not prove that the service accepts or rejects a request.
`test_lifecycle_helpers.py` checks deterministic deployment payloads and cleanup ownership.
`test_recording_sanitizers.py` checks redaction with a local test proxy, without Azure calls.
The three lifecycle scenarios use recorded service responses in playback mode. Only the
two generated resource-group listing smoke tests remain live-only and are skipped offline.

For persistent local configuration, use this package's [.env.example](.env.example).
Copy it to `.env` at the worktree root, or merge its settings into an existing `.env`
without overwriting other configuration. From this package directory:

```powershell
if (-not (Test-Path ..\..\..\.env)) {
    Copy-Item .\.env.example ..\..\..\.env
}
```

Replace the subscription placeholder before running live tests. The test setup loads
`.env` automatically; variables already set in the shell take precedence. The example
defaults to offline execution. Keep `.env` local and uncommitted.

| Mode | `AZURE_TEST_RUN_LIVE` | `AZURE_SKIP_LIVE_RECORDING` |
| --- | --- | --- |
| Record: call Azure and save HTTP recordings | `true` | `false` |
| Live: call Azure without saving recordings | `true` | `true` |
| Playback / offline: no Azure calls | `false` | Ignored |

These are standard repository test settings, not EdgeActions-specific flags.
`AZURE_SKIP_LIVE_RECORDING` is not a playback switch. Lifecycle playback requires usable
recordings and fails if they are missing or do not match. No Python source edits are
needed to switch modes. Offline unit tests use mocks and do not require recordings.
If mode variables were set with PowerShell `$env:...`, remove those overrides or open
a fresh terminal before relying on the values in `.env`.

`test_edge_actions_mgmt_client_lifecycle_test.py` contains live, recordable scenarios for tag replacement
and clearing, invalid updates (including rejection of an empty PATCH body), version deployment and code retrieval (file and ZIP),
default-version swaps, and execution-filter CRUD. They follow the Azure PowerShell
EdgeAction scenarios, using the Python SDK test framework for authentication and resource
ownership. The existing resource-group list smoke tests are also live-only.
Live tests list only within the test resource group or a test-created action, not across
the subscription. Subscription-wide listing and pagination are covered offline for
both clients, so recordings do not capture EdgeActions from other resource groups in
a shared subscription. Any separate live subscription-list check must run without
recording or in an isolated test subscription.

### Record and replay the lifecycle scenarios

Run both phases from `sdk\edgeactions\azure-mgmt-edgeactions`, with your virtual
environment activated and using the same explicit test path. The examples use
`python` from that environment, whether it is located at the package or worktree root.

First, remove/comment out `AZURE_RESOURCEGROUP_NAME` in the worktree-root `.env` to
use fresh random groups. Select an authorized **test** subscription and account:

```powershell
az login # Needed only if Azure CLI is not already signed in.
az account set --subscription "<test-subscription-id>"
if ($LASTEXITCODE -ne 0) { throw "Could not select the test subscription." }
$env:AZURE_SUBSCRIPTION_ID = az account show --query id -o tsv
if ($LASTEXITCODE -ne 0) { throw "Could not read the test subscription." }
$env:AZURE_TEST_USE_CLI_AUTH = "true"
$env:AZURE_TEST_USE_PWSH_AUTH = "false"
$env:AZURE_TEST_USE_AZD_AUTH = "false"
Remove-Item Env:AZURE_RESOURCEGROUP_NAME -ErrorAction SilentlyContinue

# Record: calls Azure, saves sanitized recordings, and attempts resource cleanup.
$env:AZURE_TEST_RUN_LIVE = "true"
$env:AZURE_SKIP_LIVE_RECORDING = "false"
python -m pytest tests\test_edge_actions_mgmt_client_lifecycle_test.py -v -s
if ($LASTEXITCODE -ne 0) { throw "Recording failed; resolve the failure before playback." }
```

Expect three passing scenarios. Then replay those same scenarios without contacting Azure:

```powershell
$env:AZURE_TEST_RUN_LIVE = "false"
python -m pytest tests\test_edge_actions_mgmt_client_lifecycle_test.py -v -s
if ($LASTEXITCODE -ne 0) { throw "Playback failed; inspect the recording mismatch." }

# Optional broader check: includes lifecycle playback and all offline unit tests.
python -m pytest tests -q
```

Playback should report three passed lifecycle tests, not skipped. `tests` selects the
contributor suite; the explicit lifecycle filename selects only those three scenarios.
Always supply a test path: omitting it (including through an unset PowerShell variable)
also discovers the separate `generated_tests` directory. `-q`, `-v`, and `-s`
change console output, not recording mode. For streamed INFO logs, add
`--log-cli-level=INFO`. Console logs are not sanitized by recording sanitizers.
Keep `AZURE_TEST_RUN_LIVE=false` for ordinary offline development.

Alternatively, use the signed-in Azure PowerShell account with
`AZURE_TEST_USE_PWSH_AUTH=true` and set `AZURE_SUBSCRIPTION_ID` to its selected test
subscription. Service-principal authentication uses the standard `AZURE_TENANT_ID`,
`AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` variables. Do not commit credentials.

The account needs permission to create/delete resource groups and manage
`Microsoft.Cdn/edgeActions`. The subscription must support EdgeActions. New lifecycle
test resource groups are in `eastus` and follow the standard framework naming convention
`rgpy-pythonsdk-edgeaction-test-<random suffix>`. The same prefix is used by the
sync/async resource-group listing smoke tests. Leave `AZURE_RESOURCEGROUP_NAME` unset for
a fresh group per scenario. EdgeAction names use `eapython<test-derived suffix>`:
the framework generates distinct names for different scenarios and repeats each name
for playback. The fresh resource group isolates repeated live runs; names are not
replaced wholesale with `Sanitized`. Renaming a scenario or its test module changes
the generated resource name and requires fresh recordings.

EdgeActions use the Standard SKU;
EdgeActions and their children use `global`. The framework tags temporary groups and initiates their deletion
after each scenario. Scenario cleanup waits for deletion of its EdgeAction and children.

Optionally, reuse an existing dedicated test group. For example, if you have created
a group named `edgeaction-pythonsdk-tests-rg`, set
`AZURE_RESOURCEGROUP_NAME=edgeaction-pythonsdk-tests-rg` in your local `.env`.
This name is only an example, not a default or a group the tests create automatically.
The framework does not create or delete a supplied group; the scenarios still create and
delete their own `eapython...` actions within it. Leave this variable unset for isolated
groups. Never point these tests at a production group.

The proxy starts automatically when recording or replaying. Re-record after changes
that affect requests or expected service responses. Older captures made before the
playback-safe sanitizer setup may have lost resource names/IDs or `Location` paths;
replace those captures with a live recording rather than guessing the erased values.

Following the existing [Network management tests](../../network/azure-mgmt-network/tests/conftest.py),
package setup preserves `Location` headers and resource names; it also preserves resource IDs,
as the [JavaScript EdgeActions tests](https://github.com/Azure/azure-sdk-for-js/blob/main/sdk/edgeactions/arm-edgeactions/test/public/utils/recordedClient.ts)
and the .NET/Java ARM frameworks do. Shared Python setup already preserves
`operation-location`. Only the overly broad defaults for those fields are disabled,
not the credential sanitizers.

Package sanitizers in `tests/conftest.py` replace the `t`, `c`, `s`, and `h` polling-query values in URLs,
headers, and bodies, along with unnecessary trace-header values. Configured identity
and credential values are matched literally, including secrets containing regex
metacharacters. Cookies, OAuth token fields, and `systemData` creator/modifier identities
are also sanitized. Polling operation paths/IDs, API versions, and functional test payloads
are preserved for reliable playback. These rules are not a blanket guarantee that every
future response is safe to publish: review new recording fields before sharing them.

Review sanitization and
follow the testing guide's recording-migration instructions to publish recordings to
`azure-sdk-assets` and commit the resulting `assets.json` pointer.

## Next steps

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues)
section of the project. 

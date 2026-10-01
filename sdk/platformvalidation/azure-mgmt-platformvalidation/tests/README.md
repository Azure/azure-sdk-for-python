# PlatformValidation recorded integration tests

These handwritten tests follow the [management-plane testing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/tests.md)
and the [Python SDK testing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md). Do not edit the
regeneration-owned files in `generated_tests/`.

## Coverage

Both synchronous and asynchronous clients exercise CloudValidation create, get,
list by resource group, list by subscription, update and delete. Assertions cover
resource identity, location, provisioning state, tags, description persistence and
HTTP 404 after deletion. Separate tests check GET of a nonexistent resource.
The lifecycle tests identify their own resource in list results, without assuming
the subscription or resource group is empty.

Each lifecycle test also checks that `<cvname>-mrg` does not exist before creation
and verifies its absence after CloudValidation cleanup, including failure cleanup.
These resource-management SDK checks are recorded with the scenario. Absence must
be observed three consecutive times, with up to 60 checks spaced 10 seconds apart
in live mode. Playback skips the sleeps. A leftover managed group fails the test;
the tests never explicitly delete a managed group or unrelated resources.

## Setup

Use an isolated Python environment and, from this package directory, install the
repository's test tooling and the local SDK:

```powershell
python -m pip install -r dev_requirements.txt -e .
```

Follow the repository's [feed configuration](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md#package-index-configuration)
and [authentication instructions](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#configure-test-variables).
Use an approved test subscription with `Microsoft.PlatformValidation` registered,
a supported CloudValidation location, and permission for resource-group creation
and deletion, resource-group existence checks, the CloudValidation lifecycle, and
subscription-list operations.

Configure `AZURE_SUBSCRIPTION_ID` and `PLATFORMVALIDATION_LOCATION`.
Live mode requires the service location; playback uses a sanitized placeholder,
not a live target. `ResourceGroupPreparer` creates a uniquely named prerequisite
resource group per test and requests its deletion afterward, as described in the
[management-plane example](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/tests.md#example-2-basic-preparer-usage).
Resource-group metadata is stored in `eastus`; this does not select the
CloudValidation service location.

Leave `AZURE_RESOURCEGROUP_NAME` unset for automatic provisioning. The standard
preparer also supports this variable to reuse an existing group, which it will
not create or delete. That is optional, not a requirement. Resource-group
preparation is excluded from HTTP recordings and uses a fake group during playback.
The resource-management package in `dev_requirements.txt` supports the preparer;
it is not a runtime dependency of the PlatformValidation SDK.

For user authentication, choose the documented `AZURE_TEST_USE_*_AUTH` option.
For Azure CLI authentication, sign in using `az login` and set
`AZURE_TEST_USE_CLI_AUTH=true`. Put the approved subscription and service location
in the repository-root, git-ignored `.env`, or provide them as environment
variables. Do not commit subscription-specific target configuration.
For service-principal authentication with `EnvironmentVariableLoader`, set
`PLATFORMVALIDATION_TENANT_ID`, `PLATFORMVALIDATION_CLIENT_ID` and
`PLATFORMVALIDATION_CLIENT_SECRET`; the loader maps them to the shared credential
variables. Never commit credentials or a local `.env`.

## Record, replay and publish recordings

Live mode calls Azure and incurs resource creation/deletion. Only run it after the
target and resource mutations are approved. Run serially; do not run concurrent
copies of the same test against the same resource group.

```powershell
$env:AZURE_TEST_RUN_LIVE = "true"
$env:AZURE_SKIP_LIVE_RECORDING = "false"
python -m pytest tests -v

$env:AZURE_TEST_RUN_LIVE = "false"
python -m pytest tests -v
```

For an offline check before recordings exist:

```powershell
$env:AZURE_TEST_RUN_LIVE = "false"
python -m pytest tests --collect-only -q
python -m pytest tests/test_managed_group_cleanup.py -q
```

The cleanup unit tests use mocked resource-management calls, not live requests
or fabricated HTTP recordings. They check delayed deletion, reappearance,
timeout and request-error handling for both sync and async clients.

The test proxy starts through `conftest.py`. The first command captures real HTTP
interactions; the second verifies the same tests against those recordings without
calling Azure. Do not fabricate recordings, skip tests to hide missing recordings,
or treat collection-only checks as a successful playback run.

Sanitizers remove cookies instead of substituting `Set-Cookie`, which could make
playback clients send cookies absent from the original requests. Signed ARM
polling query parameters are redacted consistently in URLs and response headers.
The checked-in `assets.json` references the sanitized live recordings used by
playback; normal playback does not require Azure credentials.

Before publishing, inspect all recordings for sensitive values, including
unrelated resources returned by subscription listing. Follow the official
[initial recording migration](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/recording_migration_guide.md)
to upload recordings to `Azure/azure-sdk-assets` and generate `assets.json`. This
requires asset-repository write access. Include the generated, verified pointer
with the test PR, not secrets or an invented asset tag.

The lifecycle tests refuse to overwrite an existing resource and check the test
tag before deletion. Cleanup is attempted on failure. If creation fails or times
out, inspect the target for late provisioning and service-managed resources;
an immediate 404 is not proof that provisioning cannot complete later. A cleanup
failure fails the test and must be resolved before recording again. The shared
resource-group preparer requests deletion without waiting for completion and can
log deletion errors instead of failing, so also verify live resource-group cleanup
before considering a recording run complete.

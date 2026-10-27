# PlatformValidation recorded integration tests

These handwritten tests follow the [Python SDK testing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md)
and [management-plane testing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/tests.md).
Do not edit regeneration-owned files in `generated_tests/`.

## Verified coverage

Twenty recorded scenarios, ten per client, exercise all 25 SDK methods in both
sync and async clients. Mocked regressions separately exercise ownership, cleanup,
timeouts, serialization and sanitization. Method coverage does not mean every
input, authorization boundary or deployment has been tested.

| Operation group | Methods exercised per client | Main assertions |
| --- | --- | --- |
| `cloud_validations` | `begin_create_or_update`, `get`, `begin_update`, `begin_delete`, `list_by_resource_group`, `list_by_subscription` | Identity, location, state, tags, description, existing-resource PUT, missing GET and post-delete 404 |
| `validation_execution_plans` | `begin_create_or_update`, `get`, `begin_update`, `begin_delete`, `list_by_resource_group` | Tags/description/configuration PATCH, omitted-field preservation, existing-resource PUT, lists and post-delete 404 |
| `execution_plan_runs` | `begin_create_or_update`, `get`, `begin_delete`, `list_by_execution_plan` | New run completes with one passing boot test; deletion removes the run and its test results |
| `validation_test_runs` | `get`, `list_by_execution_plan_run` | Exact parent identity, completed state, pass counts, timestamps and absence of failure details |
| `validation_tests` | `get`, `list_by_subscription` | Public entry discovery and exact provider-global identity |
| `validation_test_versions` | `get`, `list` | Public version discovery and exact parent/version identity |
| `validation_test_categories` | `get`, `list_by_subscription` | Public category discovery and exact identity |
| `operation_status` | `get` | Direct polling of the supported route returned by a plan PATCH |
| `operations` | `list` | Expected permission names, display metadata and data-action flags |

Existing-resource PUT is covered for CloudValidation and execution plans.
`execution_plan_runs.begin_create_or_update` is covered by creation of a new run,
not replay of an existing completed run.

Catalog requests are subscription-scoped; the approved deployment returns
provider-global IDs beginning `/providers/Microsoft.PlatformValidation/`.
Tests assert that exact identity. Description-only PATCH tests verify that
omitted tags and configuration are preserved.

Run serially; do not re-submit an existing execution merely to test its
update-shaped SDK entrypoint.

## Setup and authentication

From this package directory, use an isolated virtual environment and install
the repository tooling, test dependencies and local SDK:

```powershell
python -m pip install -r dev_requirements.txt -e .
```

Follow the repository's [feed configuration](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md#package-index-configuration)
and [test authentication guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#configure-test-variables).
Use an approved subscription with `Microsoft.PlatformValidation` registered,
a supported location, and permission to create/delete test resource groups and
exercise the listed operations. The resource-management SDK is a test dependency,
not a runtime dependency of PlatformValidation.

For Azure CLI authentication, sign in with `az login`, then configure:

```powershell
$env:AZURE_SUBSCRIPTION_ID = "<approved-test-subscription-id>"
$env:PLATFORMVALIDATION_LOCATION = "<supported-service-location>"
$env:AZURE_TEST_USE_CLI_AUTH = "true"
$env:AZURE_TEST_USE_PWSH_AUTH = "false"
$env:AZURE_TEST_USE_AZD_AUTH = "false"
Remove-Item Env:\AZURE_RESOURCEGROUP_NAME -ErrorAction SilentlyContinue
```

Other documented authentication modes remain available. With the environment
loader, service-principal inputs are `PLATFORMVALIDATION_TENANT_ID`,
`PLATFORMVALIDATION_CLIENT_ID` and `PLATFORMVALIDATION_CLIENT_SECRET`.
Never commit credentials or local target configuration.

`AzureMgmtRecordedTestCase` creates framework-managed clients and selects
live/fake credentials. Async tests use `get_credential(..., is_async=True)` and
`create_client_from_credential`, and close their credentials.

## Execution prerequisites and cleanup

The full workload lifecycle uses this preparer order:

```python
@ExecutionEnvironmentPreparer()
@ExecutionResourceGroupPreparer(
    name_prefix="platformvalidationexec", random_name_enabled=True, location="eastus"
)
@ExecutionPrerequisitesPreparer()
@recorded_by_proxy
def test_execution_lifecycle(self, platformvalidation_location, resource_group, cloud_validation_name):
    ...
```

The async scenario uses the same preparers and `recorded_by_proxy_async`.
Preparers create a fresh parent RG and CloudValidation outside recordings.
The service must create `<cvname>-mrg`; setup verifies its `managedBy` association.
There is no manual MRG creation, role assignment or fallback.
Playback supplies fake prerequisites and creates no Azure resources.

Cleanup order is EPR and cascaded VTRs, VEP, CV, service-managed MRG disappearance,
then the owned parent RG. Exact IDs, ownership tags, run descriptions and terminal
states are required. Unexpected siblings, active resources and orphan results
block deletion. The parent is retained if prerequisite cleanup is unconfirmed,
even when ARM's generic resource list is empty.

CV deletion retries only HTTP 409 `CannotDeleteResource`, at most 30 attempts
ten seconds apart, checking that the plan list is empty before each attempt.
Other errors still fail. Managed-group absence requires three consecutive checks,
with at most 60 checks ten seconds apart; playback skips sleeps.
Managed groups are never deleted directly.

Plan-only/update scenarios borrow an approved, successfully provisioned CV.
Read-only result scenarios additionally need a completed, one-test boot run:

```powershell
$env:PLATFORMVALIDATION_EXECUTION_RESOURCE_GROUP = "<approved-parent-group>"
$env:PLATFORMVALIDATION_EXECUTION_CLOUD_VALIDATION = "<approved-cv>"
$env:PLATFORMVALIDATION_EXECUTION_OWNERSHIP = "borrowed-parent"
$env:PLATFORMVALIDATION_EXECUTION_PLAN = "<completed-plan>"
$env:PLATFORMVALIDATION_EXECUTION_RUN = "<completed-run>"
```

Borrowed-parent tests never create/delete the CV, MRG or parent group. Update
tests create and delete only their own new plans and submit no executions.
Read-only result tests create or delete nothing.

Creation tests also require `PLATFORMVALIDATION_SOURCE_VHD_URI`: supply an
approved HTTPS Linux Gen1 X64 image through a secure process environment.
Do not place a signed URI in source, shell history, `.env`, logs or recordings.
Playback uses `https://example.invalid/image.vhd` and needs no image access.
The approved fixture uses `Standard_D4s_v3` and one
`compute-vmimagevalidation-vm-boot-test` step.

The embedded configuration uses `microsoft.validate/executionPlan.v0` and
`ExecutionPlan`, separately from ARM API version `2026-08-01-preview`.

## Record, replay and publish

The following maps the official guide to this suite:

| Guide step | Implementation or command |
| --- | --- |
| Install tooling and local library | `python -m pip install -r dev_requirements.txt -e .` |
| Select framework credentials | Base test case and environment loaders; no handwritten credential construction |
| Prepare auxiliary resources | Framework preparers, excluded from recordings |
| Record actual service traffic | `recorded_by_proxy` / `recorded_by_proxy_async` and the `test_proxy` fixture |
| Sanitize secrets | Package-scoped fixtures plus image-input and list-response sanitizers |
| Replay the same tests | Set `AZURE_TEST_RUN_LIVE=false`; run `python -m pytest tests -q` |
| Publish updates | Supported `manage_recordings.py push`; include its generated `assets.json` |
| Verify contribution | Replay the full included suite from a clean checkout using published assets; inspect PR CI |

Start with a single provisioning scenario:

```powershell
$env:AZURE_TEST_RUN_LIVE = "true"
$env:AZURE_SKIP_LIVE_RECORDING = "false"
python -m pytest tests\test_cloud_validations.py::TestCloudValidations::test_cloud_validation_lifecycle -v --maxfail=1
```

Then record its async equivalent, fresh execution lifecycles and other configured
scenarios serially. Catalog live tests additionally accept
`PLATFORMVALIDATION_CATALOG_ENDPOINT` and `PLATFORMVALIDATION_CATALOG_TEST`.
The approved retest used regional Canary ARM and the boot catalog entry;
these are environment settings, not public SDK endpoint defaults.

Stop and investigate live failures. Before recording, locate the cache and
preserve unpublished changes:

```powershell
python ..\..\..\scripts\manage_recordings.py locate
```

A failed live test can replace its cached recording. Retain failure evidence
privately and restore that scenario's last-known-good asset, if any.
Do not fabricate recordings, hand-edit failures into successes or publish
failed recordings as passing coverage.

After successful recording:

```powershell
$env:AZURE_TEST_RUN_LIVE = "false"
python -m pytest tests -q
```

The included suite needs no Azure credentials, image URI or real prerequisites
in playback. Inspect recordings for secrets and valid nested JSON before
publication. Sanitizers remove cookies/private headers, redact signed query
values and identity fields, replace image URLs, and redact unrelated resources
in subscription lists while preserving the target identity. The package replaces
the generic SAS sanitizer with an escape-preserving expression; it does not
require changes to shared SDK tooling. Mocked regressions cover nested JSON,
escaped slashes and Unicode escapes.

This package is already migrated to external recording assets. Use the
[recording update workflow](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#update-test-recordings),
not initial migration:

```powershell
python ..\..\..\scripts\manage_recordings.py push
```

This requires asset-repository write access and generates a new tag pointer in
`assets.json`. Verify the tag remotely and replay from a clean checkout without
the old cache or local shared-tool modifications. Commit the generated pointer
with the tests, not recordings, credentials or private diagnostics.

ResourceGroupPreparer can request deletion without waiting. Independently
confirm live parent-group cleanup before declaring a run complete.
Passing playback is evidence for recorded behavior, not a repeatability or
concurrent-live-run claim.

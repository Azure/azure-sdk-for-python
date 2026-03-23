# Scenario Tests for TypeSpec Migration Validation

These tests validate that real-world customer scenarios continue to work correctly
after the TypeSpec migration of the `azure-ai-ml` REST clients. They are designed
to run **live** against a real Azure ML workspace.

## Why These Tests Exist

Kashif's TypeSpec migration branch (`kashifkhan/azure_ai_ml_tsp`) regenerates the
following REST clients from TypeSpec specs instead of Swagger/AutoRest:

- `arm_ml_service` — backs all versioned `ServiceClientXXXX` partials
- `registry_discovery` — `RegistryDiscoveryClient`
- `model_dataplane` — `ModelDataplaneClient`
- `dataset_dataplane` — dataset operations
- `workspace_dataplane` — workspace discovery and metadata
- `runhistory` — job run history and metrics

These tests exercise **complex multi-step customer workflows** that stress these
clients, focusing on edge cases like:

- Round-trip serialization fidelity (tags, properties, descriptions with special chars)
- Nested object structures (search space, early termination, pipeline steps)
- Traffic splitting and metadata updates on endpoints
- Archive/restore lifecycle for assets
- Job cancellation and status transitions
- Workspace connections with credential types

## Test Files

| File | REST Clients Exercised | Scenario | Speed |
|------|----------------------|----------|-------|
| `test_scenario_asset_lifecycle.py` (workspace metadata) | `workspace_dataplane` | Workspace get, datastore list | ~10s |
| `test_scenario_asset_lifecycle.py` (CRUD) | `dataset_dataplane`, `model_dataplane` | Multi-asset CRUD, special chars, archive/restore | ~30s |
| `test_scenario_connections_compute_jobs.py` | `arm_ml_service`, `runhistory` | Connections, identity compute, job cancel/complete lifecycle | ~10-15min |
| `test_scenario_pipeline_train_register.py` | `arm_ml_service`, `runhistory` | 3-step pipeline → model registration with round-trip checks | ~15-20min |
| `test_scenario_sweep_tuning.py` | `arm_ml_service`, `runhistory` | Bayesian sweep with BanditPolicy, config serialization validation | ~15-20min |
| `test_scenario_blue_green_deployment.py` | `arm_ml_service` (endpoints) | Blue-green deployment with traffic shifting, metadata updates | ~20-30min |
| `test_scenario_private_network.py` (read-only) | `arm_ml_service` | Workspace managed-network settings deserialization, outbound rules list | ~10s |
| `test_scenario_private_network.py` (CRUD) | `arm_ml_service` | FQDN & ServiceTag outbound-rule CRUD, update, round-trip serialization | ~2-5min* |

\* CRUD tests require workspace with managed-network isolation enabled (`AllowInternetOutbound` or `AllowOnlyApprovedOutbound`). Skipped on `Disabled` workspaces.

## Setup

### 1. Python environment

These tests run against the **local editable install** of `azure-ai-ml`. Use the
repo's venv (or any venv with the package installed):

```powershell
# From the repo root — the venv at C:\Repos\azure-sdk-for-python\venv already
# has azure-ai-ml and its dependencies installed in editable mode.
& c:\Repos\azure-sdk-for-python\venv\Scripts\Activate.ps1
```

If you need to set up a fresh venv:

```powershell
python -m venv venv
& .\venv\Scripts\Activate.ps1
pip install -e sdk/ml/azure-ai-ml
pip install pytest pytest-timeout azure-identity
```

### 2. Environment variables

Set these before running (PowerShell):

```powershell
$env:ML_SUBSCRIPTION_ID = "<your-subscription-id>"
$env:ML_RESOURCE_GROUP   = "<your-resource-group>"
$env:ML_WORKSPACE_NAME   = "<your-workspace-name>"

# Optional — for service principal auth (falls back to Azure CLI → DefaultAzureCredential)
$env:ML_TENANT_ID     = "..."
$env:ML_CLIENT_ID     = "..."
$env:ML_CLIENT_SECRET = "..."
```

### 3. Workspace requirements

- **Azure CLI login**: `az login` must be completed (unless using SP auth).
- **Storage key auth**: Some tests (model upload) require the workspace storage
  account to allow key-based authentication. If disabled, those tests will
  `pytest.skip()` gracefully.
- **Compute quota**: Tests that create compute need at least 4 vCPU quota for
  `STANDARD_DS3_V2` in the workspace region.

### 4. Test isolation

These tests have their own `pytest.ini` inside `tests/scenario_tests/` that
prevents pytest from loading the parent `tests/conftest.py` (which requires
`devtools_testutils`). **You must run from the `scenario_tests/` directory**
or specify `--rootdir`:

```powershell
cd sdk/ml/azure-ai-ml/tests/scenario_tests
```

## Running

All commands assume you are in `sdk/ml/azure-ai-ml/tests/scenario_tests/` with
env vars set and the correct venv activated.

```powershell
# List all scenarios (no execution)
python -m pytest . -v --co

# Run the fastest test (~10s, no compute)
python -m pytest test_scenario_asset_lifecycle.py::TestScenarioAssetLifecycle::test_workspace_metadata_and_datastore_access -v -s

# Run asset CRUD tests (~30s, no compute)
python -m pytest test_scenario_asset_lifecycle.py -v -s

# Run the full connections + compute + jobs scenario (~10-15min)
python -m pytest test_scenario_connections_compute_jobs.py -v -s --timeout=900

# Run all scenarios (may take 30+ minutes)
python -m pytest . -v -s --timeout=1800

# Run with the repo venv explicitly (if not activated)
& c:\Repos\azure-sdk-for-python\venv\Scripts\python.exe -m pytest . -v -s
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'devtools_testutils'` | Running from wrong directory; parent `conftest.py` is loaded | `cd` into `tests/scenario_tests/` before running |
| `ModuleNotFoundError: No module named 'azure.mgmt'` | Missing `azure-mgmt-core` | `pip install azure-mgmt-core` |
| `ModuleNotFoundError: No module named 'msrest'` | Missing `msrest` | `pip install msrest` (or `pip install -e sdk/ml/azure-ai-ml`) |
| `KeyBasedAuthenticationNotPermitted` | Workspace storage has key auth disabled | Test will `pytest.skip()` automatically; or use a workspace with storage keys enabled |
| `KeyError: 'ML_SUBSCRIPTION_ID'` | Env vars not set | Set `$env:ML_SUBSCRIPTION_ID` etc. |
| `AttributeError: 'dict' object has no attribute '_to_compute_rest_object'` | Identity passed as dict instead of `IdentityConfiguration` | Already fixed — use `IdentityConfiguration(type="system_assigned")` |

## Design Principles

1. **Live mode only** — no mocking, no recordings. These test real service behavior.
2. **try/finally cleanup** — every test cleans up resources even on failure.
3. **Round-trip fidelity** — create → fetch → assert all properties survived serialization.
4. **Edge cases over mirrors** — these don't duplicate azureml-examples; they test
   variations and corner cases (special chars, long descriptions, traffic splits, etc.).
5. **Collision-safe names** — all resource names use `rand_name()` with random suffixes.
6. **Graceful skip** — tests skip (not fail) for infra limitations like disabled storage keys.

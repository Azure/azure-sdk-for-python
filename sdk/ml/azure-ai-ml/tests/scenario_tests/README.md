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
| `test_scenario_batch_endpoint.py` (deploy+invoke) | `arm_ml_service` (endpoints) | Batch endpoint deploy, invoke with data asset, list jobs, config round-trip (does not poll to completion or verify output) | ~15-30min |
| `test_scenario_batch_endpoint.py` (config variations) | `arm_ml_service` (endpoints) | Alternate deployment config (SUMMARY_ONLY, error_threshold=-1), round-trip | ~10-15min |

\* CRUD tests require workspace with managed-network isolation enabled (`AllowInternetOutbound` or `AllowOnlyApprovedOutbound`). Skipped on `Disabled` workspaces.

## Quick Start (Bug Bash)

Copy-paste these commands to go from zero to a passing test in under 2 minutes:

```powershell
# 1. cd into scenario_tests
cd sdk/ml/azure-ai-ml/tests/scenario_tests

# 2. Create & activate a fresh venv
python -m venv .venv
& .\.venv\Scripts\Activate.ps1

# 3. Install the wheel + test deps (replace path to your wheel)
pip install <path-to-azure_ai_ml-wheel>.whl
pip install pytest pytest-timeout

# 4. Set env vars
$env:ML_SUBSCRIPTION_ID = "<your-subscription-id>"
$env:ML_RESOURCE_GROUP   = "<your-resource-group>"
$env:ML_WORKSPACE_NAME   = "<your-workspace-name>"

# 5. Verify with the fastest test (~15s)
python -m pytest test_scenario_asset_lifecycle.py::TestScenarioAssetLifecycle::test_workspace_metadata_and_datastore_access -v -s
```

> **Note:** `azure-identity` and `msrest` are installed automatically as
> dependencies of the wheel — you do **not** need to install them separately.

## Setup (detailed)

### 1. Python environment

These tests run against a **pre-built wheel** of `azure-ai-ml` (a release
candidate produced by the CI pipeline). Install it into a fresh venv:

```powershell
cd sdk/ml/azure-ai-ml/tests/scenario_tests
python -m venv .venv
& .\.venv\Scripts\Activate.ps1

# Install the RC wheel (the same wheel can be used for sample testing
# and manual validation)
pip install <path-to>/azure_ai_ml-<version>-py3-none-any.whl
pip install pytest pytest-timeout
```

> **Tip:** If you have exactly one wheel in the current directory:
> ```powershell
> pip install (Get-Item *.whl).FullName
> ```

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

### 3. Azure CLI login

Make sure you're logged in (unless using SP auth):

```powershell
az login
az account set --subscription "<your-subscription-id>"
```

### 4. Workspace requirements

- **Storage key auth**: Some tests (model upload) require the workspace storage
  account to allow key-based authentication. If disabled, those tests will
  `pytest.skip()` gracefully.
- **Compute quota**: Tests that create compute need at least 4 vCPU quota for
  `STANDARD_DS3_V2` in the workspace region.

### 5. Test isolation

These tests have their own `pytest.ini` inside `tests/scenario_tests/` that
prevents pytest from loading the parent `tests/conftest.py` (which requires
`devtools_testutils`). **You must `cd` into the `scenario_tests/` directory
before running.**

```powershell
cd sdk/ml/azure-ai-ml/tests/scenario_tests
```

## Running

All commands assume you are in `sdk/ml/azure-ai-ml/tests/scenario_tests/` with
env vars set and the `.venv` activated.

```powershell
# List all scenarios (no execution)
python -m pytest . -v --co

# Run the fastest test (~15s, no compute needed)
python -m pytest test_scenario_asset_lifecycle.py::TestScenarioAssetLifecycle::test_workspace_metadata_and_datastore_access -v -s

# Run asset CRUD tests (~30s, no compute)
python -m pytest test_scenario_asset_lifecycle.py -v -s

# Run the full connections + compute + jobs scenario (~10-15min)
python -m pytest test_scenario_connections_compute_jobs.py -v -s --timeout=900

# Run all scenarios (may take 30+ minutes)
python -m pytest . -v -s --timeout=1800
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'devtools_testutils'` | Running from wrong directory; parent `conftest.py` is loaded | `cd` into `tests/scenario_tests/` before running |
| `ModuleNotFoundError: No module named 'azure.mgmt'` | Missing `azure-mgmt-core` (should come with the wheel) | `pip install azure-mgmt-core` |
| `ModuleNotFoundError: No module named 'msrest'` | Missing `msrest` (should come with the wheel) | `pip install msrest` |
| `KeyBasedAuthenticationNotPermitted` | Workspace storage has key auth disabled | Test will `pytest.skip()` automatically; or use a workspace with storage keys enabled |
| `KeyError: 'ML_SUBSCRIPTION_ID'` | Env vars not set | Set `$env:ML_SUBSCRIPTION_ID` etc. (see Quick Start above) |
| `AttributeError: 'dict' object has no attribute '_to_compute_rest_object'` | Identity passed as dict instead of `IdentityConfiguration` | Already fixed — use `IdentityConfiguration(type="system_assigned")` |

## Adding New Scenarios (Bug Bash)

We have a Claude/Copilot skill file at `.copilot/scenario_skill.instructions.md`
that teaches the AI how to generate scenario tests matching our conventions. Use
the following prompt in **GitHub Copilot Chat** (or any Copilot agent) to generate
new scenarios:

### Prompt template

> ```
> Using the skill in .copilot/scenario_skill.instructions.md, generate a new
> scenario test for the azure-ai-ml SDK.
>
> **Feature area:** <AREA>
> **Customer story:** <STORY>
>
> Requirements:
> - Use only public APIs from azure.ai.ml and azure.ai.ml.entities
> - Follow the existing patterns in tests/scenario_tests/ (look at conftest.py
>   fixtures: ml_client, rand_name, credential, wait_for_job)
> - Each test method must do 5+ SDK calls in a realistic multi-step workflow
> - try/finally cleanup for every resource created
> - Round-trip fidelity assertions (create → get → assert properties match)
> - Inline any training scripts via tempfile.TemporaryDirectory
> - No mocking, no devtools_testutils — these run live
> - Test edge cases and variations, not happy-path-only
> ```

### Example prompts for specific areas

**AutoML classification:**
> Using the skill in .copilot/scenario_skill.instructions.md, generate a scenario
> test for AutoML classification. Customer story: A data scientist uploads a CSV
> dataset, creates an AutoML classification job with a 15-minute timeout and
> blocked algorithms, waits for completion, then retrieves the best model and
> registers it. Test edge cases: special chars in display name, custom
> featurization settings, ensemble disabled.

**Batch endpoint with data asset:**
> Using the skill in .copilot/scenario_skill.instructions.md, generate a scenario
> test for batch endpoints. Customer story: An ML engineer creates a batch
> endpoint, deploys a model, invokes the endpoint with a URI folder data asset,
> polls the batch job to completion, and downloads the scoring output. Test edge
> cases: deployment with mini_batch_size, error_threshold, max_concurrency settings.

**Registry cross-workspace:**
> Using the skill in .copilot/scenario_skill.instructions.md, generate a scenario
> test for cross-workspace model sharing via Registry. Customer story: A platform
> team registers an environment and model in a registry, then a workspace user
> references those registry assets in a command job. Test round-trip fidelity of
> registry asset references and verify job completes successfully.

**Datastore & data pipeline:**
> Using the skill in .copilot/scenario_skill.instructions.md, generate a scenario
> test for data pipelines. Customer story: A data engineer registers an Azure Blob
> datastore, creates a uri_folder data asset pointing to it, builds a 2-step
> pipeline (prepare_data → train) where step 1 reads from the data asset and step
> 2 outputs to the datastore path. Verify output data exists after pipeline
> completes.

### Scenario ideas not yet covered

| Area | What to test | Complexity |
|------|-------------|------------|
| AutoML classification/regression | Job config, blocked algos, featurization, best model retrieval | Level 3 |
| Batch endpoints (poll + output) | Poll batch job to completion, download/verify scoring output | Level 4 |
| Registry cross-workspace | Register assets in registry, use in workspace job | Level 5 |
| Distributed training | Multi-node PyTorch/TF command job | Level 3 |
| Managed online endpoint + MLflow | No-code MLflow model deployment | Level 4 |
| Data import job | Import data from external source into workspace | Level 2 |
| Schedule/trigger | Create scheduled pipeline, verify it triggers | Level 3 |
| Feature store | Create feature set, run materialization | Level 3 |
| Responsible AI dashboard | RAI insights on a registered model | Level 5 |
| Serverless compute job | Submit command job without named compute | Level 3 |
| Backward compatibility | A customer submits a pipeline authored with an older SDK version against a newer service. ||
| Network isolation | Private workspace and endpoint creation | |
| Pipeline jobs | Linear pipelines with mixed data types ||
| Pipeline jobs | Parameterized pipelines with complex params and a mix of default and non-default parameters ||
| Parallel jobs | Processing parallel jobs using mount mode ||

## Design Principles

1. **Live mode only** — no mocking, no recordings. These test real service behavior.
2. **try/finally cleanup** — every test cleans up resources even on failure.
3. **Round-trip fidelity** — create → fetch → assert all properties survived serialization.
4. **Edge cases over mirrors** — these don't duplicate azureml-examples; they test
   variations and corner cases (special chars, long descriptions, traffic splits, etc.).
5. **Collision-safe names** — all resource names use `rand_name()` with random suffixes.
6. **Graceful skip** — tests skip (not fail) for infra limitations like disabled storage keys.

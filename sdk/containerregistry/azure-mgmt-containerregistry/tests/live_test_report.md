# Live Test Summary Report — azure-mgmt-containerregistry

**Date:** 2026-03-24  
**Package:** `azure-mgmt-containerregistry` (v15.1.0b1)  
**Python Version:** 3.9.25  
**Test Mode:** Live (`AZURE_TEST_RUN_LIVE=true`)  
**Source Commit:** `c0408d1f3f3a6dbd4cc968c14aa50288a51e13a9`

---

## Overall Result: ❌ ALL TESTS FAILED

| Category | Count |
|----------|-------|
| **Sync tests (errors)** | 3 |
| **Async tests (collection errors)** | 2 |
| **Disabled test files** | 6 |
| **Total active test files** | 4 |
| **Total active test cases** | 6 (3 sync + 3 async) |
| **Passed** | 0 |
| **Failed/Error** | 5 |

---

## Sync Test Results

All 3 sync tests errored during **setup** due to missing Azure credentials (`AZURE_SUBSCRIPTION_ID` not set).

| Test | File | Result | Error |
|------|------|--------|-------|
| `test_operations_list` | `test_container_registry_management_operations_test.py` | ❌ ERROR | `ValueError: Could not get SUBSCRIPTION_ID` |
| `test_registries_list` | `test_container_registry_management_registries_operations_test.py` | ❌ ERROR | `ValueError: Could not get SUBSCRIPTION_ID` |
| `test_registries_list_by_resource_group` | `test_container_registry_management_registries_operations_test.py` | ❌ ERROR | `ValueError: Could not get SUBSCRIPTION_ID` |

### Root Cause

The tests require the following environment variables to be set for live testing:
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`

These credentials were not available in the test environment. The error occurs in `setup_method` when `create_mgmt_client()` calls `get_settings_value("SUBSCRIPTION_ID")`, which fails because `AZURE_SUBSCRIPTION_ID` is not set and no fallback settings file is present.

### Error Traceback (representative)

```
tests/test_container_registry_management_operations_test.py:19: in setup_method
    self.client = self.create_mgmt_client(ContainerRegistryManagementClient)
devtools_testutils/mgmt_recorded_testcase.py:17: in create_mgmt_client
    subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
devtools_testutils/azure_recorded_testcase.py:75: in get_settings_value
    raise ValueError(f"Could not get {key}") from ex
ValueError: Could not get SUBSCRIPTION_ID
```

---

## Async Test Results

Both async test files failed during **collection** due to a missing `aiohttp` dependency.

| Test File | Result | Error |
|-----------|--------|-------|
| `test_container_registry_management_operations_async_test.py` | ❌ COLLECTION ERROR | `ImportError: aiohttp package is not installed` |
| `test_container_registry_management_registries_operations_async_test.py` | ❌ COLLECTION ERROR | `ImportError: aiohttp package is not installed` |

### Root Cause

The `aiohttp` package is listed in `dev_requirements.txt` but was not available in the sandboxed test environment (no internet access to install from PyPI). The import chain is:

```
tests/*_async_test.py → devtools_testutils.aio → recorded_by_proxy_async
    → azure.core.pipeline.transport → AioHttpTransport → aiohttp (missing)
```

---

## Disabled Test Files

The following 6 test files are prefixed with `disable_` and were **not collected** by pytest:

| File | Description |
|------|-------------|
| `disable_test_cli_mgmt_containerregistry.py` | CLI mgmt container registry tests |
| `disable_test_cli_mgmt_containerregistry_registry.py` | CLI mgmt registry tests |
| `disable_test_cli_mgmt_containerregistry_task.py` | CLI mgmt task tests |
| `disable_test_mgmt_containerregistry.py` | Mgmt container registry tests |
| `disable_test_mgmt_containerregistry_2017_03_01.py` | API version 2017-03-01 tests |
| `disable_test_mgmt_containerregistry_2018_02_01_preview.py` | API version 2018-02-01-preview tests |

---

## Test Infrastructure Notes

1. **All active tests are `@pytest.mark.live_test_only`** — they cannot run in playback mode and require real Azure credentials.
2. **Tests use `AzureMgmtRecordedTestCase`** base class with `@RandomNameResourceGroupPreparer` for resource group provisioning.
3. **Tests use `@recorded_by_proxy`** (sync) and `@recorded_by_proxy_async`** (async) decorators for test proxy integration.

---

## Recommendations

To successfully run these live tests, the following prerequisites must be met:

1. **Set Azure credentials** as environment variables:
   ```bash
   export AZURE_SUBSCRIPTION_ID="<your-subscription-id>"
   export AZURE_TENANT_ID="<your-tenant-id>"
   export AZURE_CLIENT_ID="<your-client-id>"
   export AZURE_CLIENT_SECRET="<your-client-secret>"
   export AZURE_TEST_RUN_LIVE=true
   ```

2. **Install all dependencies** including `aiohttp`:
   ```bash
   pip install -r dev_requirements.txt
   pip install -e .
   ```

3. **Ensure network access** to Azure services and PyPI.

4. **Run tests**:
   ```bash
   pytest tests/ -v --tb=long
   ```

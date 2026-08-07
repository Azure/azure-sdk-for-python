# Azure AI ML: Autorest → TypeSpec Migration Plan

## Background

Two companion PRs initiated the migration from autorest-generated REST clients to TypeSpec-generated ones:

- **Spec PR**: [Azure/azure-rest-api-specs#40758](https://github.com/Azure/azure-rest-api-specs/pull/40758) — Authored TypeSpec definitions for 6 services (1 mgmt + 5 data-plane), merged Mar 26, 2026.
- **SDK PR**: [Azure/azure-sdk-for-python#45389](https://github.com/Azure/azure-sdk-for-python/pull/45389) — Consumed the TypeSpec specs to generate new Python clients, deleted some old GA versioned folders, merged Mar 27, 2026.

### What Those PRs Did
1. Created TypeSpec definitions in `azure-rest-api-specs` for:
   - `MachineLearningServices.Management` (ARM)
   - `AzureAI.RegistryDiscovery` (data-plane)
   - `AzureAI.WorkspaceDataplane` (data-plane)
   - `AzureAI.DatasetDataplane` (data-plane)
   - `AzureAI.ModelDataplane` (data-plane)
   - `AzureAI.RunHistory` (data-plane)
2. Generated TypeSpec-based Python clients in `_restclient/`
3. Removed old GA autorest client _full_ packages (kept models/operations stubs for backward compat)
4. Updated all imports in the SDK codebase to point to new TypeSpec clients where possible
5. Modernized packaging (setup.py → pyproject.toml, dropped msrest/azure-common)

---

## Current State (Post-Migration PR)

### TypeSpec-Generated Clients (DONE ✅)

| Client Folder | TypeSpec Spec Path | API Version | Status |
|---|---|---|---|
| `arm_ml_service/` | `MachineLearningServices.Management` | 2025-12-01 | ✅ Generated & in use |
| `registry_discovery/` | `AzureAI.RegistryDiscovery` | v1.0 | ✅ Generated & in use |
| `workspace_dataplane/` | `AzureAI.WorkspaceDataplane` | — | ✅ Generated & in use |
| `dataset_dataplane/` | `AzureAI.DatasetDataplane` | 1.5.0 | ✅ Generated & in use |
| `model_dataplane/` | `AzureAI.ModelDataplane` | 1.0.0 | ✅ Generated & in use |
| `runhistory/` | `AzureAI.RunHistory` | v1.0 | ✅ Generated & in use |
| `azure_ai_assets_v2024_04_01/` | `AzureAI.Assets` | 2024-04-01 | ✅ Generated & in use |

### GA Versions — Already Migrated ✅

The following GA versions were fully deleted by PR #45389. Their functionality is now covered by the TypeSpec `arm_ml_service` client (2025-12-01):
- 2022-05-01
- 2022-10-01
- 2023-04-01
- 2023-10-01

(Local `__pycache__` remnants may exist but no source files remain; these folders are not tracked in git.)

### Remaining Autorest Clients (STILL TO MIGRATE ❌)

| Folder | API Version | Key Usage | Priority |
|---|---|---|---|
| `v2020_09_01_dataplanepreview/` | 2020-09-01-dataplanepreview | BatchJobResource, DataVersion, UriFileJobOutput models | Low (legacy) |
| `v2021_10_01_dataplanepreview/` | 2021-10-01-dataplanepreview | AzureMachineLearningWorkspaces client, ModelVersionData | Low (legacy) |
| `v2022_01_01_preview/` | 2022-01-01-preview | Identity models (RestIdentityConfiguration, RestUserAssignedIdentity) | Medium |
| `v2022_02_01_preview/` | 2022-02-01-preview | ServiceClient, DeploymentLogsRequest, JobBaseData, KeyType, operations | Medium |
| `v2022_10_01_preview/` | 2022-10-01-preview | ServiceClient102022, UsageUnit | Medium |
| `v2022_12_01_preview/` | 2022-12-01-preview | (check usage) | Medium |
| `v2023_02_01_preview/` | 2023-02-01-preview | (check usage) | Medium |
| `v2023_04_01_preview/` | 2023-04-01-preview | ServiceClient022023Preview, many models (JobInput, JobOutput, Datastore creds, Identity, etc.) | **HIGH** |
| `v2023_06_01_preview/` | 2023-06-01-preview | ServiceClient062023Preview, models | Medium |
| `v2023_08_01_preview/` | 2023-08-01-preview | ServiceClient082023Preview, JobType, ListViewType, ModelVersion | Medium |
| `v2024_01_01_preview/` | 2024-01-01-preview | ServiceClient012024, TriggerOnceRequest, ComponentVersion, ComputeInstanceDataMount, JobBase | **HIGH** |
| `v2024_04_01_preview/` | 2024-04-01-preview | ServiceClient042024Preview, SsoSetting, models | **HIGH** |
| `v2024_07_01_preview/` | 2024-07-01-preview | ServiceClient072024Preview, Datastore models, SecretExpiry | **HIGH** |
| `v2024_10_01_preview/` | 2024-10-01-preview | ServiceClient102024Preview, ManagedNetworkProvisionOptions, OutboundRuleBasicResource, JobType | **HIGH** |
| `v2025_01_01_preview/` | 2025-01-01-preview | ServiceClient012025Preview | **HIGH** |

---

## Work Required

### Phase 1: TypeSpec Spec Authoring (azure-rest-api-specs repo)

For each remaining API version, swagger must be converted to TypeSpec in the `azure-rest-api-specs` repo. The ARM client already uses TypeSpec with versioning (via `@versioned` enum).

**Current TypeSpec coverage in spec repo (`MachineLearningServices.Management`):**
- 2024-10-01-preview ✅
- 2025-10-01-preview ✅
- 2025-12-01 ✅
- 2026-01-15-preview ✅
- 2026-03-01 ✅
- 2026-03-15-preview ✅

**Current TypeSpec coverage for dataplane projects:**
- `data-plane/DatasetDataplane` → 1.5.0 ✅
- `data-plane/ModelDataplane` → 1.0.0 ✅
- `data-plane/RunHistory` → v1.0 ✅
- `data-plane/RegistryDiscovery` → v1.0 ✅
- `data-plane/WorkspaceDataplane` → 2023-06-01-preview ✅
- `AzureAI.Assets` → 2024-04-01-preview, 2024-05-01-preview ✅

**Versions that NEED TypeSpec authoring (not yet in spec repo):**

| API Version | Type | Swagger Exists | Action Needed |
|---|---|---|---|
| 2020-09-01-dataplanepreview | Dataplane | ✅ | Add to TypeSpec or deprecate |
| 2021-10-01-dataplanepreview | Dataplane | ✅ | Add to TypeSpec or deprecate |
| 2022-01-01-preview | ARM | ✅ | Add to `@versioned` enum |
| 2022-02-01-preview | ARM | ✅ | Add to `@versioned` enum |
| 2022-10-01-preview | ARM | ✅ | Add to `@versioned` enum |
| 2022-12-01-preview | ARM | ✅ | Add to `@versioned` enum |
| 2023-02-01-preview | ARM | ✅ | Add to `@versioned` enum |
| 2023-04-01-preview | ARM | ✅ | Add to `@versioned` enum |
| 2023-06-01-preview | ARM | ✅ | Add to `@versioned` enum |
| 2023-08-01-preview | ARM | ✅ | Add to `@versioned` enum |
| 2024-01-01-preview | ARM | ✅ | Add to `@versioned` enum |
| 2024-04-01-preview | ARM | ✅ | Add to `@versioned` enum |
| 2024-07-01-preview | ARM | ✅ | Add to `@versioned` enum |
| 2025-01-01-preview | ARM | ✅ | Add to `@versioned` enum |

**Note:** The ARM TypeSpec was auto-generated from swagger using `@autorest/openapi-to-typespec` converter (v0.11.12). Adding older versions requires adding `@added(Versions.vXXXX)` decorators to models/operations and extending the Versions enum.

**Action Required:** We need TypeSpec definitions authored for all remaining autorest restclient API versions listed above. Each version's swagger needs to be converted and added to the `@versioned` enum in the `MachineLearningServices.Management` TypeSpec project (for ARM versions) or to the respective dataplane TypeSpec projects (for dataplane versions). Once the TypeSpec specs exist, we can generate the Python clients and replace the old autorest code.

### Phase 2: Generate TypeSpec Clients (azure-sdk-for-python repo)

Once specs are authored, generate clients using TypeSpec emitter and replace the autorest folders.

### Phase 3: Update Imports & Remove Old Clients

For each migrated version:
1. Update all imports in `azure/ai/ml/` to use the new TypeSpec-generated client
2. Run tests to validate no regressions
3. Delete old autorest folder

### Phase 4: Clean Up Local Artifacts

Remove leftover `__pycache__` directories from the deleted GA folders (v2022_05_01, v2022_10_01, v2023_04_01, v2023_10_01) — these are already untracked in git.

---

## Immediate Action: Versions With TypeSpec Already Available

The `v2024_04_01_dataplanepreview/` autorest client has been fully migrated — it was replaced by `azure_ai_assets_v2024_04_01/` (TypeSpec-generated from `AzureAI.Assets`). The old folder has been deleted.

The following remaining autorest client **already has TypeSpec definitions** in the spec repo and should be converted next:

| Autorest Client | API Version | TypeSpec Path in `azure-rest-api-specs` | Status |
|---|---|---|---|
| `v2024_10_01_preview/` | 2024-10-01-preview | `specification/machinelearningservices/MachineLearningServices.Management` (in `@versioned` enum) | Ready to generate |

**This should be the next target** — generate the TypeSpec client for this version, update imports, and remove the old autorest folder.

### How to Generate a REST Client from TypeSpec

From the `sdk/ml/azure-ai-ml/azure/ai/ml/_restclient` directory, use the `tsp-client` tool:

```bash
# Generate a specific client (e.g., arm_ml_service)
tsp-client update -d ./arm_ml_service

# Or to generate all clients listed in the batch tsp-location.yaml
tsp-client update
```

Each client subfolder has its own `tsp-location.yaml` pointing to the TypeSpec spec:
```yaml
directory: specification/machinelearningservices/MachineLearningServices.Management
commit: <commit-sha>
repo: Azure/azure-rest-api-specs
additionalDirectories: []
```

To target a specific commit or branch of the spec repo, update the `commit` field in the `tsp-location.yaml` before running `tsp-client update`.

## Versions Without TypeSpec (Require Spec Authoring First)

The following **13 versions** do NOT have TypeSpec definitions yet. Swagger-to-TypeSpec conversion is needed before these can be migrated:

| Autorest Client | API Version | Type |
|---|---|---|
| `v2020_09_01_dataplanepreview/` | 2020-09-01-dataplanepreview | Dataplane |
| `v2021_10_01_dataplanepreview/` | 2021-10-01-dataplanepreview | Dataplane |
| `v2022_01_01_preview/` | 2022-01-01-preview | ARM |
| `v2022_02_01_preview/` | 2022-02-01-preview | ARM |
| `v2022_10_01_preview/` | 2022-10-01-preview | ARM |
| `v2022_12_01_preview/` | 2022-12-01-preview | ARM |
| `v2023_02_01_preview/` | 2023-02-01-preview | ARM |
| `v2023_04_01_preview/` | 2023-04-01-preview | ARM |
| `v2023_06_01_preview/` | 2023-06-01-preview | ARM |
| `v2023_08_01_preview/` | 2023-08-01-preview | ARM |
| `v2024_01_01_preview/` | 2024-01-01-preview | ARM |
| `v2024_04_01_preview/` | 2024-04-01-preview | ARM |
| `v2024_07_01_preview/` | 2024-07-01-preview | ARM |
| `v2025_01_01_preview/` | 2025-01-01-preview | ARM |

---

## Recommended Execution Order

1. **Start with the 1 version that has TypeSpec available now** (`v2024_10_01_preview`) — generate client and migrate. (`v2024_04_01_dataplanepreview` already migrated as `azure_ai_assets_v2024_04_01`).
2. **Then target recent ARM previews** (2025-01-01-preview, 2024-07-01-preview, 2024-04-01-preview, 2024-01-01-preview) once their TypeSpecs are authored.
3. **Work backwards** through 2023-08-01-preview, 2023-06-01-preview, 2023-04-01-preview, etc.
4. **Legacy dataplane versions** (2020/2021) should be assessed for deprecation rather than migration — they may only be needed for very old model compatibility.

---

## Key Decisions Needed

1. **Multi-version vs single-latest**: Should the TypeSpec ARM client expose multiple API versions (via `@versioned`), or should old version imports be remapped to use the latest API version?
2. **Deprecation of legacy dataplane versions**: Can `v2020_09_01_dataplanepreview` and `v2021_10_01_dataplanepreview` be dropped entirely, or are they needed for live service compatibility?
3. **Model-only stubs**: Can GA stub folders be deleted if their models are re-exported from `arm_ml_service`?
4. **Incremental vs big-bang**: Migrate one API version at a time (safer) or batch multiple together?

---

## Summary Metrics

| Category | Count |
|---|---|
| TypeSpec clients already generated | 8 (+ 4 GA versions fully migrated) |
| Autorest clients still remaining | 15 preview versions |
| High-priority migrations | 6 (2023-04-01-preview through 2025-01-01-preview) |
| Legacy candidates for deprecation | 2 (2020/2021 dataplane) |

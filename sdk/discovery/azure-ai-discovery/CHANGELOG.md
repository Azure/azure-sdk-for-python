# Release History

## 1.0.0 (2026-07-25)

General availability release of `azure-ai-discovery`. API version `2026-06-01` is now the default for both `WorkspaceClient` and `BookshelfClient`.

### Features Added

- **Workspace**:
  - New paged list response models: `PagedConversation`, `PagedInvestigation`.
  - New `StorageMountProtocol` enum for controlling storage mount protocols.
  - New `tools.cancel_run_lro` long-running cancellation flow (in addition to the existing immediate `cancel_run`).
  - Investigation `update` is now exposed via a documented sample.
- **Bookshelf**: knowledge-base surface is significantly redesigned around a single `KnowledgeBasesOperations` group that exposes the full lifecycle in one place:
  - **Lifecycle**: `create_or_update`, `get`, `delete`, plus `get_operation_status` for polling long-running operations.
  - **Indexing**: `start_indexing` and `cancel_indexing`, with results modeled via `KnowledgeBaseIndexingOperationResponse`, `IndexingOperationResult`, `IndexingMetrics`, and `LastIndexingRun`.
  - **Search**: new `search` operation taking `SearchRequest` and returning `SearchResponse`, including `SearchResultItem` with `Citation` and `CitationType` for citation-aware results.
  - **LRO results**: status responses now use `KnowledgeBaseOperationResponse` / `KnowledgeBaseSearchOperationResponse`; create/update returns the `KnowledgeBase` resource.
  - New enum `KnowledgeBaseOperationType`.

### Breaking Changes

> Note: these are breaking changes only relative to the `1.0.0b1` preview release. As a first stable (GA) release, `1.0.0` is the new compatibility baseline going forward.

- **Bookshelf**: the `KnowledgeBaseVersionsOperations` operation group is removed. Knowledge-base versioning has been folded into the unified `KnowledgeBasesOperations` group; callers using `client.knowledge_base_versions.<method>` must migrate to the equivalent method on `client.knowledge_bases`.
- **Bookshelf**: the models `KnowledgeBaseOperationStatus` and `KnowledgeBaseVersion` are removed. Operation-status payloads are now typed as `KnowledgeBaseOperationResponse`, `KnowledgeBaseIndexingOperationResponse`, or `KnowledgeBaseSearchOperationResponse` depending on the operation; create/update returns the `KnowledgeBase` resource.
- The preview API version `2026-02-01-preview` is no longer listed as a supported value for the `api_version` kwarg. Both `WorkspaceClient` and `BookshelfClient` now default to `2026-06-01`. Pinning to the removed preview value is not supported in the GA SDK.
- **Workspace**: the investigations long-running operation status model, previously generated as `ResourceOperationStatusInvestigationInvestigationError`, has been renamed to `InvestigationOperationStatus`. The payload is unchanged; only the model name differs.

### Other Changes

- Regenerated against [Azure/azure-rest-api-specs PR #42884](https://github.com/Azure/azure-rest-api-specs/pull/42884) (commit `fbe3c49c541a2932f4a4cb348fb0798988f4aca4`).
- `Development Status` classifier flipped from `4 - Beta` to `5 - Production/Stable`.
- Emitter `@azure-tools/typespec-python` at `0.63.3`; the four hand-written client `_patch.py` overrides that expose `transport` and `api_version` as explicit keyword-only parameters remain in place pending future emitter support.

## 1.0.0b1 (2026-05-16)

Initial beta release of the Azure AI Discovery client library for Python.

### Features Added

- Added `WorkspaceClient` for managing Discovery workspace resources, with operation groups for:
  - `investigations` — create, list, get, and delete investigations, and start/stop/get/update the per-investigation Discovery Engine.
  - `conversations` — create, list, get, update, and delete conversations that interact with the Discovery Engine.
  - `tasks` — create, list (with `$filter` support), get, update, comment on, start, and delete tasks; record execution history.
  - `tools` — run tools on supercomputer node pools, monitor run status with log retrieval, cancel runs, and query compute usage.
- Added `BookshelfClient` for managing knowledge bases, with operation groups for:
  - `knowledge_bases` — list available knowledge bases.
  - `knowledge_base_versions` — create or update, get, list, delete, and retrieve the latest version of a knowledge base; start, cancel, and monitor indexing.
- Added shared model types under `azure.ai.discovery.models` covering investigations, conversations, tasks, tools, knowledge bases, and the Discovery Engine.

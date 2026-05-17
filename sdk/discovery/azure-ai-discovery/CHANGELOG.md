# Release History

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

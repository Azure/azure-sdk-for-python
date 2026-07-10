# AGENTS.md - Azure SDK for Python: Storage

This file provides guidance for AI agents (e.g., GitHub Copilot, MCP servers, or LLM-based assistants) working with the Azure Storage SDK packages in this directory.

## Storage SDK Overview

The `sdk/storage/` directory contains the following modules:

| Package | Azure Service |
|---------|---------------|
| `azure-storage-blob` | Azure Blob Storage — object storage for unstructured data |
| `azure-storage-queue` | Azure Queue Storage — message queuing service |
| `azure-storage-file-share` | Azure Files — fully managed SMB/NFS file shares |
| `azure-storage-file-datalake` | Azure Data Lake Storage Gen2 — hierarchical namespace over Blob |
| `azure-storage-blob-changefeed` | Azure Blob Storage Change Feed — ordered log of blob changes |
| `azure-storage-extensions` | Native performance extensions for Storage Python SDKs |
| `azure-mgmt-storage` | Azure Storage Management — storage account and resource management |
| `azure-mgmt-storagecache` | Azure HPC Cache / Storage Cache management |
| `azure-mgmt-storagesync` | Azure File Sync management |
| `azure-mgmt-storageimportexport` | Azure Import/Export Service management |

## Rules for AI Agents

### Rule 1: Do Not Edit Generated Code

The following directories contain auto-generated code produced by the Azure REST API code generator. **Do not modify these files directly.** Changes must be made upstream in the API specification or the autorest/TypeSpec configuration and then regenerated.

- `azure-storage-blob/azure/storage/blob/_generated/`
- `azure-storage-queue/azure/storage/queue/_generated/`
- `azure-storage-file-share/azure/storage/fileshare/_generated/`
- `azure-storage-file-datalake/azure/storage/filedatalake/_generated/`
- `azure-mgmt-storage/azure/mgmt/storage/`  *(entire package is generated)*
- `azure-mgmt-storagecache/azure/mgmt/storagecache/`  *(entire package is generated)*
- `azure-mgmt-storagesync/azure/mgmt/storagesync/`  *(entire package is generated)*
- `azure-mgmt-storageimportexport/azure/mgmt/storageimportexport/`  *(entire package is generated)*

Handwritten (patch) code lives alongside `_generated/` in the package root and in `_patch.py` files. Edits to patch files are acceptable.

### Rule 2: Preserve API Consistency Across Blobs, Queues, Files, and Data Lake

The four data-plane storage packages (`blob`, `queue`, `file-share`, `file-datalake`) share a common design language:

- Each service exposes a **service client** (`BlobServiceClient`, `QueueServiceClient`, `ShareServiceClient`, `DataLakeServiceClient`) that handles account-level operations.
- Each exposes a **container/share/filesystem client** and an **item client** (blob, queue, file/directory) with matching method signatures where applicable.
- Sync and async clients share the same public method names; the async variants live in a corresponding `aio/` subpackage.
- When adding or changing a method on one client, verify whether the equivalent clients in the other packages should receive the same change.
- When updating a package `_shared/` module, check equivalent `_shared` modules across other storage packages and keep shared behavior aligned unless divergence is intentional and documented.

### Rule 3: Prefer Existing Patterns Over New Abstractions

Before introducing a new helper class, utility function, or base class, search for an existing implementation across the storage packages. Common patterns already in use include:

- Prefer existing helper and handler patterns before introducing new abstractions.
- Check common extension points first: `_helpers` modules, upload/download helper modules, handler modules, and package `_shared` utilities.

Introduce new abstractions only when an existing pattern genuinely cannot accommodate the requirement.

### Rule 4: No Magic Strings

Azure Storage services are case-sensitive for many identifiers (container names, blob names, metadata keys, SAS parameters). Avoid hardcoding raw string literals for:

- HTTP header names — use constants from `azure.storage.blob._shared.constants` or equivalent.
- Service version strings — reference the `X_MS_VERSION` constant (from `azure.storage.blob._shared.constants`) rather than inline strings.
- SAS permission characters — use the typed permission classes (e.g., `BlobSasPermissions`, `QueueSasPermissions`) instead of raw character strings.
- Error codes/constants — avoid repeating literal strings. Reuse existing constants when available (including shared constants modules). If none exist, define module-level constants near usage and follow local package conventions.

## Storage Service Semantics

Agents modifying service-specific logic should be aware of the following behavioral characteristics:

### Blob Storage

- **AppendBlob**: Append operations are not idempotent. Retrying an `append_block` call on a transient failure can produce duplicate data. Guards against duplicate appends should use the `appendpos_condition` parameter to assert the expected blob length before writing.
- **BlockBlob commit flow**: Data is uploaded as one or more staged blocks (`stage_block` / `upload_blob_from_url`), then committed atomically via `commit_block_list`. An uncommitted block list is discarded if not committed within 7 days. The public `upload_blob` method handles this flow automatically for large uploads; do not replicate it manually.
- **PageBlob**: Aligned to 512-byte pages. Writes must start and end on 512-byte boundaries.

### Queue Storage

- **Visibility timeout**: A dequeued message is hidden from other consumers for the duration of the visibility timeout (default 30 seconds, max 7 days). If processing takes longer than the timeout, extend it with `update_message` before it expires, or the message will reappear and be processed again.
- **Message encoding**: Messages are **not** encoded by default (`NoEncodePolicy`). Base64 encoding is opt-in via `message_encode_policy` (e.g., `TextBase64EncodePolicy` or `BinaryBase64EncodePolicy`) on the `QueueClient`. Changing the policy on an existing queue that already contains messages can make previously written messages undecodable.

### Azure Files (File Share)

- **Share hierarchy**: The resource hierarchy is Account → Share → Directory (nested) → File. The `create_directory` API does not support recursive creation; each parent directory must be created individually before creating a subdirectory. There is no built-in `mkdir -p` equivalent in the SDK.
- **Lease semantics**: Files (but not directories) support leases. A lease must be acquired before exclusive write access. Shares support snapshot-level leases for backup scenarios.

### Data Lake Storage Gen2

- **Hierarchical namespace**: Rename and move operations on directories are atomic when the storage account has hierarchical namespace (HNS) enabled. On non-HNS accounts, the Data Lake client falls back to Blob operations and these operations are not atomic.
- **Access Control Lists (ACLs)**: POSIX-style ACLs are only enforced on HNS-enabled accounts. `set_access_control` calls on non-HNS accounts will succeed but have no effect on authorization.

## Build and Test

### Install a package in development mode

```bash
cd sdk/storage/<package-name>
pip install -r dev_requirements.txt
pip install -e .
azpysdk black .
```
> Use a virtual environment (recommended) to avoid dependency conflicts with other SDK packages or your global Python environment.

### Run tests (playback mode — no live service required)

```bash
To run tests in live mode, set the environment variable first (do not use a `--live` flag):

```bash
# Linux/macOS
export AZURE_TEST_RUN_LIVE=true

# Windows (PowerShell)
$env:AZURE_TEST_RUN_LIVE="true"
```

If there is a test command immediately after, keep it and make it normal `pytest` usage (no `--live`).

---

### C) Add single/few-test examples in test section (near live guidance)

Add:

```bash
# Run one test file
pytest tests/test_<feature>.py

# Run one test case
pytest tests/test_<feature>.py::test_<name>
```


### Run tests against the Azurite local emulator (optional)

> **Optional**: Azurite emulator testing is not required. Most tests can be run in playback mode (see above) without any live service or local emulator. Use this section only if you specifically need to validate behavior against a local emulator.

Start Azurite before running tests:

```bash
# Install Azurite (requires Node.js)
npm install -g azurite

# Start all storage services (Blob on 10000, Queue on 10001, Table on 10002)
azurite --silent --location /tmp/azurite --debug /tmp/azurite/debug.log
```

Then point the SDK at the local emulator using the well-known Azurite connection string:

```bash
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"
pytest tests/ -v --live
```

### Run linting and static analysis

```bash
cd sdk/storage/<package-name>
azpysdk pylint .
azpysdk mypy .
```

### Rule 5: Follow typing conventions

- All public APIs must include Python 3 style type hints. Add hints to private functions and internal helpers when practical.
- Follow existing SDK typing patterns (for example, prefer `Literal` where that pattern is established rather than introducing new enum types only for typing).
- If a typing-only import is not needed at runtime, place it under `if TYPE_CHECKING:`.
- Prefer explicit optionality in signatures. For kwargs containers, make optionality clear when `None` is accepted (for example, `Optional[Dict[str, Any]]` or `dict[str, Any] | None`).

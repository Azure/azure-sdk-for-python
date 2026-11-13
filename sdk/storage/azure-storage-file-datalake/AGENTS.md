# AGENTS.md - Azure Storage Data Lake SDK

This file provides package-specific guidance for AI agents working in `sdk/storage/azure-storage-file-datalake/`.

For repository-wide guidance, see the root [`AGENTS.md`](../../../AGENTS.md).
For storage-wide guidance, see [`sdk/storage/AGENTS.md`](../AGENTS.md).

## Scope

This package implements Azure Data Lake Storage Gen2 clients built on top of Azure Blob Storage:

- Sync and async clients in `azure/storage/filedatalake/` and `azure/storage/filedatalake/aio/`
- `DataLakeServiceClient`, `FileSystemClient`, `DataLakeDirectoryClient`, and `DataLakeFileClient`
- Access control list (ACL) management
- Path and filesystem operations with hierarchical namespace semantics

## Directory Structure

```
azure-storage-file-datalake/
├── azure/storage/filedatalake/
│   ├── _generated/                  # AUTO-GENERATED — do not edit directly
│   ├── _shared/                     # Shared utilities (symlinked from azure-storage-blob)
│   ├── aio/                         # Async client implementations
│   ├── _data_lake_service_client.py # DataLakeServiceClient (handwritten)
│   ├── _file_system_client.py       # FileSystemClient (handwritten)
│   ├── _data_lake_directory_client.py  # DataLakeDirectoryClient (handwritten)
│   ├── _data_lake_file_client.py    # DataLakeFileClient (handwritten)
│   └── _patch.py                    # Handwritten patches applied over generated code
└── tests/
    ├── recordings/                  # Recorded test cassettes for playback mode
    └── test_*.py                    # Test files
```

## Rules for AI Agents

### Rule 1: Do Not Edit Generated Code

Do not modify anything under `azure/storage/filedatalake/_generated/`. Changes to generated behavior must be made in the upstream API specification or autorest/TypeSpec configuration, then regenerated.

Handwritten code lives in the package root and in `_patch.py` files — these are the correct locations for targeted changes.

### Rule 2: Preserve the Blob/Data Lake Relationship

Data Lake Storage Gen2 is a superset of Blob Storage — when hierarchical namespace (HNS) is not enabled on the account, the Data Lake client falls back to Blob Storage operations. This distinction must be preserved:

- Do not introduce logic that assumes all accounts are HNS-enabled.
- Non-atomic fallback behavior on non-HNS accounts is correct and expected.

### Rule 3: Keep Sync/Async Public Surface Aligned

The sync clients in `azure/storage/filedatalake/` and the async clients in `azure/storage/filedatalake/aio/` must expose matching public method names and signatures. When changing a method on one, verify the equivalent in the other.

### Rule 4: Use Constants and Typed Helpers

Avoid magic strings. Use existing constants and typed classes for:

- HTTP header names — use constants from `azure.storage.filedatalake._shared.constants`
- Service version strings — reference the `X_MS_VERSION` constant
- SAS permissions — use typed classes (`FileSystemSasPermissions`, `DataLakeSasPermissions`)
- Error codes — compare against named constants, not literal strings

## Data Lake-Specific Semantics to Preserve

- **Hierarchical namespace (HNS)**: Rename and move operations on directories are **atomic only on HNS-enabled accounts**. On non-HNS accounts, the client falls back to Blob operations and these operations are not atomic.
- **Access Control Lists (ACLs)**: POSIX-style ACLs are only enforced on HNS-enabled accounts. `set_access_control` calls on non-HNS accounts will succeed but have no effect on authorization.
- **Path operations**: Paths (directories and files) are first-class resources. Create, rename, delete, and recursive ACL propagation are path-level operations with specific consistency guarantees on HNS accounts.
- **Pagination of directory listings**: Directory entries are returned paginated; avoid collecting all pages eagerly in a single call when the directory may be large.

## Testing Guidance

### Playback tests (default — no live service required)

```bash
cd sdk/storage/azure-storage-file-datalake
pytest tests/ -v
```

### Live tests

Set `AZURE_STORAGE_ACCOUNT_NAME` and either `AZURE_STORAGE_ACCOUNT_KEY` or `AZURE_STORAGE_CONNECTION_STRING`, then:

```bash
cd sdk/storage/azure-storage-file-datalake
pytest tests/ -v --live
```

### Azurite emulator tests (optional)

> **Optional**: Most tests run in playback mode without a live service or emulator. Use this only when you specifically need emulator behavior.

See [`sdk/storage/AGENTS.md`](../AGENTS.md) for Azurite setup instructions.

## Validation

```bash
cd sdk/storage/azure-storage-file-datalake
azpysdk pylint .
azpysdk mypy .
```

## Cross-Package Consistency

The four data-plane storage packages share a common design language. Before adding or changing a method here, check whether the equivalent clients in `azure-storage-blob`, `azure-storage-queue`, and `azure-storage-file-share` should receive the same change. See [`sdk/storage/AGENTS.md`](../AGENTS.md) for details.

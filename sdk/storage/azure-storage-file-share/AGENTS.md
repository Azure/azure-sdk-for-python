# AGENTS.md - Azure Storage File Share SDK

This file provides package-specific guidance for AI agents working in `sdk/storage/azure-storage-file-share/`.

For repository-wide guidance, see the root [`AGENTS.md`](../../../AGENTS.md).
For storage-wide guidance, see [`sdk/storage/AGENTS.md`](../AGENTS.md).

## Scope

This package implements Azure Files clients for SMB/NFS file shares:

- Sync and async clients in `azure/storage/fileshare/` and `azure/storage/fileshare/aio/`
- `ShareServiceClient`, `ShareClient`, `ShareDirectoryClient`, and `ShareFileClient`
- SAS generation helpers (`generate_share_sas`, `generate_file_sas`)
- Lease support for files and shares

## Directory Structure

```
azure-storage-file-share/
├── azure/storage/fileshare/
│   ├── _generated/              # AUTO-GENERATED — do not edit directly
│   ├── _shared/                 # Shared utilities (symlinked from azure-storage-blob)
│   ├── aio/                     # Async client implementations
│   ├── _share_client.py         # ShareClient (handwritten)
│   ├── _share_service_client.py # ShareServiceClient (handwritten)
│   ├── _directory_client.py     # ShareDirectoryClient (handwritten)
│   ├── _file_client.py          # ShareFileClient (handwritten)
│   └── _patch.py                # Handwritten patches applied over generated code
└── tests/
    ├── recordings/              # Recorded test cassettes for playback mode
    └── test_*.py                # Test files
```

## Rules for AI Agents

### Rule 1: Do Not Edit Generated Code

Do not modify anything under `azure/storage/fileshare/_generated/`. Changes to generated behavior must be made in the upstream API specification or autorest/TypeSpec configuration, then regenerated.

Handwritten code lives in the package root and in `_patch.py` files — these are the correct locations for targeted changes.

### Rule 2: Preserve Client Hierarchy Semantics

Azure Files has a strict four-level resource hierarchy:

```
ShareServiceClient → ShareClient → ShareDirectoryClient → ShareFileClient
```

Do not flatten or blur this hierarchy. Operations belong at the correct client level; account-level operations go on the service client, share-level operations on the share client, and so on.

### Rule 3: Keep Sync/Async Public Surface Aligned

The sync clients in `azure/storage/fileshare/` and the async clients in `azure/storage/fileshare/aio/` must expose matching public method names and signatures. When changing a method on one, verify the equivalent in the other.

### Rule 4: Use Constants and Typed Helpers

Avoid magic strings. Use existing constants and typed classes for:

- HTTP header names — use constants from `azure.storage.fileshare._shared.constants`
- Service version strings — reference the `X_MS_VERSION` constant
- SAS permissions — use typed classes (`ShareSasPermissions`, `FileSasPermissions`)
- Error codes — compare against named constants, not literal strings

## File Share-Specific Semantics to Preserve

- **Directory creation is non-recursive**: `create_directory` creates a single directory. Each parent directory must already exist before creating a subdirectory. There is no built-in `mkdir -p` equivalent in the SDK.
- **Lease behavior differs by resource type**: Files (but not directories) support leases for exclusive write access. Shares support snapshot-level leases for backup scenarios. Preserve these semantics; do not apply file-style leases to directories or share-level leases to files.
- **Share snapshots**: Snapshots are read-only point-in-time copies of a share. They can be addressed via the `snapshot` parameter on `ShareClient`. Do not conflate snapshot operations with live share operations.
- **SMB vs. NFS**: The service supports both SMB and NFS protocols at the share level. Avoid introducing protocol-specific assumptions in shared code paths.

## Testing Guidance

### Playback tests (default — no live service required)

```bash
cd sdk/storage/azure-storage-file-share
pytest tests/ -v
```

### Live tests

Set `AZURE_STORAGE_ACCOUNT_NAME` and either `AZURE_STORAGE_ACCOUNT_KEY` or `AZURE_STORAGE_CONNECTION_STRING`, then:

```bash
cd sdk/storage/azure-storage-file-share
pytest tests/ -v --live
```

### Azurite emulator tests (optional)

> **Optional**: Most tests run in playback mode without a live service or emulator. Use this only when you specifically need emulator behavior.

See [`sdk/storage/AGENTS.md`](../AGENTS.md) for Azurite setup instructions.

## Validation

```bash
cd sdk/storage/azure-storage-file-share
azpysdk pylint .
azpysdk mypy .
```

## Cross-Package Consistency

The four data-plane storage packages share a common design language. Before adding or changing a method here, check whether the equivalent clients in `azure-storage-blob`, `azure-storage-queue`, and `azure-storage-file-datalake` should receive the same change. See [`sdk/storage/AGENTS.md`](../AGENTS.md) for details.

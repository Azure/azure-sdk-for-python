# AGENTS.md - Azure Storage Blob SDK

This file provides package-specific guidance for AI agents working in `sdk/storage/azure-storage-blob/`.

For repository-wide guidance, see the root [`AGENTS.md`](../../../AGENTS.md).
For storage-wide guidance, see [`sdk/storage/AGENTS.md`](../AGENTS.md).

## Scope

This package implements Azure Blob Storage clients and supporting models/utilities:

- Sync and async clients in `azure/storage/blob/` and `azure/storage/blob/aio/`
- `BlobServiceClient`, `ContainerClient`, `BlobClient`, and `BlobLeaseClient`
- SAS generation helpers (`generate_blob_sas`, `generate_container_sas`, etc.)
- Transfer helpers for upload and download

## Directory Structure

```
azure-storage-blob/
├── azure/storage/blob/
│   ├── _generated/          # AUTO-GENERATED — do not edit directly
│   ├── _shared/             # Shared utilities reused by other storage packages
│   ├── aio/                 # Async client implementations
│   ├── _blob_client.py      # BlobClient (handwritten)
│   ├── _container_client.py # ContainerClient (handwritten)
│   ├── _blob_service_client.py  # BlobServiceClient (handwritten)
│   └── _patch.py            # Handwritten patches applied over generated code
└── tests/
    ├── recordings/          # Recorded test cassettes for playback mode
    └── test_*.py            # Test files
```

## Rules for AI Agents

### Rule 1: Do Not Edit Generated Code

Do not modify anything under `azure/storage/blob/_generated/`. Changes to generated behavior must be made in the upstream API specification or autorest/TypeSpec configuration, then regenerated.

Handwritten code lives in the package root and in `_patch.py` files — these are the correct locations for targeted changes.

### Rule 2: Keep Sync/Async Public Surface Aligned

The sync clients in `azure/storage/blob/` and the async clients in `azure/storage/blob/aio/` must expose matching public method names and signatures. When changing a method on one, verify the equivalent in the other.

### Rule 3: Preserve Client Layering

Blob APIs follow a strict resource hierarchy:

```
BlobServiceClient → ContainerClient → BlobClient
```

Do not move operations to the wrong client level. Prefer existing shared helpers in `_shared/` over new abstractions.

### Rule 4: Use Constants and Typed Helpers

Avoid magic strings. Use existing constants and typed classes for:

- HTTP header names — use constants from `azure.storage.blob._shared.constants`
- Service version strings — reference the `X_MS_VERSION` constant
- SAS permissions — use typed classes (`BlobSasPermissions`, `ContainerSasPermissions`)
- Error codes — compare against named constants, not literal strings

## Blob-Specific Semantics to Preserve

- **AppendBlob**: Append operations are **not idempotent**. Retrying `append_block` on a transient failure can produce duplicate data. Use the `appendpos_condition` parameter to assert the expected blob length before writing.
- **BlockBlob**: Data is staged as blocks (`stage_block`) then committed atomically via `commit_block_list`. An uncommitted block list is discarded after 7 days. The `upload_blob` method handles this automatically for large uploads — do not replicate it manually.
- **PageBlob**: Aligned to 512-byte pages. All writes must start and end on 512-byte boundaries.

## Testing Guidance

### Playback tests (default — no live service required)

```bash
cd sdk/storage/azure-storage-blob
pytest tests/ -v
```

### Live tests

Set `AZURE_STORAGE_ACCOUNT_NAME` and either `AZURE_STORAGE_ACCOUNT_KEY` or `AZURE_STORAGE_CONNECTION_STRING`, then:

```bash
cd sdk/storage/azure-storage-blob
pytest tests/ -v --live
```

### Azurite emulator tests (optional)

> **Optional**: Most tests run in playback mode without a live service or emulator. Use this only when you specifically need emulator behavior.

See [`sdk/storage/AGENTS.md`](../AGENTS.md) for Azurite setup instructions.

## Validation

```bash
cd sdk/storage/azure-storage-blob
azpysdk pylint .
azpysdk mypy .
```

## Cross-Package Consistency

The four data-plane storage packages share a common design language. Before adding or changing a method here, check whether the equivalent clients in `azure-storage-queue`, `azure-storage-file-share`, and `azure-storage-file-datalake` should receive the same change. See [`sdk/storage/AGENTS.md`](../AGENTS.md) for details.

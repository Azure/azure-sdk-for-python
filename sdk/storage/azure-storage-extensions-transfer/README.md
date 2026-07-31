# Extension package for Azure Storage Python libraries — Transfer Acceleration

**This package provides optional native transfer acceleration for Azure Storage Blob Python SDK and is not intended for direct use.**

This package contains a Rust-based native extension module that accelerates blob upload and download operations by delegating to the `azure_storage_blob` Rust crate. It is designed exclusively for use with `azure-storage-blob` and must be explicitly installed to enable enhanced transfer performance.

## Important Notes

⚠️ **Not for standalone use**: This package is designed exclusively as an optional dependency for Azure Storage Python SDK libraries. The API surface is subject to change without following semantic versioning conventions—breaking changes may occur between minor versions.

## Installation

Install this package via extras when installing Azure Storage Blob:

```bash
pip install azure-storage-blob[ext-transfer]
```

This ensures you get compatible versions of both the SDK and the extensions package.

> ⚠️ Installing `azure-storage-extensions-transfer` directly is not recommended. Use the extras syntax above to ensure compatibility.

### Prerequisites
* Python 3.10 or later is required.
* A Rust toolchain is required to build from source. Pre-built wheels are provided for common platforms.

## What it accelerates

When installed, this package transparently accelerates:
- **Block blob uploads** — Large data uploads use the Rust SDK's managed parallel chunking
- **Block blob downloads** — Downloads use Rust's `download_into` over a sliding window, giving
  parallel range fetches within each window while bounding peak memory to a single window

The Python SDK automatically falls back to its built-in Python implementation when:
- Client-side encryption is enabled
- The blob type is not a block blob
- Text-mode download encoding is requested
- Content decompression is needed
- Content validation (checksums) is enabled
- Non-TokenCredential authentication is used (e.g., account keys without SAS)

## Supported Authentication
- **TokenCredential** (Azure Identity / Entra ID) — OAuth access tokens
- **SAS URLs** — Pre-signed URLs with embedded SAS tokens

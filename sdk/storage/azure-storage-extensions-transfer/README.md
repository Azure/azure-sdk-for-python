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

## Rust source layout

- `src/lib.rs`: Python module registration, shared runtime/transport, client construction, and transfer defaults.
- `src/credentials.rs`: Python token callback credential and process-wide credential cache.
- `src/upload.rs`: Upload bindings, zero-copy Python buffer ownership, and upload response conversion.
- `src/download.rs`: Download bindings and the windowed download stream.

## Running Rust tests

The automated Rust tests run offline without an Azure account, Azurite, or an
installed extension. They embed Python through PyO3 and use a fake HTTP transport
to exercise transfer requests and responses. A Python 3.10+ installation and the
Rust toolchain are required.

From this package directory, run:

```powershell
cargo test --lib
cargo test --lib credentials
cargo test --lib upload
cargo test --lib download
cargo fmt --all -- --check
```

On Windows, the directory containing the Python DLL must be on `PATH`. If needed,
select the interpreter and expose its DLL directory before running Cargo:

```powershell
$env:PYO3_PYTHON = python -c "import sys; print(sys.executable)"
$pythonHome = python -c "import sys; print(sys.base_prefix)"
$env:PATH = "$pythonHome;$env:PATH"
cargo test --lib
```

To also verify extension packaging (requires maturin), run:

```powershell
python -m maturin build --interpreter python
```

Maturin enables the PyO3 extension-module feature through `pyproject.toml`;
ordinary Cargo tests leave it disabled so the embedded interpreter can link.

## What it accelerates

When installed, this package transparently accelerates:
- **Block blob uploads** — Large data uploads use the Rust SDK's managed parallel chunking
- **Block blob downloads** — Downloads use Rust's `download_into` over a sliding window, giving
  parallel range fetches within each window while bounding peak memory to a single window

Download errors can occur when starting a download or while consuming later windows.
Incomplete reads raise an error rather than ending iteration successfully. After a
stream fails, subsequent reads re-raise the failure without issuing more requests.
Bytes already yielded or written to a destination are not rolled back. Nonempty
ranged responses must include a valid `Content-Range` total; the response
`Content-Length` alone does not identify the total blob size.

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

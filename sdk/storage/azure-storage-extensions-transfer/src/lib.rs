// -------------------------------------------------------------------------
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for
// license information.
// --------------------------------------------------------------------------

//! PyO3 native module for accelerated Azure Blob Storage transfers.
//!
//! Provides `upload_blob` and `download_blob` functions that delegate to the
//! `azure_storage_blob` Rust crate for high-performance parallel transfers.

use std::collections::HashMap;
use std::num::NonZero;
use std::sync::Arc;

use azure_core::credentials::{AccessToken, Secret, TokenCredential, TokenRequestOptions};
use azure_core::http::headers::HeaderName;
use azure_core::http::{NoFormat, RequestContent, Url};
use azure_core::Bytes;
use azure_storage_blob::models::{
    BlobClientDownloadOptions, BlockBlobClientUploadOptions, HttpRange,
};
use azure_storage_blob::{BlobClient, BlobClientOptions};
use once_cell::sync::Lazy;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::buffer::PyBuffer;
use pyo3::types::{PyBytes, PyDict};
use tokio::runtime::Runtime;

/// Shared tokio runtime — created once, reused across all calls to avoid
/// per-call overhead of spawning a new runtime.
static RUNTIME: Lazy<Runtime> = Lazy::new(|| {
    Runtime::new().expect("Failed to create tokio runtime")
});

/// Custom error wrapper for mapping `azure_core::Error` to Python exceptions.
struct AzureError(azure_core::Error);

impl From<AzureError> for PyErr {
    fn from(err: AzureError) -> PyErr {
        PyValueError::new_err(format!("Azure Storage error: {}", err.0))
    }
}

impl From<azure_core::Error> for AzureError {
    fn from(e: azure_core::Error) -> Self {
        Self(e)
    }
}

/// Build a `BlobClient` from a fully-qualified blob URL and optional token provider.
///
/// `blob_url` must be the complete, already percent-encoded blob URL
/// (e.g. `https://account.blob.core.windows.net/container/blob`), optionally including a
/// SAS token in the query string. It is parsed and used as-is — `BlobClient::new` expects
/// the caller to have encoded it correctly, and `Url::parse` preserves existing
/// percent-encoding, so no double-encoding occurs.
///
/// If `token_provider` is provided, a Python-callback credential is used that fetches a
/// fresh token on demand. If the `blob_url` contains a SAS token in the query string,
/// pass `token_provider=None`.
fn build_blob_client(
    blob_url: &str,
    token_provider: Option<Py<PyAny>>,
) -> Result<BlobClient, AzureError> {
    let blob_url = Url::parse(blob_url).map_err(|e| {
        azure_core::Error::with_message(
            azure_core::error::ErrorKind::Other,
            format!("Invalid URL: {}", e),
        )
    })?;

    let credential: Option<Arc<dyn TokenCredential>> = match token_provider {
        Some(provider) => Some(Arc::new(PyCallbackCredential::new(provider))),
        None => None,
    };

    let client =
        BlobClient::new(blob_url, credential, None::<BlobClientOptions>).map_err(AzureError::from)?;
    Ok(client)
}

/// A `TokenCredential` that delegates to a Python callable on every request.
///
/// Rather than caching a single token string, we hold a Python "token provider"
/// (`Py<PyAny>`) and invoke it whenever the `azure_core` bearer-token policy needs a
/// token — including when the cached token nears expiry. This lets token refresh flow
/// all the way back to the real Python credential (e.g. `DefaultAzureCredential`), which
/// owns caching and refresh.
///
/// The provider has the signature `provider(scopes: list[str]) -> (token: str, expires_on: int)`
/// where `expires_on` is a Unix timestamp in seconds.
///
/// Thread-safety: the struct holds only an immutable `Py<PyAny>` (which is `Send + Sync`);
/// each `get_token` call independently re-acquires the GIL, which serializes the actual
/// Python execution. The Python-side provider additionally serializes calls with a lock.
/// The `azure_core` bearer policy already serializes refreshes via a `RwLock`, so under
/// parallel chunked transfers only one refresh runs at a time per client.
#[derive(Debug)]
struct PyCallbackCredential {
    provider: Py<PyAny>,
}

impl PyCallbackCredential {
    fn new(provider: Py<PyAny>) -> Self {
        Self { provider }
    }
}

#[async_trait::async_trait]
impl TokenCredential for PyCallbackCredential {
    async fn get_token(
        &self,
        scopes: &[&str],
        _options: Option<TokenRequestOptions<'_>>,
    ) -> azure_core::Result<AccessToken> {
        // Re-attach the current thread to the interpreter (valid to do inside the outer
        // `detach`) and call the Python token provider to obtain a fresh token and its
        // real expiry.
        Python::attach(|py| {
            let scope_list: Vec<String> = scopes.iter().map(|s| s.to_string()).collect();
            let result = self.provider.bind(py).call1((scope_list,)).map_err(|e| {
                azure_core::Error::with_message(
                    azure_core::error::ErrorKind::Credential,
                    format!("Python token provider call failed: {}", e),
                )
            })?;
            let (token, expires_on): (String, i64) = result.extract().map_err(|e| {
                azure_core::Error::with_message(
                    azure_core::error::ErrorKind::Credential,
                    format!(
                        "Python token provider returned an unexpected value (expected (str, int)): {}",
                        e
                    ),
                )
            })?;
            let expires = azure_core::time::OffsetDateTime::from_unix_timestamp(expires_on)
                .map_err(|e| {
                    azure_core::Error::with_message(
                        azure_core::error::ErrorKind::Credential,
                        format!("Python token provider returned an invalid expiry: {}", e),
                    )
                })?;
            Ok(AccessToken::new(Secret::new(token), expires))
        })
    }
}

/// Upload a block blob using the Rust SDK.
///
/// This function releases the GIL during the entire Rust I/O operation,
/// allowing other Python threads to run concurrently.
#[pyfunction]
#[pyo3(signature = (
    url,
    data,
    *,
    token_provider = None,
    overwrite = false,
    content_type = None,
    metadata = None,
    max_concurrency = None,
    _max_single_put_size = None,
    max_block_size = None,
))]
fn upload_blob<'py>(
    py: Python<'py>,
    url: &str,
    data: &Bound<'py, PyAny>,
    token_provider: Option<Py<PyAny>>,
    overwrite: bool,
    content_type: Option<&str>,
    metadata: Option<HashMap<String, String>>,
    max_concurrency: Option<usize>,
    _max_single_put_size: Option<u64>,
    max_block_size: Option<u64>,
) -> PyResult<Bound<'py, PyDict>> {
    let blob_client = build_blob_client(url, token_provider)?;

    // We copy the payload once into a Rust-owned `Bytes` here, while the interpreter is attached.
    //
    // This single copy is required (not merely convenient): the upload below detaches the
    // current thread from the interpreter via `detach`, so we must not hold a borrow into
    // Python-owned memory that another Python thread could mutate or free. Accepting any
    // buffer-protocol object (bytes, bytearray, contiguous memoryview) via `PyBuffer` lets
    // the caller avoid a separate Python-side `bytes()` conversion.
    //
    // We intentionally do NOT stream across the FFI boundary: the Rust crate buffers each
    // partition into memory regardless, and a Python-backed stream would require per-chunk
    // re-attachment from parallel tasks — more complex and slower than one bulk copy.
    // For the buffered path, the crate partitions via zero-copy `Bytes::slice`.
    let buffer = PyBuffer::<u8>::get(data)?;
    if !buffer.is_c_contiguous() {
        return Err(PyValueError::new_err(
            "Native upload requires a C-contiguous buffer.",
        ));
    }
    let content: RequestContent<Bytes, NoFormat> = Bytes::from(buffer.to_vec(py)?).into();

    let mut options = BlockBlobClientUploadOptions::default();

    if !overwrite {
        options = options.if_not_exists();
    }

    if let Some(ct) = content_type {
        options.blob_content_type = Some(ct.to_string());
    }

    if let Some(meta) = metadata {
        options.metadata = Some(meta);
    }

    if let Some(concurrency) = max_concurrency {
        options.parallel = NonZero::new(concurrency);
    }

    if let Some(block_size) = max_block_size {
        options.partition_size = NonZero::new(block_size);
    }

    // Release the interpreter (detach this thread) and perform the upload on the shared tokio runtime
    let result = py
        .detach(|| {
            RUNTIME.block_on(async { blob_client.upload(content, Some(options)).await })
        })
        .map_err(AzureError::from)?;

    // Build response dict from upload result fields
    let dict = PyDict::new(py);
    if let Some(etag) = result.etag {
        dict.set_item("etag", etag.to_string())?;
    }
    if let Some(last_modified) = result.last_modified {
        dict.set_item("last_modified", last_modified.to_string())?;
    }

    Ok(dict)
}

/// Default download window size (256 MiB).
///
/// Each iteration of [`NativeDownloadStream`] fills one window via `download_into`, so peak
/// memory is bounded to a single window while the Rust SDK still performs parallel
/// partitioned range fetches *within* that window. A large window keeps that intra-window
/// parallelism high.
const DEFAULT_WINDOW_SIZE: u64 = 256 * 1024 * 1024;

/// The `Content-Range` response header (`bytes start-end/total`).
const CONTENT_RANGE: HeaderName = HeaderName::from_static("content-range");

/// Parse the total resource length from a `Content-Range: bytes start-end/total` header value.
///
/// Returns `None` if the header is malformed or the total is `*` (unknown length).
fn parse_content_range_total(value: &str) -> Option<u64> {
    let total = value.rsplit('/').next()?.trim();
    if total == "*" {
        return None;
    }
    total.parse::<u64>().ok()
}

/// A lazy, windowed blob download exposed to Python as an iterator of `bytes` chunks.
///
/// Rather than pre-allocating a single arbitrarily large buffer (which fails for blobs larger
/// than the buffer and holds the whole blob in memory), each iteration downloads one
/// `window_size`-byte window using the Rust SDK's parallel `download_into`. Throughput within a
/// window still benefits from concurrent range requests, while peak memory stays bounded to a
/// single window. The total blob size is learned from the first window's `Content-Range`
/// response header, so no separate metadata request is required.
#[pyclass]
struct NativeDownloadStream {
    client: BlobClient,
    max_concurrency: Option<usize>,
    window_size: u64,
    /// Absolute blob offset of the next window to fetch.
    next_offset: u64,
    /// Absolute end offset (exclusive) of the overall requested region.
    end_offset: u64,
    /// Total number of bytes this stream will deliver.
    size: u64,
    /// First window, downloaded eagerly during construction so `size` is known immediately
    /// and the first chunk is ready without another round trip.
    pending: Option<Py<PyBytes>>,
    etag: Option<String>,
    last_modified: Option<String>,
}

impl NativeDownloadStream {
    /// Download a single window `[offset, offset + len)` into a fresh buffer and return it as
    /// Python `bytes` along with the number of bytes actually written. Releases the GIL during
    /// the network/IO operation.
    fn fetch_window<'py>(
        client: &BlobClient,
        max_concurrency: Option<usize>,
        py: Python<'py>,
        offset: u64,
        len: u64,
    ) -> PyResult<(Bound<'py, PyBytes>, u64)> {
        let mut options = BlobClientDownloadOptions::default();
        options.range = Some(HttpRange::new(offset, len));
        if let Some(concurrency) = max_concurrency {
            options.parallel = NonZero::new(concurrency);
        }

        let (buffer, written) = py.detach(move || {
            RUNTIME.block_on(async {
                let mut buffer = vec![0u8; len as usize];
                let result = client
                    .download_into(&mut buffer, Some(options))
                    .await
                    .map_err(AzureError::from)?;
                buffer.truncate(result.len);
                Ok::<(Vec<u8>, u64), PyErr>((buffer, result.len as u64))
            })
        })?;

        Ok((PyBytes::new(py, &buffer), written))
    }
}

#[pymethods]
impl NativeDownloadStream {
    /// Total number of bytes this stream will deliver.
    #[getter]
    fn size(&self) -> u64 {
        self.size
    }

    /// The blob's ETag, if reported by the service.
    #[getter]
    fn etag(&self) -> Option<String> {
        self.etag.clone()
    }

    /// The blob's last-modified timestamp, if reported by the service.
    #[getter]
    fn last_modified(&self) -> Option<String> {
        self.last_modified.clone()
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    /// Return the next window as `bytes`, or `None` (StopIteration) when the blob is exhausted.
    fn __next__(&mut self, py: Python<'_>) -> PyResult<Option<Py<PyBytes>>> {
        if let Some(chunk) = self.pending.take() {
            return Ok(Some(chunk));
        }
        if self.next_offset >= self.end_offset {
            return Ok(None);
        }
        let remaining = self.end_offset - self.next_offset;
        let len = remaining.min(self.window_size);
        let (chunk, written) =
            NativeDownloadStream::fetch_window(&self.client, self.max_concurrency, py, self.next_offset, len)?;
        // Guard against a zero-length read so a truncated/short response can't loop forever.
        if written == 0 {
            return Ok(None);
        }
        self.next_offset += written;
        Ok(Some(chunk.unbind()))
    }
}

/// Begin a windowed download of a block blob.
///
/// Returns a [`NativeDownloadStream`] that yields the blob content one window at a time. The
/// first window is fetched eagerly so the total `size` is known immediately (parsed from the
/// `Content-Range` header) and the first chunk is ready without an extra round trip.
#[pyfunction]
#[pyo3(signature = (
    url,
    *,
    token_provider = None,
    offset = None,
    length = None,
    max_concurrency = None,
    max_chunk_size = None,
))]
fn download_blob(
    py: Python<'_>,
    url: &str,
    token_provider: Option<Py<PyAny>>,
    offset: Option<u64>,
    length: Option<u64>,
    max_concurrency: Option<usize>,
    max_chunk_size: Option<u64>,
) -> PyResult<NativeDownloadStream> {
    let blob_client = build_blob_client(url, token_provider)?;

    // A window size of 0 would make no progress; clamp to at least 1 byte.
    let window_size = max_chunk_size.unwrap_or(DEFAULT_WINDOW_SIZE).max(1);
    let start = offset.unwrap_or(0);
    // First window is bounded by the window size and, if the caller requested a range, by the
    // requested length.
    let first_len = match length {
        Some(l) => l.min(window_size),
        None => window_size,
    };

    let mut options = BlobClientDownloadOptions::default();
    options.range = Some(HttpRange::new(start, first_len));
    if let Some(concurrency) = max_concurrency {
        options.parallel = NonZero::new(concurrency);
    }

    // Fetch the first window and, from its response, learn the total blob size and properties.
    // The closure borrows `blob_client` (only `&self` is needed by `download_into`) so we retain
    // ownership afterwards for the returned stream.
    let (buffer, written, content_range_total, content_length, etag, last_modified) =
        py.detach(|| {
            RUNTIME.block_on(async {
                let mut buffer = vec![0u8; first_len as usize];
                let result = blob_client
                    .download_into(&mut buffer, Some(options))
                    .await
                    .map_err(AzureError::from)?;
                buffer.truncate(result.len);
                let content_range_total = result
                    .headers
                    .get_optional_str(&CONTENT_RANGE)
                    .and_then(parse_content_range_total);
                let content_length = result.properties.content_length;
                let etag = result.properties.etag.map(|e| e.to_string());
                let last_modified = result.properties.last_modified.map(|d| d.to_string());
                Ok::<_, PyErr>((
                    buffer,
                    result.len as u64,
                    content_range_total,
                    content_length,
                    etag,
                    last_modified,
                ))
            })
        })?;

    // The total addressable size of the blob. Prefer the `Content-Range` total; fall back to
    // the response `Content-Length`, then to what we actually read.
    let total_blob_size = content_range_total.or(content_length).unwrap_or(start + written);

    let end_offset = match length {
        Some(l) => (start + l).min(total_blob_size),
        None => total_blob_size,
    };
    let size = end_offset.saturating_sub(start);

    let pending = Some(PyBytes::new(py, &buffer).unbind());

    Ok(NativeDownloadStream {
        client: blob_client,
        max_concurrency,
        window_size,
        next_offset: start + written,
        end_offset,
        size,
        pending,
        etag,
        last_modified,
    })
}

/// Python module definition.
#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(upload_blob, m)?)?;
    m.add_function(wrap_pyfunction!(download_blob, m)?)?;
    m.add_class::<NativeDownloadStream>()?;
    Ok(())
}

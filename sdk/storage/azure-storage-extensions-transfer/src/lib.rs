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
use std::str::FromStr;
use std::sync::{Arc, Mutex, RwLock};

use azure_core::credentials::{AccessToken, Secret, TokenCredential, TokenRequestOptions};
use azure_core::http::headers::HeaderName;
use azure_core::http::{
    new_http_client, HttpClientOptions, NoFormat, RequestContent, Transport, Url,
};
use azure_core::Bytes;
use azure_storage_blob::models::{
    AccessTier, BlobClientDownloadOptions, BlockBlobClientUploadOptions, EncryptionAlgorithmType,
    HttpRange, ImmutabilityPolicyMode,
};
use azure_storage_blob::{BlobClient, BlobClientOptions};
use once_cell::sync::Lazy;
use pyo3::buffer::PyBuffer;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use tokio::runtime::Runtime;

/// An immutable Python buffer retained as the owner of a zero-copy [`Bytes`] value.
///
/// `PyBuffer` keeps the exporter and its allocation alive until it is dropped. Uploads only
/// construct this owner from Python `bytes`, whose contents cannot be mutated while Rust reads
/// them without the GIL.
struct PythonBytesOwner {
    buffer: PyBuffer<u8>,
}

impl AsRef<[u8]> for PythonBytesOwner {
    fn as_ref(&self) -> &[u8] {
        // SAFETY: construction requires a C-contiguous Python `bytes` object. Its allocation is
        // immutable and remains exported (and therefore alive) through `self.buffer`.
        unsafe {
            std::slice::from_raw_parts(self.buffer.buf_ptr().cast::<u8>(), self.buffer.len_bytes())
        }
    }
}

/// Shared tokio runtime — created once, reused across all calls to avoid
/// per-call overhead of spawning a new runtime.
static RUNTIME: Lazy<Runtime> =
    Lazy::new(|| Runtime::new().expect("Failed to create tokio runtime"));

/// Shared HTTP transport — a single connection pool reused by every `BlobClient` we build.
///
/// Each `BlobClient` otherwise constructs its own HTTP client (and therefore its own
/// connection pool), so building a fresh client per transfer would repeat TLS handshakes and
/// discard warm connections. Injecting one shared transport keeps the pool warm across calls.
///
/// Automatic decompression is disabled to guarantee the crate receives raw bytes for
/// partitioned/ranged downloads (matching the storage default for range requests).
static SHARED_TRANSPORT: Lazy<Transport> = Lazy::new(|| {
    Transport::new(new_http_client(Some(HttpClientOptions {
        automatic_decompression: false,
    })))
});

/// Process-wide token credentials keyed by the identity of their Python credential.
static CACHED_CREDENTIALS: Lazy<Mutex<HashMap<usize, Arc<PyCallbackCredential>>>> =
    Lazy::new(|| Mutex::new(HashMap::new()));

fn get_cached_credential(provider: Py<PyAny>, credential_id: usize) -> Arc<PyCallbackCredential> {
    let mut cached = CACHED_CREDENTIALS
        .lock()
        .unwrap_or_else(|poisoned| poisoned.into_inner());
    cached
        .entry(credential_id)
        .or_insert_with(|| Arc::new(PyCallbackCredential::new(provider)))
        .clone()
}

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
/// If `token_provider` is provided, `credential_id` is required and selects the cached
/// credential (fetching a token from Python once and reusing it). If the `blob_url` contains
/// a SAS token in the query string, pass `token_provider=None`.
///
/// Every client is built with the shared transport so connection pooling persists across
/// transfers regardless of authentication mode.
fn build_blob_client(
    blob_url: &str,
    token_provider: Option<Py<PyAny>>,
    credential_id: Option<usize>,
) -> Result<BlobClient, AzureError> {
    let blob_url = Url::parse(blob_url).map_err(|e| {
        azure_core::Error::with_message(
            azure_core::error::ErrorKind::Other,
            format!("Invalid URL: {}", e),
        )
    })?;

    // Reuse one shared connection pool across every client we build.
    let mut options = BlobClientOptions::default();
    options.client_options.transport = Some(SHARED_TRANSPORT.clone());

    let credential: Option<Arc<dyn TokenCredential>> = match token_provider {
        Some(provider) => {
            let credential_id = credential_id.ok_or_else(|| {
                AzureError(azure_core::Error::with_message(
                    azure_core::error::ErrorKind::Credential,
                    "credential_id is required when token_provider is provided",
                ))
            })?;
            Some(get_cached_credential(provider, credential_id))
        }
        None => None,
    };

    let client = BlobClient::new(blob_url, credential, Some(options)).map_err(AzureError::from)?;
    Ok(client)
}

/// A `TokenCredential` that delegates to a Python callable on every request.
///
/// We hold a Python "token provider" (`Py<PyAny>`) and additionally cache the last token it
/// returned. The cache lets the credential serve tokens without re-entering Python on every
/// request; when the cached token nears expiry the provider is invoked again, so refresh
/// still flows back to the real Python credential (e.g. `DefaultAzureCredential`).
///
/// The provider has the signature `provider(scopes: list[str]) -> (token: str, expires_on: int)`
/// where `expires_on` is a Unix timestamp in seconds.
///
/// Thread-safety: the provider is an immutable `Py<PyAny>` (`Send + Sync`); the token cache is
/// guarded by an `RwLock`. Concurrent callers take the read path and return the cached token;
/// a refresh takes the write lock so callers coalesce onto a single Python invocation.
#[derive(Debug)]
struct PyCallbackCredential {
    provider: Py<PyAny>,
    /// Cached token as `(token, expiry)`. Stored as components rather than an `AccessToken`
    /// so we don't rely on `Secret` being cloneable.
    cache: RwLock<Option<(String, azure_core::time::OffsetDateTime)>>,
}

impl PyCallbackCredential {
    fn new(provider: Py<PyAny>) -> Self {
        Self {
            provider,
            cache: RwLock::new(None),
        }
    }
}

#[async_trait::async_trait]
impl TokenCredential for PyCallbackCredential {
    async fn get_token(
        &self,
        scopes: &[&str],
        _options: Option<TokenRequestOptions<'_>>,
    ) -> azure_core::Result<AccessToken> {
        // Refresh a little ahead of expiry, mirroring the bearer-token policy's own window, so
        // callers always receive a token with comfortable remaining lifetime.
        const REFRESH_WINDOW_SECS: i64 = 300;
        let now = azure_core::time::OffsetDateTime::now_utc().unix_timestamp();

        // Fast path: return the cached token if it is still comfortably valid. This is what
        // avoids re-invoking the Python credential on every transfer, since each new
        // `BlobClient` starts with a cold per-pipeline token cache.
        {
            let cache = self
                .cache
                .read()
                .unwrap_or_else(|poisoned| poisoned.into_inner());
            if let Some((token, expires)) = cache.as_ref() {
                if expires.unix_timestamp() - now > REFRESH_WINDOW_SECS {
                    return Ok(AccessToken::new(Secret::new(token.clone()), *expires));
                }
            }
        }

        // Slow path: fetch a fresh token. Hold the write lock across the fetch so concurrent
        // callers coalesce onto a single refresh rather than each calling into Python.
        let mut cache = self
            .cache
            .write()
            .unwrap_or_else(|poisoned| poisoned.into_inner());
        if let Some((token, expires)) = cache.as_ref() {
            if expires.unix_timestamp() - now > REFRESH_WINDOW_SECS {
                return Ok(AccessToken::new(Secret::new(token.clone()), *expires));
            }
        }

        // Re-attach the current thread to the interpreter (valid to do inside the outer
        // `detach`) and call the Python token provider to obtain a fresh token and its
        // real expiry.
        let (token, expires) = Python::attach(|py| {
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
            Ok::<(String, azure_core::time::OffsetDateTime), azure_core::Error>((token, expires))
        })?;

        *cache = Some((token.clone(), expires));
        Ok(AccessToken::new(Secret::new(token), expires))
    }
}

const DEFAULT_PARTITION_SIZE: u64 = 4 * 1024 * 1024;

fn transfer_sizes(
    max_concurrency: Option<usize>,
    partition_size: Option<u64>,
) -> Result<(NonZero<usize>, NonZero<u64>), String> {
    let concurrency = match max_concurrency {
        Some(value) => NonZero::new(value)
            .ok_or_else(|| "max_concurrency must be greater than zero.".to_string())?,
        None => std::thread::available_parallelism()
            .unwrap_or(NonZero::new(8).expect("Fallback concurrency is nonzero")),
    };
    let partition_size = NonZero::new(partition_size.unwrap_or(DEFAULT_PARTITION_SIZE))
        .ok_or_else(|| "Chunk/block size must be greater than zero.".to_string())?;
    Ok((concurrency, partition_size))
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
    credential_id = None,
    overwrite = false,
    content_type = None,
    content_encoding = None,
    content_language = None,
    content_disposition = None,
    cache_control = None,
    content_md5 = None,
    metadata = None,
    tags = None,
    lease_id = None,
    encryption_key = None,
    encryption_key_sha256 = None,
    encryption_algorithm = None,
    encryption_scope = None,
    if_match = None,
    if_none_match = None,
    if_modified_since = None,
    if_unmodified_since = None,
    if_tags = None,
    immutability_policy_expiry = None,
    immutability_policy_mode = None,
    legal_hold = None,
    tier = None,
    timeout = None,
    max_concurrency = None,
    max_block_size = None,
))]
fn upload_blob<'py>(
    py: Python<'py>,
    url: &str,
    data: &Bound<'py, PyAny>,
    token_provider: Option<Py<PyAny>>,
    credential_id: Option<usize>,
    overwrite: bool,
    content_type: Option<&str>,
    content_encoding: Option<&str>,
    content_language: Option<&str>,
    content_disposition: Option<&str>,
    cache_control: Option<&str>,
    content_md5: Option<Vec<u8>>,
    metadata: Option<HashMap<String, String>>,
    tags: Option<HashMap<String, String>>,
    lease_id: Option<&str>,
    encryption_key: Option<&str>,
    encryption_key_sha256: Option<&str>,
    encryption_algorithm: Option<&str>,
    encryption_scope: Option<&str>,
    if_match: Option<&str>,
    if_none_match: Option<&str>,
    if_modified_since: Option<i64>,
    if_unmodified_since: Option<i64>,
    if_tags: Option<&str>,
    immutability_policy_expiry: Option<i64>,
    immutability_policy_mode: Option<&str>,
    legal_hold: Option<bool>,
    tier: Option<&str>,
    timeout: Option<i32>,
    max_concurrency: Option<usize>,
    max_block_size: Option<u64>,
) -> PyResult<Bound<'py, PyDict>> {
    let blob_client = build_blob_client(url, token_provider, credential_id)?;

    // Export the Python allocation and make it the owner of `Bytes`. This passes its address
    // across the FFI boundary without copying; `Bytes` keeps the export alive while the Rust SDK
    // clones and slices the body across asynchronous upload tasks.
    if !data.is_instance_of::<PyBytes>() {
        return Err(PyValueError::new_err(
            "Native zero-copy upload requires an immutable bytes object.",
        ));
    }
    let buffer = PyBuffer::<u8>::get(data)?;
    if !buffer.is_c_contiguous() {
        return Err(PyValueError::new_err(
            "Native upload requires a C-contiguous buffer.",
        ));
    }
    let content: RequestContent<Bytes, NoFormat> =
        Bytes::from_owner(PythonBytesOwner { buffer }).into();

    let mut options = BlockBlobClientUploadOptions::default();

    let has_access_conditions = if_match.is_some()
        || if_none_match.is_some()
        || if_modified_since.is_some()
        || if_unmodified_since.is_some()
        || if_tags.is_some();
    if !overwrite && !has_access_conditions {
        options = options.if_not_exists();
    }

    if let Some(ct) = content_type {
        options.blob_content_type = Some(ct.to_string());
    }

    if let Some(encoding) = content_encoding {
        options.blob_content_encoding = Some(encoding.to_string());
    }

    if let Some(language) = content_language {
        options.blob_content_language = Some(language.to_string());
    }

    if let Some(disposition) = content_disposition {
        options.blob_content_disposition = Some(disposition.to_string());
    }

    if let Some(control) = cache_control {
        options.blob_cache_control = Some(control.to_string());
    }

    options.blob_content_md5 = content_md5;

    if let Some(meta) = metadata {
        options.metadata = Some(meta);
    }

    if let Some(tags) = tags {
        options = options.with_tags(tags);
    }

    options.lease_id = lease_id.map(str::to_string);
    options.encryption_key = encryption_key.map(str::to_string);
    options.encryption_key_sha256 = encryption_key_sha256.map(str::to_string);
    options.encryption_scope = encryption_scope.map(str::to_string);
    options.if_match = if_match.map(Into::into);
    options.if_none_match = if_none_match.map(Into::into);
    options.if_modified_since = if_modified_since
        .map(azure_core::time::OffsetDateTime::from_unix_timestamp)
        .transpose()
        .map_err(|e| PyValueError::new_err(format!("Invalid if_modified_since value: {e}")))?;
    options.if_unmodified_since = if_unmodified_since
        .map(azure_core::time::OffsetDateTime::from_unix_timestamp)
        .transpose()
        .map_err(|e| PyValueError::new_err(format!("Invalid if_unmodified_since value: {e}")))?;
    options.if_tags = if_tags.map(str::to_string);
    options.immutability_policy_expiry = immutability_policy_expiry
        .map(azure_core::time::OffsetDateTime::from_unix_timestamp)
        .transpose()
        .map_err(|e| {
            PyValueError::new_err(format!("Invalid immutability policy expiry value: {e}"))
        })?;
    options.legal_hold = legal_hold;
    options.per_request_timeout = timeout;

    if let Some(algorithm) = encryption_algorithm {
        options.encryption_algorithm = Some(
            EncryptionAlgorithmType::from_str(algorithm)
                .map_err(|e| PyValueError::new_err(e.to_string()))?,
        );
    }

    if let Some(mode) = immutability_policy_mode {
        options.immutability_policy_mode = Some(
            ImmutabilityPolicyMode::from_str(mode)
                .map_err(|e| PyValueError::new_err(e.to_string()))?,
        );
    }

    if let Some(tier) = tier {
        options.tier =
            Some(AccessTier::from_str(tier).map_err(|e| PyValueError::new_err(e.to_string()))?);
    }

    let (concurrency, block_size) =
        transfer_sizes(max_concurrency, max_block_size).map_err(PyValueError::new_err)?;
    options.parallel = Some(concurrency);
    options.partition_size = Some(block_size);

    // Release the interpreter (detach this thread) and perform the upload on the shared tokio runtime
    let result = py
        .detach(|| RUNTIME.block_on(async { blob_client.upload(content, Some(options)).await }))
        .map_err(AzureError::from)?;

    // Build response dict from upload result fields
    let dict = PyDict::new(py);
    if let Some(etag) = result.etag {
        dict.set_item("etag", etag.to_string())?;
    }
    if let Some(last_modified) = result.last_modified {
        dict.set_item("last_modified", last_modified.to_string())?;
    }
    if let Some(content_md5) = result.content_md5 {
        dict.set_item("content_md5", PyBytes::new(py, &content_md5))?;
    }
    if let Some(content_crc64) = result.content_crc64 {
        dict.set_item("content_crc64", PyBytes::new(py, &content_crc64))?;
    }
    if let Some(encryption_key_sha256) = result.encryption_key_sha256 {
        dict.set_item("encryption_key_sha256", encryption_key_sha256)?;
    }
    if let Some(encryption_scope) = result.encryption_scope {
        dict.set_item("encryption_scope", encryption_scope)?;
    }
    if let Some(version_id) = result.version_id {
        dict.set_item("version_id", version_id)?;
    }

    Ok(dict)
}

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
    download_options: BlobClientDownloadOptions<'static>,
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
}

impl NativeDownloadStream {
    /// Download a single window `[offset, offset + len)` into a fresh buffer and return it as
    /// Python `bytes` along with the number of bytes actually written. Releases the GIL during
    /// the network/IO operation.
    fn fetch_window<'py>(
        client: &BlobClient,
        download_options: &BlobClientDownloadOptions<'static>,
        py: Python<'py>,
        offset: u64,
        len: u64,
    ) -> PyResult<(Bound<'py, PyBytes>, u64)> {
        let mut options = download_options.clone();
        options.range = Some(HttpRange::new(offset, len));

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
        let (chunk, written) = NativeDownloadStream::fetch_window(
            &self.client,
            &self.download_options,
            py,
            self.next_offset,
            len,
        )?;
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
    credential_id = None,
    offset = None,
    length = None,
    lease_id = None,
    encryption_key = None,
    encryption_key_sha256 = None,
    encryption_algorithm = None,
    if_match = None,
    if_none_match = None,
    if_modified_since = None,
    if_unmodified_since = None,
    if_tags = None,
    version_id = None,
    timeout = None,
    max_concurrency = None,
    max_chunk_size = None,
))]
fn download_blob(
    py: Python<'_>,
    url: &str,
    token_provider: Option<Py<PyAny>>,
    credential_id: Option<usize>,
    offset: Option<u64>,
    length: Option<u64>,
    lease_id: Option<&str>,
    encryption_key: Option<&str>,
    encryption_key_sha256: Option<&str>,
    encryption_algorithm: Option<&str>,
    if_match: Option<&str>,
    if_none_match: Option<&str>,
    if_modified_since: Option<i64>,
    if_unmodified_since: Option<i64>,
    if_tags: Option<&str>,
    version_id: Option<&str>,
    timeout: Option<i32>,
    max_concurrency: Option<usize>,
    max_chunk_size: Option<u64>,
) -> PyResult<NativeDownloadStream> {
    let blob_client = build_blob_client(url, token_provider, credential_id)?;

    let (concurrency, chunk_size) =
        transfer_sizes(max_concurrency, max_chunk_size).map_err(PyValueError::new_err)?;
    let concurrency_u64 = u64::try_from(concurrency.get())
        .map_err(|e| PyValueError::new_err(format!("Invalid max_concurrency value: {e}")))?;
    let window_size = concurrency_u64
        .checked_mul(chunk_size.get())
        .ok_or_else(|| {
            PyValueError::new_err(
                "max_concurrency multiplied by max_chunk_size exceeds the supported window size.",
            )
        })?;
    let start = offset.unwrap_or(0);
    // First window is bounded by the window size and, if the caller requested a range, by the
    // requested length.
    let first_len = match length {
        Some(l) => l.min(window_size),
        None => window_size,
    };

    let mut download_options = BlobClientDownloadOptions::default();
    download_options.lease_id = lease_id.map(str::to_string);
    download_options.encryption_key = encryption_key.map(str::to_string);
    download_options.encryption_key_sha256 = encryption_key_sha256.map(str::to_string);
    download_options.if_match = if_match.map(Into::into);
    download_options.if_none_match = if_none_match.map(Into::into);
    download_options.if_modified_since = if_modified_since
        .map(azure_core::time::OffsetDateTime::from_unix_timestamp)
        .transpose()
        .map_err(|e| PyValueError::new_err(format!("Invalid if_modified_since value: {e}")))?;
    download_options.if_unmodified_since = if_unmodified_since
        .map(azure_core::time::OffsetDateTime::from_unix_timestamp)
        .transpose()
        .map_err(|e| PyValueError::new_err(format!("Invalid if_unmodified_since value: {e}")))?;
    download_options.if_tags = if_tags.map(str::to_string);
    download_options.version_id = version_id.map(str::to_string);
    download_options.timeout = timeout;
    let chunk_size = usize::try_from(chunk_size.get())
        .map_err(|e| PyValueError::new_err(format!("Invalid max_chunk_size value: {e}")))?;
    download_options.partition_size = NonZero::new(chunk_size);
    download_options.parallel = Some(concurrency);

    if let Some(algorithm) = encryption_algorithm {
        download_options.encryption_algorithm = Some(
            EncryptionAlgorithmType::from_str(algorithm)
                .map_err(|e| PyValueError::new_err(e.to_string()))?,
        );
    }

    let mut first_options = download_options.clone();
    first_options.range = Some(HttpRange::new(start, first_len));

    // Fetch the first window and, from its response, learn the total blob size.
    // The closure borrows `blob_client` (only `&self` is needed by `download_into`) so we retain
    // ownership afterwards for the returned stream.
    let (buffer, written, content_range_total, content_length) = py.detach(|| {
        RUNTIME.block_on(async {
            let mut buffer = vec![0u8; first_len as usize];
            let result = blob_client
                .download_into(&mut buffer, Some(first_options))
                .await
                .map_err(AzureError::from)?;
            buffer.truncate(result.len);
            let content_range_total = result
                .headers
                .get_optional_str(&CONTENT_RANGE)
                .and_then(parse_content_range_total);
            let content_length = result.properties.content_length;
            Ok::<_, PyErr>((
                buffer,
                result.len as u64,
                content_range_total,
                content_length,
            ))
        })
    })?;

    // The total addressable size of the blob. Prefer the `Content-Range` total; fall back to
    // the response `Content-Length`, then to what we actually read.
    let total_blob_size = content_range_total
        .or(content_length)
        .unwrap_or(start + written);

    let end_offset = match length {
        Some(l) => (start + l).min(total_blob_size),
        None => total_blob_size,
    };
    let size = end_offset.saturating_sub(start);

    let pending = Some(PyBytes::new(py, &buffer).unbind());

    Ok(NativeDownloadStream {
        client: blob_client,
        download_options,
        window_size,
        next_offset: start + written,
        end_offset,
        size,
        pending,
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

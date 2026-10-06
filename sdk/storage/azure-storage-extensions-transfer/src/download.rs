// -------------------------------------------------------------------------
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for
// license information.
// --------------------------------------------------------------------------

use std::num::NonZero;
use std::str::FromStr;

use azure_core::http::headers::HeaderName;
use azure_storage_blob::models::{BlobClientDownloadOptions, EncryptionAlgorithmType, HttpRange};
use azure_storage_blob::BlobClient;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

use crate::{build_blob_client, transfer_sizes, AzureError, RUNTIME};

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
pub(crate) struct NativeDownloadStream {
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
pub(crate) fn download_blob(
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

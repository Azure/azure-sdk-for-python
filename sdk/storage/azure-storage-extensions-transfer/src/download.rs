// -------------------------------------------------------------------------
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for
// license information.
// --------------------------------------------------------------------------

use std::num::NonZero;
use std::str::FromStr;

use azure_core::error::ErrorKind;
use azure_core::http::headers::{HeaderName, Headers};
use azure_storage_blob::models::{BlobClientDownloadOptions, EncryptionAlgorithmType, HttpRange};
use azure_storage_blob::BlobClient;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

use crate::{build_blob_client, get_runtime, transfer_sizes, AzureError};

/// The `Content-Range` response header (`bytes start-end/total`).
const CONTENT_RANGE: HeaderName = HeaderName::from_static("content-range");

/// Parse the total resource length from a `Content-Range: bytes start-end/total` header value.
///
/// Returns `None` if the header is malformed or the total is `*` (unknown length).
fn parse_content_range_total(value: &str) -> Option<u64> {
    let (range, total) = value.strip_prefix("bytes ")?.split_once('/')?;
    let total = total.parse::<u64>().ok()?;
    let (start, end) = range.split_once('-')?;
    let start = start.parse::<u64>().ok()?;
    let end = end.parse::<u64>().ok()?;
    (start <= end && end < total).then_some(total)
}

fn total_blob_size(
    headers: &Headers,
    content_length: Option<u64>,
    start: u64,
) -> azure_core::Result<u64> {
    match headers.get_optional_str(&CONTENT_RANGE) {
        Some(value) => parse_content_range_total(value).ok_or_else(|| {
            azure_core::Error::with_message(
                ErrorKind::DataConversion,
                "Missing or invalid total blob size in Content-Range.",
            )
        }),
        None if start == 0 && content_length == Some(0) => Ok(0),
        None => Err(azure_core::Error::with_message(
            ErrorKind::DataConversion,
            "Missing Content-Range; cannot determine the total blob size from a ranged response.",
        )),
    }
}

fn validate_download_length(offset: u64, expected: u64, actual: u64) -> azure_core::Result<()> {
    if actual == expected {
        return Ok(());
    }
    let kind = if actual < expected {
        std::io::ErrorKind::UnexpectedEof
    } else {
        std::io::ErrorKind::InvalidData
    };
    Err(azure_core::Error::new(
        ErrorKind::Io,
        std::io::Error::new(
            kind,
            format!(
                "Incomplete blob download: expected {expected} bytes at offset {offset}, but received {actual} bytes."
            ),
        ),
    ))
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
    failure: Option<PyErr>,
}

impl NativeDownloadStream {
    fn new(
        py: Python<'_>,
        client: BlobClient,
        download_options: BlobClientDownloadOptions<'static>,
        window_size: u64,
        start: u64,
        length: Option<u64>,
    ) -> PyResult<Self> {
        let requested_end = length
            .map(|length| {
                start.checked_add(length).ok_or_else(|| {
                    PyValueError::new_err(
                        "offset plus length exceeds the supported download range.",
                    )
                })
            })
            .transpose()?;
        let mut stream = Self {
            client,
            download_options,
            window_size,
            next_offset: start,
            end_offset: start,
            size: 0,
            pending: None,
            failure: None,
        };
        if length == Some(0) {
            return Ok(stream);
        }

        let first_len = length.unwrap_or(window_size).min(window_size);
        start.checked_add(first_len).ok_or_else(|| {
            PyValueError::new_err("offset plus window size exceeds the supported download range.")
        })?;
        let buffer_len = usize::try_from(first_len)
            .map_err(|e| PyValueError::new_err(format!("Invalid download window size: {e}")))?;
        let mut first_options = stream.download_options.clone();
        first_options.range = Some(HttpRange::new(start, first_len));

        let runtime = get_runtime()?;
        let (buffer, written, total_size) = py.detach(|| {
            runtime.block_on(async {
                let mut buffer = vec![0u8; buffer_len];
                let result = stream
                    .client
                    .download_into(&mut buffer, Some(first_options))
                    .await
                    .map_err(AzureError::from)?;
                buffer.truncate(result.len);
                let total_size =
                    total_blob_size(&result.headers, result.properties.content_length, start)
                        .map_err(AzureError::from)?;
                Ok::<_, PyErr>((buffer, result.len as u64, total_size))
            })
        })?;

        stream.end_offset = requested_end.unwrap_or(total_size).min(total_size);
        stream.size = stream.end_offset.checked_sub(start).ok_or_else(|| {
            AzureError(azure_core::Error::with_message(
                ErrorKind::DataConversion,
                "The response blob size is smaller than the requested offset.",
            ))
        })?;
        validate_download_length(start, first_len.min(stream.size), written)
            .map_err(AzureError::from)?;
        stream.next_offset = start + written;
        if written != 0 {
            stream.pending = Some(PyBytes::new(py, &buffer).unbind());
        }
        Ok(stream)
    }

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
        let buffer_len = usize::try_from(len)
            .map_err(|e| PyValueError::new_err(format!("Invalid download window size: {e}")))?;
        let mut options = download_options.clone();
        options.range = Some(HttpRange::new(offset, len));

        let runtime = get_runtime()?;
        let (buffer, written) = py.detach(move || {
            runtime.block_on(async {
                let mut buffer = vec![0u8; buffer_len];
                let result = client
                    .download_into(&mut buffer, Some(options))
                    .await
                    .map_err(AzureError::from)?;
                validate_download_length(offset, len, result.len as u64)
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
        if let Some(error) = &self.failure {
            return Err(error.clone_ref(py));
        }
        if let Some(chunk) = self.pending.take() {
            return Ok(Some(chunk));
        }
        if self.next_offset >= self.end_offset {
            return Ok(None);
        }
        let remaining = self.end_offset - self.next_offset;
        let len = remaining.min(self.window_size);
        let (chunk, written) = match NativeDownloadStream::fetch_window(
            &self.client,
            &self.download_options,
            py,
            self.next_offset,
            len,
        ) {
            Ok(result) => result,
            Err(error) => {
                self.failure = Some(error.clone_ref(py));
                return Err(error);
            }
        };
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
    download_with_client(
        py,
        blob_client,
        offset,
        length,
        lease_id,
        encryption_key,
        encryption_key_sha256,
        encryption_algorithm,
        if_match,
        if_none_match,
        if_modified_since,
        if_unmodified_since,
        if_tags,
        version_id,
        timeout,
        max_concurrency,
        max_chunk_size,
    )
}

fn download_with_client(
    py: Python<'_>,
    blob_client: BlobClient,
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

    NativeDownloadStream::new(
        py,
        blob_client,
        download_options,
        window_size,
        start,
        length,
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_support::MockHttpClient;

    #[test]
    fn content_range_totals() {
        for (value, expected) in [
            ("bytes 0-3/10", Some(10)),
            ("bytes 0-0/1", Some(1)),
            ("bytes 42-42/100", Some(100)),
            ("bytes 0-0/18446744073709551615", Some(u64::MAX)),
            ("bytes 0-1/*", None),
            ("", None),
            ("items 0-1/2", None),
            ("bytes 0-1", None),
            ("bytes x-1/2", None),
            ("bytes 0-x/2", None),
            ("bytes 0-1/x", None),
            ("bytes 0-1/18446744073709551616", None),
            ("bytes 2-1/3", None),
            ("bytes 0-2/2", None),
            ("bytes 0-0/0", None),
        ] {
            assert_eq!(parse_content_range_total(value), expected, "{value:?}");
        }
    }

    #[test]
    fn total_size_uses_range_not_response_length() {
        let mut headers = Headers::new();
        headers.insert(CONTENT_RANGE, "bytes 4-5/100");
        assert_eq!(total_blob_size(&headers, Some(2), 4).unwrap(), 100);
        for (value, content_length, start, expected) in [
            (None, Some(0), 0, Some(0)),
            (None, None, 0, None),
            (None, Some(2), 0, None),
            (None, Some(0), 1, None),
            (Some("invalid"), Some(0), 0, None),
            (Some("bytes 0-1/*"), Some(2), 0, None),
        ] {
            let mut headers = Headers::new();
            if let Some(value) = value {
                headers.insert(CONTENT_RANGE, value);
            }
            let result = total_blob_size(&headers, content_length, start);
            match expected {
                Some(total) => assert_eq!(result.unwrap(), total),
                None => assert!(matches!(
                    result.unwrap_err().kind(),
                    ErrorKind::DataConversion
                )),
            }
        }
    }

    #[test]
    fn validates_exact_short_and_excess_lengths() {
        for (expected, actual) in [(0, 0), (4, 4), (u64::MAX, u64::MAX)] {
            validate_download_length(12, expected, actual).unwrap();
        }
        for (actual, expected_kind) in [
            (3, std::io::ErrorKind::UnexpectedEof),
            (5, std::io::ErrorKind::InvalidData),
        ] {
            let error = validate_download_length(12, 4, actual).unwrap_err();
            assert!(matches!(error.kind(), ErrorKind::Io));
            let source = std::error::Error::source(&error)
                .unwrap()
                .downcast_ref::<std::io::Error>()
                .unwrap();
            assert_eq!(source.kind(), expected_kind);
        }
    }

    #[test]
    fn range_arithmetic_overflows_before_io() {
        Python::initialize();
        Python::attach(|py| {
            let mock = MockHttpClient::new(|_| panic!("Overflow must fail before HTTP"));
            for (start, length, window) in [(u64::MAX, Some(1), 1), (u64::MAX - 1, None, 2)] {
                assert!(NativeDownloadStream::new(
                    py,
                    mock.client(),
                    BlobClientDownloadOptions::default(),
                    window,
                    start,
                    length,
                )
                .is_err());
            }
            assert!(download_with_client(
                py,
                mock.client(),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                Some(2),
                Some(u64::MAX),
            )
            .is_err());
            assert!(mock.requests().is_empty());
        });
    }
}

#[cfg(test)]
#[path = "../tests/rust/download.rs"]
mod stream_tests;

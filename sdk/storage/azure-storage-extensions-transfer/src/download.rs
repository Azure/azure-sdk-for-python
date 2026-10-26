// -------------------------------------------------------------------------
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for
// license information.
// --------------------------------------------------------------------------

use std::collections::VecDeque;
use std::num::NonZero;
use std::str::FromStr;
use std::sync::{Arc, Mutex, PoisonError};

use azure_core::error::ErrorKind;
use azure_core::http::headers::{HeaderName, Headers};
use azure_core::http::{AsyncResponseBody, Etag};
use azure_core::Bytes;
use azure_storage_blob::models::{BlobClientDownloadOptions, EncryptionAlgorithmType, HttpRange};
use azure_storage_blob::BlobClient;
use futures::StreamExt;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use tokio::sync::mpsc;
use tokio::task::JoinHandle;

use crate::{build_blob_client, get_runtime, transfer_sizes, AzureError, DEFAULT_PARTITION_SIZE};

/// The `Content-Range` response header (`bytes start-end/total`).
const CONTENT_RANGE: HeaderName = HeaderName::from_static("content-range");
const ETAG: HeaderName = HeaderName::from_static("etag");

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

type Chunk = azure_core::Result<Bytes>;

/// Aborts the wrapped task when dropped, so abandoned downloads stop issuing requests.
struct AbortOnDrop<T>(JoinHandle<T>);

impl<T> Drop for AbortOnDrop<T> {
    fn drop(&mut self) {
        self.0.abort();
    }
}

fn task_error(error: tokio::task::JoinError) -> azure_core::Error {
    azure_core::Error::with_message(ErrorKind::Other, format!("Download task failed: {error}"))
}

fn to_usize(value: u64) -> azure_core::Result<usize> {
    usize::try_from(value).map_err(|e| {
        azure_core::Error::with_message(
            ErrorKind::DataConversion,
            format!("Download range does not fit in memory: {e}"),
        )
    })
}

/// Read a response body that must contain exactly `len` bytes into one contiguous chunk.
///
/// A single-frame body is returned without copying; multi-frame bodies are merged into one
/// buffer sized up front.
async fn read_body(mut body: AsyncResponseBody, offset: u64, len: u64) -> Chunk {
    let mut single: Option<Bytes> = None;
    let mut merged: Vec<u8> = Vec::new();
    let mut received: u64 = 0;
    while let Some(frame) = body.next().await {
        let frame = frame?;
        received = received.saturating_add(frame.len() as u64);
        if received > len {
            validate_download_length(offset, len, received)?;
        }
        if merged.is_empty() {
            match single.take() {
                None => {
                    single = Some(frame);
                    continue;
                }
                Some(previous) => {
                    merged.reserve_exact(to_usize(len)?);
                    merged.extend_from_slice(&previous);
                }
            }
        }
        merged.extend_from_slice(&frame);
    }
    validate_download_length(offset, len, received)?;
    Ok(single.unwrap_or_else(|| Bytes::from(merged)))
}

/// Download exactly one partition-sized (or smaller) range with a single request.
async fn fetch_range(
    client: Arc<BlobClient>,
    mut options: BlobClientDownloadOptions<'static>,
    offset: u64,
    len: u64,
) -> Chunk {
    options.range = Some(HttpRange::new(offset, len));
    let response = client.download(Some(options)).await?;
    read_body(response.body, offset, len).await
}

enum PumpStop {
    /// The consumer dropped the receiving end; stop quietly.
    Closed,
    Failed(azure_core::Error),
}

impl From<azure_core::Error> for PumpStop {
    fn from(error: azure_core::Error) -> Self {
        Self::Failed(error)
    }
}

/// Everything needed to deliver the rest of a download after the first response's headers.
struct Pump {
    client: Arc<BlobClient>,
    /// Options for every request after the first, ETag-locked to the first response.
    options: BlobClientDownloadOptions<'static>,
    /// Unread body of the first response, covering `[first_offset, rest_offset)`.
    first_body: AsyncResponseBody,
    first_offset: u64,
    rest_offset: u64,
    end_offset: u64,
    partition_size: u64,
    parallel: usize,
}

impl Pump {
    /// Stream the download into `sender` in order, one partition per message.
    async fn run(self, sender: mpsc::Sender<Chunk>) {
        if let Err(PumpStop::Failed(error)) = self.forward(&sender).await {
            let _ = sender.send(Err(error)).await;
        }
    }

    async fn forward(self, sender: &mpsc::Sender<Chunk>) -> Result<(), PumpStop> {
        let Pump {
            client,
            options,
            first_body,
            first_offset,
            rest_offset,
            end_offset,
            partition_size,
            parallel,
        } = self;
        let send = |chunk: Bytes| async move {
            sender.send(Ok(chunk)).await.map_err(|_| PumpStop::Closed)
        };
        // Ranged requests run as separate tasks so they progress (and copy) in parallel, while
        // results are delivered strictly in order. Completed-but-undelivered ranges stay in the
        // queue, so buffered memory is bounded by `parallel` partitions plus the channel.
        let mut in_flight: VecDeque<AbortOnDrop<Chunk>> = VecDeque::with_capacity(parallel);
        let mut next_offset = rest_offset;
        let mut fill = |in_flight: &mut VecDeque<AbortOnDrop<Chunk>>, limit: usize| {
            while in_flight.len() < limit && next_offset < end_offset {
                let len = (end_offset - next_offset).min(partition_size);
                in_flight.push_back(AbortOnDrop(tokio::spawn(fetch_range(
                    client.clone(),
                    options.clone(),
                    next_offset,
                    len,
                ))));
                next_offset += len;
            }
        };

        // The first body is still streaming on its own connection; keep the total at `parallel`.
        fill(&mut in_flight, parallel.saturating_sub(1).max(1));
        send(read_body(first_body, first_offset, rest_offset - first_offset).await?).await?;
        while let Some(mut task) = in_flight.pop_front() {
            fill(&mut in_flight, parallel);
            let chunk = (&mut task.0).await.map_err(task_error)??;
            send(chunk).await?;
        }
        Ok(())
    }
}

enum StreamState {
    /// The first response's headers have arrived; nothing has been consumed yet.
    NotStarted(Box<Pump>),
    /// A background pump is prefetching partitions into the channel. The pump handle is held
    /// only so that dropping this state aborts the pump.
    Streaming {
        receiver: mpsc::Receiver<Chunk>,
        _pump: AbortOnDrop<()>,
    },
    Done,
    Failed(PyErr),
}

/// A lazy blob download exposed to Python as an iterator of `bytes` chunks.
///
/// Construction sends a single ranged request for the first partition and waits only for its
/// headers, so the total `size` (from `Content-Range`) and the blob ETag are known after about
/// one round trip. Every later request is locked to that ETag.
///
/// Iterating starts a background pump that keeps up to `parallel` single-partition range requests
/// in flight and prefetches completed partitions into a bounded channel (about one window of
/// `parallel * partition_size` bytes), so the network keeps working while Python consumes data.
/// Each yielded chunk is one partition.
#[pyclass]
pub(crate) struct NativeDownloadStream {
    /// Total number of bytes this stream will deliver.
    size: u64,
    /// Absolute blob offset of the next byte to deliver.
    next_offset: u64,
    /// Absolute end offset (exclusive) of the overall requested region.
    end_offset: u64,
    /// Prefetch channel capacity, in partitions.
    prefetch: usize,
    // A Mutex makes the non-`Sync` response body safe to hold in a Python object; access always
    // goes through `&mut self`, so it is never contended.
    state: Mutex<StreamState>,
}

impl NativeDownloadStream {
    fn new(
        py: Python<'_>,
        client: BlobClient,
        download_options: BlobClientDownloadOptions<'static>,
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
            size: 0,
            next_offset: start,
            end_offset: start,
            prefetch: 1,
            state: Mutex::new(StreamState::Done),
        };
        if length == Some(0) {
            return Ok(stream);
        }

        let partition_size = download_options
            .partition_size
            .map_or(DEFAULT_PARTITION_SIZE, |size| size.get() as u64);
        let parallel = download_options.parallel.map_or(1, NonZero::get);
        let first_len = length.unwrap_or(partition_size).min(partition_size);
        start.checked_add(first_len).ok_or_else(|| {
            PyValueError::new_err("offset plus chunk size exceeds the supported download range.")
        })?;
        let mut first_options = download_options.clone();
        first_options.range = Some(HttpRange::new(start, first_len));

        let client = Arc::new(client);
        let runtime = get_runtime()?;
        let response = py
            .detach(|| runtime.block_on(client.download(Some(first_options))))
            .map_err(AzureError::from)?;
        let total_size =
            total_blob_size(&response.headers, response.properties.content_length, start)
                .map_err(AzureError::from)?;

        stream.end_offset = requested_end.unwrap_or(total_size).min(total_size);
        stream.size = stream.end_offset.checked_sub(start).ok_or_else(|| {
            AzureError(azure_core::Error::with_message(
                ErrorKind::DataConversion,
                "The response blob size is smaller than the requested offset.",
            ))
        })?;
        stream.prefetch = parallel;
        if stream.size == 0 {
            return Ok(stream);
        }

        let mut options = download_options;
        if let Some(etag) = response.headers.get_optional_str(&ETAG) {
            // Lock later ranges to the version served first
            options.if_match = Some(Etag::from(etag));
            options.if_none_match = None;
            options.if_modified_since = None;
            options.if_unmodified_since = None;
            options.if_tags = None;
        }
        stream.state = Mutex::new(StreamState::NotStarted(Box::new(Pump {
            client,
            options,
            first_body: response.body,
            first_offset: start,
            rest_offset: start + first_len.min(stream.size),
            end_offset: stream.end_offset,
            partition_size,
            parallel,
        })));
        Ok(stream)
    }

    fn fail(state: &mut StreamState, py: Python<'_>, error: PyErr) -> PyErr {
        *state = StreamState::Failed(error.clone_ref(py));
        error
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

    /// Return the next partition as `bytes`, or `None` (StopIteration) when the blob is exhausted.
    fn __next__(&mut self, py: Python<'_>) -> PyResult<Option<Py<PyBytes>>> {
        let state = self.state.get_mut().unwrap_or_else(PoisonError::into_inner);
        if matches!(state, StreamState::NotStarted(_)) {
            let runtime = get_runtime()?;
            let StreamState::NotStarted(pump) = std::mem::replace(state, StreamState::Done) else {
                unreachable!();
            };
            let (sender, receiver) = mpsc::channel(self.prefetch.max(1));
            let task = AbortOnDrop(runtime.spawn(pump.run(sender)));
            *state = StreamState::Streaming {
                receiver,
                _pump: task,
            };
        }
        let message = match state {
            StreamState::Failed(error) => return Err(error.clone_ref(py)),
            StreamState::Done | StreamState::NotStarted(_) => return Ok(None),
            StreamState::Streaming { receiver, .. } => py.detach(|| receiver.blocking_recv()),
        };
        let remaining = self.end_offset - self.next_offset;
        let chunk = match message {
            Some(Ok(chunk)) if chunk.len() as u64 <= remaining => chunk,
            Some(Ok(chunk)) => {
                let error =
                    validate_download_length(self.next_offset, remaining, chunk.len() as u64)
                        .unwrap_err();
                return Err(Self::fail(state, py, AzureError(error).into()));
            }
            Some(Err(error)) => return Err(Self::fail(state, py, AzureError(error).into())),
            None => {
                let error = validate_download_length(self.next_offset, remaining, 0).unwrap_err();
                return Err(Self::fail(state, py, AzureError(error).into()));
            }
        };
        self.next_offset += chunk.len() as u64;
        if self.next_offset == self.end_offset {
            *state = StreamState::Done;
        }
        Ok(Some(PyBytes::new(py, &chunk).unbind()))
    }
}

/// Begin a download of a block blob.
///
/// Returns a [`NativeDownloadStream`] that yields the blob content one partition at a time. The
/// first partition's response headers are awaited eagerly so the total `size` is known
/// immediately (parsed from the `Content-Range` header).
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
    // The prefetch buffer holds about one window of `concurrency * chunk_size` bytes.
    concurrency_u64
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

    NativeDownloadStream::new(py, blob_client, download_options, start, length)
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
    fn download_length_errors_use_normalized_categories() {
        Python::initialize();
        Python::attach(|py| {
            for (actual, expected) in [(3, "incomplete_read"), (5, "io")] {
                let error = validate_download_length(12, 4, actual).unwrap_err();
                let converted = PyErr::from(AzureError(error));
                assert_eq!(
                    converted
                        .value(py)
                        .getattr("kind")
                        .unwrap()
                        .extract::<String>()
                        .unwrap(),
                    expected
                );
            }
        });
    }

    #[test]
    fn range_arithmetic_overflows_before_io() {
        Python::initialize();
        Python::attach(|py| {
            let mock = MockHttpClient::new(|_| panic!("Overflow must fail before HTTP"));
            for (start, length, partition) in [(u64::MAX, Some(1), 1), (u64::MAX - 1, None, 2)] {
                let mut options = BlobClientDownloadOptions::default();
                options.partition_size = NonZero::new(partition);
                assert!(
                    NativeDownloadStream::new(py, mock.client(), options, start, length).is_err()
                );
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

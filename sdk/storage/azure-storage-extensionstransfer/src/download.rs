// -------------------------------------------------------------------------
// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License. See License.txt in the project root for
// license information.
// --------------------------------------------------------------------------

use std::mem::ManuallyDrop;
use std::num::NonZero;
use std::str::FromStr;
use std::sync::{Arc, Mutex, PoisonError};

use azure_core::error::ErrorKind;
use azure_core::http::headers::{HeaderName, Headers};
use azure_core::http::{AsyncResponseBody, Etag};
use azure_core::Bytes;
use azure_storage_blob::models::{BlobClientDownloadOptions, EncryptionAlgorithmType, HttpRange};
use azure_storage_blob::BlobClient;
use futures::future::Either;
use futures::{stream, StreamExt};
use pyo3::exceptions::{PyMemoryError, PyRuntimeError, PyValueError};
use pyo3::ffi;
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

fn length_mismatch(offset: u64, expected: u64, actual: u64) -> azure_core::Error {
    let kind = if actual < expected {
        std::io::ErrorKind::UnexpectedEof
    } else {
        std::io::ErrorKind::InvalidData
    };
    azure_core::Error::new(
        ErrorKind::Io,
        std::io::Error::new(
            kind,
            format!(
                "Incomplete blob download: expected {expected} bytes at offset {offset}, but received {actual} bytes."
            ),
        ),
    )
}

fn validate_download_length(offset: u64, expected: u64, actual: u64) -> azure_core::Result<()> {
    if actual == expected {
        Ok(())
    } else {
        Err(length_mismatch(offset, expected, actual))
    }
}

/// One partition of the download and the absolute blob offset where it starts.
struct Partition {
    offset: u64,
    data: Bytes,
}

type Chunk = azure_core::Result<Partition>;

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

/// Read a response body that must contain exactly `len` bytes into one contiguous buffer.
async fn read_body(
    mut body: AsyncResponseBody,
    offset: u64,
    len: u64,
) -> azure_core::Result<Bytes> {
    let mut data = Vec::with_capacity(to_usize(len)?);
    while let Some(frame) = body.next().await {
        let frame = frame?;
        let received = data.len() as u64 + frame.len() as u64;
        if received > len {
            return Err(length_mismatch(offset, len, received));
        }
        data.extend_from_slice(&frame);
    }
    validate_download_length(offset, len, data.len() as u64)?;
    Ok(Bytes::from(data))
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
    let data = read_body(response.body, offset, len).await?;
    Ok(Partition { offset, data })
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
    /// Deliver the download to `sender` in order, one partition per message. Stops after the first
    /// error, which is delivered as the final message, or once the consumer has gone away.
    async fn run(self, sender: mpsc::Sender<Chunk>) {
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
        let first = async move {
            read_body(first_body, first_offset, rest_offset - first_offset)
                .await
                .map(|data| Partition {
                    offset: first_offset,
                    data,
                })
        };
        // Every later range runs as its own task, so ranges download (and copy) in parallel. The
        // task is spawned only when `buffered` pulls its range, and aborted if the pump is dropped.
        let rest = (rest_offset..end_offset)
            .step_by(usize::try_from(partition_size).unwrap_or(usize::MAX))
            .map(move |offset| {
                let len = (end_offset - offset).min(partition_size);
                let mut task = AbortOnDrop(tokio::spawn(fetch_range(
                    client.clone(),
                    options.clone(),
                    offset,
                    len,
                )));
                async move {
                    (&mut task.0)
                        .await
                        .unwrap_or_else(|error| Err(task_error(error)))
                }
            });
        // `buffered` keeps at most `parallel` partitions (the first body included) in flight and
        // yields them strictly in order; ranges that finish early wait for their turn. It is only
        // polled while the channel has room, so buffered memory stays bounded.
        let mut partitions =
            stream::iter(std::iter::once(Either::Left(first)).chain(rest.map(Either::Right)))
                .buffered(parallel);
        while let Some(partition) = partitions.next().await {
            let failed = partition.is_err();
            if sender.send(partition).await.is_err() || failed {
                return;
            }
        }
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

/// Sequential, bounds-checked writer over the uninitialized buffer of a [`BytesBuilder`].
struct BytesWriter {
    ptr: *mut u8,
    len: usize,
    written: usize,
}

// SAFETY: the buffer belongs to a `bytes` object that no other code can reach until
// `BytesBuilder::build_without_gil` returns it, so the thread holding the writer has exclusive
// access.
unsafe impl Send for BytesWriter {}

impl BytesWriter {
    fn remaining(&self) -> usize {
        self.len - self.written
    }

    /// Append `data` after the bytes written so far. Writes nothing and returns `false` if it does
    /// not fit.
    fn push(&mut self, data: &[u8]) -> bool {
        if data.len() > self.remaining() {
            return false;
        }
        // SAFETY: `written..written + data.len()` lies within the buffer, which only this writer
        // writes, and `data` is a separate allocation so the ranges cannot overlap.
        unsafe {
            std::ptr::copy_nonoverlapping(data.as_ptr(), self.ptr.add(self.written), data.len());
        }
        self.written += data.len();
        true
    }
}

/// Builds a `bytes` object by writing directly into a freshly allocated, uninitialized buffer.
///
/// Unlike `PyBytes::new_with`, the buffer is not zero-filled first, which would be a full pass over
/// the result with the GIL held before any data arrives. The object is only handed out by
/// [`BytesBuilder::build_without_gil`] once every byte has been written; otherwise it is discarded
/// without ever being exposed to Python.
struct BytesBuilder<'py> {
    object: Bound<'py, PyBytes>,
    writer: BytesWriter,
}

impl<'py> BytesBuilder<'py> {
    fn new(py: Python<'py>, len: usize) -> PyResult<Self> {
        let size = ffi::Py_ssize_t::try_from(len)
            .map_err(|_| PyMemoryError::new_err("The download is too large for a bytes object."))?;
        // SAFETY: a null source asks CPython for a new `bytes` object with an uninitialized buffer
        // of `size` bytes, which may be written until the object is shared (for `size == 0` the
        // shared empty object is returned, and nothing is ever written to it). The owned reference
        // is checked for allocation failure before use.
        unsafe {
            let raw = ffi::PyBytes_FromStringAndSize(std::ptr::null(), size);
            let object = Bound::from_owned_ptr_or_err(py, raw)?.cast_into_unchecked::<PyBytes>();
            let ptr = ffi::PyBytes_AsString(raw).cast::<u8>();
            debug_assert!(!ptr.is_null());
            Ok(Self {
                object,
                writer: BytesWriter {
                    ptr,
                    len,
                    written: 0,
                },
            })
        }
    }

    /// Fill the buffer with `fill` while the GIL is released, and return the `bytes` object only
    /// if every byte was written.
    fn build_without_gil(
        mut self,
        fill: impl Send + FnOnce(&mut BytesWriter) -> azure_core::Result<()>,
    ) -> azure_core::Result<Bound<'py, PyBytes>> {
        let writer = &mut self.writer;
        self.object.py().detach(|| fill(writer))?;
        if self.writer.written != self.writer.len {
            return Err(azure_core::Error::with_message(
                ErrorKind::Other,
                "Download buffer was not completely filled.",
            ));
        }
        Ok(self.object)
    }
}

/// Receive the next partition from the pump. It must start at `expected_offset` and fit within the
/// `remaining` bytes of the download.
fn recv_partition(
    receiver: &mut mpsc::Receiver<Chunk>,
    expected_offset: u64,
    remaining: u64,
) -> azure_core::Result<Bytes> {
    let partition = receiver
        .blocking_recv()
        .ok_or_else(|| length_mismatch(expected_offset, remaining, 0))??;
    if partition.offset != expected_offset {
        return Err(azure_core::Error::with_message(
            ErrorKind::Other,
            format!(
                "Download data arrived out of order: expected data at offset {expected_offset}, but received data at offset {}.",
                partition.offset
            ),
        ));
    }
    let len = partition.data.len() as u64;
    if len > remaining {
        return Err(length_mismatch(expected_offset, remaining, len));
    }
    Ok(partition.data)
}

/// Copy every remaining pumped partition into `writer`, which must be exactly the remaining size.
fn drain_into(
    receiver: &mut mpsc::Receiver<Chunk>,
    writer: &mut BytesWriter,
    offset: u64,
) -> azure_core::Result<()> {
    while writer.remaining() > 0 {
        let expected_offset = offset + writer.written as u64;
        let remaining = writer.remaining() as u64;
        let data = recv_partition(receiver, expected_offset, remaining)?;
        if !writer.push(&data) {
            return Err(length_mismatch(
                expected_offset,
                remaining,
                data.len() as u64,
            ));
        }
    }
    Ok(())
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
/// Each yielded chunk is one partition. `readall()` instead copies the pumped partitions straight
/// into a single preallocated `bytes` object with the GIL released.
#[pyclass]
pub(crate) struct NativeDownloadStream {
    pid: u32,
    /// Total number of bytes this stream will deliver.
    size: u64,
    /// Absolute blob offset of the next byte to deliver.
    next_offset: u64,
    /// Absolute end offset (exclusive) of the overall requested region.
    end_offset: u64,
    // A Mutex makes the non-`Sync` response body safe to hold in a Python object; access always
    // goes through `&mut self`, so it is never contended.
    state: ManuallyDrop<Mutex<StreamState>>,
}

impl Drop for NativeDownloadStream {
    fn drop(&mut self) {
        if self.pid == std::process::id() {
            // SAFETY: this is the only explicit drop of state. In an inheriting child we
            // deliberately retain it rather than touch parent-owned I/O and task handles.
            unsafe { ManuallyDrop::drop(&mut self.state) };
        }
    }
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
            pid: std::process::id(),
            size: 0,
            next_offset: start,
            end_offset: start,
            state: ManuallyDrop::new(Mutex::new(StreamState::Done)),
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
        *stream.state_mut() = StreamState::NotStarted(Box::new(Pump {
            client,
            options,
            first_body: response.body,
            first_offset: start,
            rest_offset: start + first_len.min(stream.size),
            end_offset: stream.end_offset,
            partition_size,
            parallel,
        }));
        Ok(stream)
    }

    fn check_process(&self) -> PyResult<()> {
        if self.pid != std::process::id() {
            return Err(PyRuntimeError::new_err(
                "This download stream was created in a different process. \
                 Start a new download in the child process.",
            ));
        }
        Ok(())
    }

    fn state_mut(&mut self) -> &mut StreamState {
        self.state.get_mut().unwrap_or_else(PoisonError::into_inner)
    }

    /// Record `error` as the stream's terminal failure and return it.
    fn fail(&mut self, py: Python<'_>, error: azure_core::Error) -> PyErr {
        let error = PyErr::from(AzureError(error));
        *self.state_mut() = StreamState::Failed(error.clone_ref(py));
        error
    }

    /// Start the pump if needed and return its receiver, `None` once everything has been
    /// delivered, or the stream's terminal failure.
    fn receiver(&mut self, py: Python<'_>) -> PyResult<Option<&mut mpsc::Receiver<Chunk>>> {
        let runtime = get_runtime()?;
        let state = self.state_mut();
        *state = match std::mem::replace(state, StreamState::Done) {
            StreamState::NotStarted(pump) => {
                let (sender, receiver) = mpsc::channel(pump.parallel);
                StreamState::Streaming {
                    receiver,
                    _pump: AbortOnDrop(runtime.spawn(pump.run(sender))),
                }
            }
            other => other,
        };
        match state {
            StreamState::Failed(error) => Err(error.clone_ref(py)),
            StreamState::Streaming { receiver, .. } => Ok(Some(receiver)),
            StreamState::Done => Ok(None),
            StreamState::NotStarted(_) => unreachable!("the pump was started above"),
        }
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
        self.check_process()?;
        let (offset, remaining) = (self.next_offset, self.end_offset - self.next_offset);
        let Some(receiver) = self.receiver(py)? else {
            return Ok(None);
        };
        let chunk = match py.detach(|| recv_partition(receiver, offset, remaining)) {
            Ok(chunk) => chunk,
            Err(error) => return Err(self.fail(py, error)),
        };
        self.next_offset += chunk.len() as u64;
        if self.next_offset == self.end_offset {
            *self.state_mut() = StreamState::Done;
        }
        Ok(Some(PyBytes::new(py, &chunk).unbind()))
    }

    /// Return all remaining content as a single `bytes` object.
    ///
    /// The result is allocated once and the pump's partitions are copied straight into it with the
    /// GIL released, so the copy overlaps with the remaining downloads and no intermediate `bytes`
    /// objects are created. Works on a fresh stream and after partial iteration.
    fn readall(&mut self, py: Python<'_>) -> PyResult<Py<PyBytes>> {
        self.check_process()?;
        let offset = self.next_offset;
        let remaining = to_usize(self.end_offset - offset).map_err(AzureError::from)?;
        let Some(receiver) = self.receiver(py)? else {
            return Ok(PyBytes::new(py, &[]).unbind());
        };
        let result = BytesBuilder::new(py, remaining)?
            .build_without_gil(|writer| drain_into(receiver, writer, offset));
        match result {
            Ok(bytes) => {
                self.next_offset = self.end_offset;
                *self.state_mut() = StreamState::Done;
                Ok(bytes.unbind())
            }
            Err(error) => Err(self.fail(py, error)),
        }
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
    fn bytes_builder_returns_object_only_when_completely_written() {
        Python::initialize();
        Python::attach(|py| {
            let filled = BytesBuilder::new(py, 5)
                .unwrap()
                .build_without_gil(|writer| {
                    assert!(writer.push(b"ab"));
                    assert!(!writer.push(b"cdef"), "Overflowing writes are rejected");
                    assert_eq!(writer.remaining(), 3);
                    assert!(writer.push(b"cde"));
                    assert!(!writer.push(b"f"));
                    Ok(())
                })
                .unwrap();
            assert_eq!(filled.as_bytes(), b"abcde");

            let partial = BytesBuilder::new(py, 4)
                .unwrap()
                .build_without_gil(|writer| {
                    assert!(writer.push(b"ab"));
                    Ok(())
                });
            assert!(partial.is_err(), "Partly written buffers are never exposed");

            let failed = BytesBuilder::new(py, 4)
                .unwrap()
                .build_without_gil(|writer| {
                    assert!(writer.push(b"ab"));
                    Err(azure_core::Error::with_message(ErrorKind::Io, "failed"))
                });
            assert!(matches!(failed.unwrap_err().kind(), ErrorKind::Io));

            let empty = BytesBuilder::new(py, 0)
                .unwrap()
                .build_without_gil(|writer| {
                    assert!(!writer.push(b"x"));
                    Ok(())
                })
                .unwrap();
            assert!(empty.as_bytes().is_empty());
        });
    }

    #[test]
    fn readall_drain_rejects_out_of_order_partitions() {
        Python::initialize();
        Python::attach(|py| {
            let (sender, mut receiver) = mpsc::channel(4);
            for (offset, data) in [(10, b"ab"), (14, b"ef"), (12, b"cd")] {
                let data = Bytes::from_static(data);
                sender
                    .blocking_send(Ok(Partition { offset, data }))
                    .unwrap();
            }
            drop(sender);
            let error = BytesBuilder::new(py, 6)
                .unwrap()
                .build_without_gil(|writer| drain_into(&mut receiver, writer, 10))
                .unwrap_err();
            assert!(matches!(error.kind(), ErrorKind::Other));
            assert!(error.to_string().contains("expected data at offset 12"));
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
            assert!(mock.requests().is_empty());
        });
    }
}

#[cfg(test)]
#[path = "../tests/rust/download.rs"]
mod stream_tests;

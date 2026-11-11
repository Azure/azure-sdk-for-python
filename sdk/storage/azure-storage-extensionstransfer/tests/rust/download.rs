// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;
use crate::test_support::{response, MockHttpClient, RecordedRequest};
use azure_core::http::{AsyncRawResponse, StatusCode};
use std::sync::Arc;
use std::time::Duration;

const ETAG_VALUE: &str = "\"stable\"";

#[test]
fn inherited_stream_reads_fail_without_touching_state() {
    Python::initialize();
    Python::attach(|py| {
        let mock = mock_blob(b"abcdef");
        let mut download = stream(py, &mock, 0, None, 1, 2).unwrap();
        download.pid = std::process::id().wrapping_add(1);
        for error in [
            download.__next__(py).unwrap_err(),
            download.readall(py).unwrap_err(),
        ] {
            assert!(error.is_instance_of::<PyRuntimeError>(py));
            assert!(error.to_string().contains("different process"));
        }
        assert_eq!(mock.requests().len(), 1);
        download.pid = std::process::id();
        assert_eq!(read_all(&mut download, py).unwrap(), b"abcdef");
    });
}

#[test]
fn stream_drop_only_releases_resources_in_the_owning_process() {
    Python::initialize();
    Python::attach(|py| {
        for inherited in [false, true] {
            let mock = mock_blob(b"abcdef");
            let weak = Arc::downgrade(&mock);
            let mut download = stream(py, &mock, 0, None, 1, 2).unwrap();
            if inherited {
                download.pid = std::process::id().wrapping_add(1);
            }
            drop(mock);
            drop(download);
            assert_eq!(weak.upgrade().is_some(), inherited);
        }
    });
}

fn range(request: &RecordedRequest) -> Option<(usize, usize)> {
    let value = request
        .headers
        .get_optional_str(&"x-ms-range".into())
        .or_else(|| request.headers.get_optional_str(&"range".into()))?;
    let (start, end) = value
        .strip_prefix("bytes=")
        .unwrap()
        .split_once('-')
        .unwrap();
    Some((start.parse().unwrap(), end.parse().unwrap()))
}

fn header<'a>(request: &'a RecordedRequest, name: &str) -> Option<&'a str> {
    request.headers.get_optional_str(&name.to_string().into())
}

fn blob_response_with(
    request: &RecordedRequest,
    payload: &[u8],
    etag: Option<&str>,
) -> azure_core::Result<AsyncRawResponse> {
    assert_eq!(request.method, "GET");
    assert!(request.body.is_empty());
    let (start, end) = range(request).expect("Expected a ranged GET");
    assert!(start < payload.len(), "Unexpected range {start}-{end}");
    let end = end.min(payload.len() - 1);
    let body = payload[start..=end].to_vec();
    let content_range = format!("bytes {start}-{end}/{}", payload.len());
    let content_length = body.len().to_string();
    let mut headers = vec![
        ("content-range", content_range.as_str()),
        ("content-length", content_length.as_str()),
    ];
    if let Some(etag) = etag {
        headers.push(("etag", etag));
    }
    response(StatusCode::PartialContent, &headers, body)
}

fn blob_response(
    request: &RecordedRequest,
    payload: &[u8],
) -> azure_core::Result<AsyncRawResponse> {
    blob_response_with(request, payload, Some(ETAG_VALUE))
}

fn mock_blob(payload: &'static [u8]) -> Arc<MockHttpClient> {
    MockHttpClient::new(move |request| blob_response(request, payload))
}

fn stream(
    py: Python<'_>,
    mock: &Arc<MockHttpClient>,
    start: u64,
    length: Option<u64>,
    parallel: usize,
    partition: usize,
) -> PyResult<NativeDownloadStream> {
    let mut options = BlobClientDownloadOptions::default();
    options.parallel = NonZero::new(parallel);
    options.partition_size = NonZero::new(partition);
    NativeDownloadStream::new(py, mock.client(), options, start, length)
}

fn next_bytes(stream: &mut NativeDownloadStream, py: Python<'_>) -> Option<Vec<u8>> {
    stream
        .__next__(py)
        .unwrap()
        .map(|chunk| chunk.bind(py).as_bytes().to_vec())
}

fn collect_chunks(stream: &mut NativeDownloadStream, py: Python<'_>) -> Vec<Vec<u8>> {
    std::iter::from_fn(|| next_bytes(stream, py)).collect()
}

fn read_all(stream: &mut NativeDownloadStream, py: Python<'_>) -> PyResult<Vec<u8>> {
    stream
        .readall(py)
        .map(|bytes| bytes.bind(py).as_bytes().to_vec())
}

fn sorted_ranges(mock: &Arc<MockHttpClient>) -> Vec<(usize, usize)> {
    let mut actual: Vec<_> = mock
        .requests()
        .iter()
        .map(|request| range(request).unwrap())
        .collect();
    actual.sort_unstable();
    actual
}

fn assert_ranges(mock: &Arc<MockHttpClient>, expected: &[(usize, usize)]) {
    let mut expected = expected.to_vec();
    expected.sort_unstable();
    assert_eq!(sorted_ranges(mock), expected);
}

/// The first request is unconditional; every later request is locked to the first ETag.
fn assert_etag_locked(mock: &Arc<MockHttpClient>, first_start: usize) {
    for request in mock.requests() {
        let expected = match range(&request) {
            Some((start, _)) if start == first_start => None,
            _ => Some(ETAG_VALUE),
        };
        assert_eq!(header(&request, "if-match"), expected, "{request:?}");
    }
}

fn error_kind(py: Python<'_>, error: &PyErr) -> String {
    assert!(error.is_instance_of::<crate::errors::NativeTransferError>(py));
    error
        .value(py)
        .getattr("kind")
        .unwrap()
        .extract::<String>()
        .unwrap()
}

#[test]
fn construction_sends_one_request_and_chunks_are_partitions() {
    Python::initialize();
    Python::attach(|py| {
        for payload in [b"ab".as_slice(), b"abc", b"abcd", b"abcdef"] {
            let mock = mock_blob(payload);
            let mut stream = stream(py, &mock, 0, None, 1, 2).unwrap();
            assert_eq!(stream.size(), payload.len() as u64);
            assert_ranges(&mock, &[(0, 1)]);
            let chunks = collect_chunks(&mut stream, py);
            let expected: Vec<_> = payload.chunks(2).map(<[u8]>::to_vec).collect();
            assert_eq!(chunks, expected);
            let expected_ranges: Vec<_> = (0..payload.len())
                .step_by(2)
                .map(|start| (start, (start + 1).min(payload.len() - 1)))
                .collect();
            assert_ranges(&mock, &expected_ranges);
            assert_etag_locked(&mock, 0);
            let count = mock.requests().len();
            assert!(next_bytes(&mut stream, py).is_none());
            assert!(next_bytes(&mut stream, py).is_none());
            assert_eq!(mock.requests().len(), count);
        }
        // The first request asks for a full partition even on a tiny blob.
        let mock = mock_blob(b"x");
        let mut stream = stream(py, &mock, 0, None, 1, 4).unwrap();
        assert_eq!(stream.size(), 1);
        assert_eq!(next_bytes(&mut stream, py).unwrap(), b"x");
        assert!(next_bytes(&mut stream, py).is_none());
        assert_ranges(&mock, &[(0, 3)]);
    });
}

#[test]
fn parallel_partitions_are_delivered_in_order_and_etag_locked() {
    Python::initialize();
    Python::attach(|py| {
        let payload = b"abcdefghijklmn";
        // Delay an early partition so later ones complete first.
        let mock = MockHttpClient::new(move |request| {
            if range(request) == Some((2, 3)) {
                std::thread::sleep(Duration::from_millis(50));
            }
            blob_response(request, payload)
        });
        let mut stream = stream(py, &mock, 0, None, 3, 2).unwrap();
        assert_eq!(stream.size(), 14);
        assert_ranges(&mock, &[(0, 1)]);
        let chunks = collect_chunks(&mut stream, py);
        let expected: Vec<_> = payload.chunks(2).map(<[u8]>::to_vec).collect();
        assert_eq!(chunks, expected);
        assert_ranges(
            &mock,
            &[(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13)],
        );
        assert_etag_locked(&mock, 0);
    });
}

#[test]
fn multi_frame_bodies_are_merged_into_partitions() {
    Python::initialize();
    Python::attach(|py| {
        let payload = b"abcdefg";
        let framed = move |request: &RecordedRequest| {
            let (start, end) = range(request).unwrap();
            let end = end.min(payload.len() - 1);
            let mut headers = Headers::new();
            headers.insert(
                "content-range",
                format!("bytes {start}-{end}/{}", payload.len()),
            );
            headers.insert("etag", ETAG_VALUE);
            let frames: Vec<azure_core::Result<Bytes>> = payload[start..=end]
                .iter()
                .map(|byte| Ok(Bytes::copy_from_slice(&[*byte])))
                .collect();
            Ok(AsyncRawResponse::new(
                StatusCode::PartialContent,
                headers,
                Box::pin(futures::stream::iter(frames)),
            ))
        };
        let mock = MockHttpClient::new(framed);
        let mut stream = stream(py, &mock, 0, None, 2, 3).unwrap();
        assert_eq!(
            collect_chunks(&mut stream, py),
            [b"abc".to_vec(), b"def".to_vec(), b"g".to_vec()]
        );
        let mock = MockHttpClient::new(framed);
        let mut stream = self::stream(py, &mock, 0, None, 2, 3).unwrap();
        assert_eq!(read_all(&mut stream, py).unwrap(), payload);
    });
}

#[test]
fn offset_bounded_length_and_end_beyond_blob() {
    Python::initialize();
    Python::attach(|py| {
        for (offset, length, expected, expected_ranges) in [
            (2, None, b"cdefgh".as_slice(), vec![(2, 4), (5, 7)]),
            (2, Some(4), b"cdef".as_slice(), vec![(2, 4), (5, 5)]),
            (6, Some(20), b"gh".as_slice(), vec![(6, 8)]),
            (1, Some(1), b"b".as_slice(), vec![(1, 1)]),
        ] {
            for use_readall in [false, true] {
                let mock = mock_blob(b"abcdefgh");
                let mut stream = stream(py, &mock, offset, length, 1, 3).unwrap();
                assert_eq!(stream.size(), expected.len() as u64);
                let bytes = if use_readall {
                    read_all(&mut stream, py).unwrap()
                } else {
                    collect_chunks(&mut stream, py).concat()
                };
                assert_eq!(bytes, expected);
                assert_ranges(&mock, &expected_ranges);
                assert_etag_locked(&mock, offset as usize);
            }
        }
    });
}

#[test]
fn zero_length_never_requests_even_beyond_eof() {
    Python::initialize();
    Python::attach(|py| {
        let mock = MockHttpClient::new(|_| panic!("Zero length must not request"));
        for start in [0, 100, u64::MAX] {
            let mut stream = stream(py, &mock, start, Some(0), 1, 2).unwrap();
            assert_eq!(stream.size(), 0);
            assert!(next_bytes(&mut stream, py).is_none());
            assert!(read_all(&mut stream, py).unwrap().is_empty());
            assert!(next_bytes(&mut stream, py).is_none());
        }
        assert!(mock.requests().is_empty());
    });
}

fn range_error() -> azure_core::Result<AsyncRawResponse> {
    response(
        StatusCode::RequestedRangeNotSatisfiable,
        &[("x-ms-error-code", "InvalidRange"), ("content-length", "0")],
        Vec::new(),
    )
}

#[test]
fn empty_blob_fallback_and_service_range_errors() {
    Python::initialize();
    Python::attach(|py| {
        let mock = MockHttpClient::new(|request| {
            assert_eq!(request.method, "GET");
            if range(request).is_some() {
                range_error()
            } else {
                response(StatusCode::Ok, &[("content-length", "0")], Vec::new())
            }
        });
        let mut stream = stream(py, &mock, 0, None, 1, 2).unwrap();
        assert_eq!(stream.size(), 0);
        assert!(next_bytes(&mut stream, py).is_none());
        assert!(read_all(&mut stream, py).unwrap().is_empty());
        let requests = mock.requests();
        assert_eq!(requests.len(), 2);
        assert_eq!(range(&requests[0]), Some((0, 1)));
        assert_eq!(range(&requests[1]), None);
        assert!(next_bytes(&mut stream, py).is_none());
        assert_eq!(mock.requests().len(), 2);

        for offset in [0, 8, 9] {
            let mock = MockHttpClient::new(|_| range_error());
            assert!(self::stream(py, &mock, offset, None, 1, 2).is_err());
            let expected_count = if offset == 0 { 2 } else { 1 };
            assert_eq!(mock.requests().len(), expected_count);
            assert_eq!(
                range(&mock.requests()[0]),
                Some((offset as usize, offset as usize + 1))
            );
            if offset == 0 {
                assert!(range(&mock.requests()[1]).is_none());
            }
        }
    });
}

#[test]
fn invalid_initial_response_fails_construction() {
    Python::initialize();
    Python::attach(|py| {
        for (content_range, body, start) in [
            (None, b"ab".as_slice(), 0),
            (Some("not a range"), b"ab".as_slice(), 0),
            (Some("bytes 0-1/*"), b"ab".as_slice(), 0),
            (Some("bytes 0-0/1"), b"a".as_slice(), 4),
        ] {
            let mock = MockHttpClient::new(move |_| {
                let mut headers = vec![("content-length", "2")];
                if let Some(value) = content_range {
                    headers.push(("content-range", value));
                }
                response(StatusCode::PartialContent, &headers, body.to_vec())
            });
            assert!(
                stream(py, &mock, start, None, 1, 2).is_err(),
                "{content_range:?}"
            );
            assert_ranges(&mock, &[(start as usize, start as usize + 1)]);
        }
    });
}

#[test]
fn short_first_body_fails_on_first_read() {
    Python::initialize();
    Python::attach(|py| {
        for use_readall in [false, true] {
            // Content-Range promises two bytes, but the body holds only one.
            let mock = MockHttpClient::new(|request| match range(request).unwrap() {
                (0, 1) => response(
                    StatusCode::PartialContent,
                    &[("content-range", "bytes 0-1/2"), ("content-length", "2")],
                    b"a".to_vec(),
                ),
                unexpected => panic!("Unexpected range: {unexpected:?}"),
            });
            let mut stream = stream(py, &mock, 0, None, 1, 2).unwrap();
            assert_eq!(stream.size(), 2);
            let error = if use_readall {
                stream.readall(py).unwrap_err()
            } else {
                stream.__next__(py).unwrap_err()
            };
            assert_eq!(error_kind(py, &error), "incomplete_read");
            for _ in 0..2 {
                assert!(stream
                    .__next__(py)
                    .unwrap_err()
                    .value(py)
                    .is(error.value(py)));
                assert!(stream
                    .readall(py)
                    .unwrap_err()
                    .value(py)
                    .is(error.value(py)));
            }
            assert_ranges(&mock, &[(0, 1)]);
        }
    });
}

fn failing_mock(failure: &'static str) -> Arc<MockHttpClient> {
    MockHttpClient::new(
        move |request| match range(request).expect("Ranged request") {
            (2, 3) => match failure {
                "truncated" => response(
                    StatusCode::PartialContent,
                    &[("content-range", "bytes 2-3/6"), ("content-length", "2")],
                    b"c".to_vec(),
                ),
                "excess" => response(
                    StatusCode::PartialContent,
                    &[("content-range", "bytes 2-3/6"), ("content-length", "3")],
                    b"cdx".to_vec(),
                ),
                "malformed" => response(
                    StatusCode::PartialContent,
                    &[("content-range", "invalid"), ("content-length", "2")],
                    b"cd".to_vec(),
                ),
                "http" => response(
                    StatusCode::InternalServerError,
                    &[
                        ("x-ms-error-code", "InternalError"),
                        ("content-length", "0"),
                    ],
                    Vec::new(),
                ),
                _ => unreachable!(),
            },
            (start, _) if start < 6 => blob_response(request, b"abcdef"),
            unexpected => panic!("Unexpected range: {unexpected:?}"),
        },
    )
}

#[test]
fn later_partition_errors_are_terminal_and_preserve_yielded_bytes() {
    Python::initialize();
    Python::attach(|py| {
        for (failure, kind) in [
            ("truncated", "incomplete_read"),
            ("excess", "io"),
            ("malformed", "data_conversion"),
            ("http", "http"),
        ] {
            let mock = failing_mock(failure);
            let mut stream = stream(py, &mock, 0, None, 1, 2).unwrap();
            let first = stream.__next__(py).unwrap().unwrap();
            let error = stream.__next__(py).unwrap_err();
            assert_eq!(error_kind(py, &error), kind, "{failure}");
            if failure == "http" {
                assert_eq!(
                    error
                        .value(py)
                        .getattr("status_code")
                        .unwrap()
                        .extract::<u16>()
                        .unwrap(),
                    500
                );
            }
            assert!(matches!(
                stream.state.get_mut().unwrap(),
                StreamState::Failed(_)
            ));
            for _ in 0..3 {
                assert!(stream
                    .__next__(py)
                    .unwrap_err()
                    .value(py)
                    .is(error.value(py)));
                assert!(stream
                    .readall(py)
                    .unwrap_err()
                    .value(py)
                    .is(error.value(py)));
            }
            assert_eq!(stream.size(), 6);
            assert_eq!(first.bind(py).as_bytes(), b"ab");
            let ranges = sorted_ranges(&mock);
            assert!(ranges.starts_with(&[(0, 1), (2, 3)]), "{ranges:?}");
        }
    });
}

#[test]
fn readall_errors_are_terminal() {
    Python::initialize();
    Python::attach(|py| {
        for failure in ["truncated", "excess", "malformed", "http"] {
            for partial in [false, true] {
                let mock = failing_mock(failure);
                let mut stream = stream(py, &mock, 0, None, 1, 2).unwrap();
                if partial {
                    assert_eq!(next_bytes(&mut stream, py).unwrap(), b"ab");
                }
                let error = stream.readall(py).unwrap_err();
                assert!(
                    error.is_instance_of::<crate::errors::NativeTransferError>(py),
                    "{failure}"
                );
                for _ in 0..2 {
                    assert!(stream
                        .readall(py)
                        .unwrap_err()
                        .value(py)
                        .is(error.value(py)));
                    assert!(stream
                        .__next__(py)
                        .unwrap_err()
                        .value(py)
                        .is(error.value(py)));
                }
            }
        }
    });
}

#[test]
fn readall_returns_remaining_content_in_one_object() {
    Python::initialize();
    Python::attach(|py| {
        let payload = b"abcdefghijklmn";
        let mock = mock_blob(payload);
        let mut stream = stream(py, &mock, 0, None, 3, 2).unwrap();
        assert_eq!(read_all(&mut stream, py).unwrap(), payload);
        assert_ranges(
            &mock,
            &[(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13)],
        );
        assert_etag_locked(&mock, 0);
        let count = mock.requests().len();
        assert!(read_all(&mut stream, py).unwrap().is_empty());
        assert!(next_bytes(&mut stream, py).is_none());
        assert_eq!(mock.requests().len(), count);

        // A blob that fits in the first partition needs no further requests.
        let mock = mock_blob(b"ab");
        let mut stream = self::stream(py, &mock, 0, None, 3, 4).unwrap();
        assert_eq!(read_all(&mut stream, py).unwrap(), b"ab");
        assert_ranges(&mock, &[(0, 3)]);
    });
}

#[test]
fn readall_places_partitions_that_complete_out_of_order() {
    Python::initialize();
    Python::attach(|py| {
        let payload = b"abcdefghijklmn";
        // Delay an early partition so later ones complete first.
        let mock = MockHttpClient::new(move |request| {
            if range(request) == Some((2, 3)) {
                std::thread::sleep(Duration::from_millis(50));
            }
            blob_response(request, payload)
        });
        let mut stream = stream(py, &mock, 0, None, 3, 2).unwrap();
        assert_eq!(read_all(&mut stream, py).unwrap(), payload);
        assert_ranges(
            &mock,
            &[(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13)],
        );
    });
}

#[test]
fn iteration_rejects_out_of_order_partitions() {
    Python::initialize();
    Python::attach(|py| {
        let mock = mock_blob(b"abcdef");
        let mut stream = stream(py, &mock, 0, None, 1, 2).unwrap();
        // Replace the pump with a channel that delivers the second partition first.
        let (sender, receiver) = mpsc::channel(2);
        let data = Bytes::from_static(b"cd");
        sender
            .blocking_send(Ok(Partition { offset: 2, data }))
            .unwrap();
        *stream.state.get_mut().unwrap() = StreamState::Streaming {
            receiver,
            _pump: AbortOnDrop(get_runtime().unwrap().spawn(async {})),
        };
        let error = stream.__next__(py).unwrap_err();
        assert_eq!(error_kind(py, &error), "other");
        assert!(error
            .value(py)
            .to_string()
            .contains("expected data at offset 0, but received data at offset 2"));
        for _ in 0..2 {
            assert!(stream
                .__next__(py)
                .unwrap_err()
                .value(py)
                .is(error.value(py)));
            assert!(stream
                .readall(py)
                .unwrap_err()
                .value(py)
                .is(error.value(py)));
        }
    });
}

#[test]
fn readall_after_partial_iteration_returns_remainder() {
    Python::initialize();
    Python::attach(|py| {
        let payload = b"abcdefghijklmn";
        let mock = mock_blob(payload);
        let mut stream = stream(py, &mock, 0, None, 2, 2).unwrap();
        assert_eq!(next_bytes(&mut stream, py).unwrap(), b"ab");
        assert_eq!(next_bytes(&mut stream, py).unwrap(), b"cd");
        assert_eq!(read_all(&mut stream, py).unwrap(), &payload[4..]);
        assert!(read_all(&mut stream, py).unwrap().is_empty());
        assert!(next_bytes(&mut stream, py).is_none());
        assert_ranges(
            &mock,
            &[(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13)],
        );
        assert_etag_locked(&mock, 0);
    });
}

#[test]
fn prefetch_is_bounded_and_dropping_stops_the_pump() {
    Python::initialize();
    Python::attach(|py| {
        static PAYLOAD: [u8; 200] = [7; 200];
        let mock = mock_blob(&PAYLOAD);
        let mut stream = stream(py, &mock, 0, None, 2, 2).unwrap();
        assert_eq!(next_bytes(&mut stream, py).unwrap(), [7, 7]);
        std::thread::sleep(Duration::from_millis(200));
        // First request, up to `parallel` in flight, `parallel` queued in the channel, and one
        // completed partition waiting to be sent.
        let prefetched = mock.requests().len();
        assert!(prefetched <= 1 + 2 + 2 + 1, "{prefetched} requests");
        drop(stream);
        std::thread::sleep(Duration::from_millis(100));
        assert_eq!(mock.requests().len(), prefetched);
    });
}

#[test]
fn python_iteration_readall_and_size_getter() {
    Python::initialize();
    Python::attach(|py| {
        let mock = mock_blob(b"abcde");
        let stream = Py::new(py, stream(py, &mock, 0, None, 1, 2).unwrap()).unwrap();
        let object = stream.bind(py);
        assert_eq!(object.getattr("size").unwrap().extract::<u64>().unwrap(), 5);
        let iterator = object.try_iter().unwrap();
        assert!(iterator.as_any().is(object.as_any()));
        let first = iterator.clone().next().unwrap().unwrap();
        assert_eq!(first.cast::<PyBytes>().unwrap().as_bytes(), b"ab");
        let rest = object.call_method0("readall").unwrap();
        assert_eq!(rest.cast::<PyBytes>().unwrap().as_bytes(), b"cde");
        assert!(object.try_iter().unwrap().next().is_none());
        assert_eq!(object.getattr("size").unwrap().extract::<u64>().unwrap(), 5);
        assert_ranges(&mock, &[(0, 1), (2, 3), (4, 4)]);
    });
}

fn download_with_options(
    py: Python<'_>,
    mock: &Arc<MockHttpClient>,
) -> PyResult<NativeDownloadStream> {
    download_with_client(
        py,
        mock.client(),
        Some(1),
        Some(6),
        Some("lease"),
        Some("key"),
        Some("hash"),
        Some("AES256"),
        Some("\"match\""),
        Some("\"not-match\""),
        Some(1_700_000_000),
        Some(1_700_000_100),
        Some("\"tag\"='value'"),
        Some("version"),
        Some(17),
        Some(1),
        Some(3),
    )
}

#[test]
fn binding_options_reach_download_requests() {
    Python::initialize();
    Python::attach(|py| {
        for etag in [Some(ETAG_VALUE), None] {
            let mock =
                MockHttpClient::new(move |request| blob_response_with(request, b"abcdefgh", etag));
            let mut stream = download_with_options(py, &mock).unwrap();
            assert_eq!(stream.size(), 6);
            assert_eq!(next_bytes(&mut stream, py).unwrap(), b"bcd");
            assert_eq!(next_bytes(&mut stream, py).unwrap(), b"efg");
            assert!(next_bytes(&mut stream, py).is_none());
            assert_ranges(&mock, &[(1, 3), (4, 6)]);
            for request in mock.requests() {
                let first = range(&request) == Some((1, 3));
                let conditions = [
                    ("if-none-match", "\"not-match\""),
                    ("if-modified-since", "Tue, 14 Nov 2023 22:13:20 GMT"),
                    ("if-unmodified-since", "Tue, 14 Nov 2023 22:15:00 GMT"),
                    ("x-ms-if-tags", "\"tag\"='value'"),
                ];
                for (name, expected) in conditions {
                    // Once locked to the first ETag, later requests drop the other conditions.
                    let expected = (first || etag.is_none()).then_some(expected);
                    assert_eq!(header(&request, name), expected, "{name}");
                }
                let expected_if_match = match (first, etag) {
                    (false, Some(etag)) => etag,
                    _ => "\"match\"",
                };
                assert_eq!(header(&request, "if-match"), Some(expected_if_match));
                for (name, expected) in [
                    ("x-ms-lease-id", "lease"),
                    ("x-ms-encryption-key", "key"),
                    ("x-ms-encryption-key-sha256", "hash"),
                    ("x-ms-encryption-algorithm", "AES256"),
                ] {
                    assert_eq!(header(&request, name), Some(expected), "{name}");
                }
                let query: Vec<_> = request.url.query_pairs().collect();
                assert!(query
                    .iter()
                    .any(|(name, value)| name == "versionid" && value == "version"));
                assert!(query
                    .iter()
                    .any(|(name, value)| name == "timeout" && value == "17"));
            }
        }
    });
}

// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;
use crate::test_support::{response, MockHttpClient, RecordedRequest};
use azure_core::http::{AsyncRawResponse, StatusCode};
use std::sync::Arc;

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

fn blob_response(
    request: &RecordedRequest,
    payload: &[u8],
) -> azure_core::Result<AsyncRawResponse> {
    assert_eq!(request.method, "GET");
    assert!(request.body.is_empty());
    let (start, end) = range(request).expect("Expected a ranged GET");
    assert!(start < payload.len(), "Unexpected range {start}-{end}");
    let end = end.min(payload.len() - 1);
    let body = payload[start..=end].to_vec();
    response(
        StatusCode::PartialContent,
        &[
            (
                "content-range",
                &format!("bytes {start}-{end}/{}", payload.len()),
            ),
            ("content-length", &body.len().to_string()),
            ("etag", "\"stable\""),
        ],
        body,
    )
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
    NativeDownloadStream::new(
        py,
        mock.client(),
        options,
        (parallel * partition) as u64,
        start,
        length,
    )
}

fn next_bytes(stream: &mut NativeDownloadStream, py: Python<'_>) -> Option<Vec<u8>> {
    stream
        .__next__(py)
        .unwrap()
        .map(|chunk| chunk.bind(py).as_bytes().to_vec())
}

fn assert_ranges(mock: &Arc<MockHttpClient>, expected: &[(usize, usize)]) {
    let mut actual: Vec<_> = mock
        .requests()
        .iter()
        .map(|request| range(request).unwrap())
        .collect();
    let mut expected = expected.to_vec();
    actual.sort_unstable();
    expected.sort_unstable();
    assert_eq!(actual, expected);
}

#[test]
fn single_exact_and_short_final_windows_are_lazy() {
    Python::initialize();
    Python::attach(|py| {
        for payload in [b"ab".as_slice(), b"abc", b"abcd", b"abcdef"] {
            let mock = mock_blob(payload);
            let mut stream = stream(py, &mock, 0, None, 1, 2).unwrap();
            assert_eq!(stream.size(), payload.len() as u64);
            assert_eq!(mock.requests().len(), 1);
            assert_eq!(next_bytes(&mut stream, py).unwrap(), payload[..2]);
            assert_eq!(mock.requests().len(), 1, "Pending chunk must not fetch");
            let mut collected = payload[..2].to_vec();
            while let Some(chunk) = next_bytes(&mut stream, py) {
                collected.extend(chunk);
            }
            assert_eq!(collected, payload);
            let expected: Vec<_> = (0..payload.len())
                .step_by(2)
                .map(|start| {
                    // The first request asks for a full partition even on a tiny blob.
                    (start, (start + 1).min(payload.len() - 1))
                })
                .collect();
            assert_ranges(&mock, &expected);
            let count = mock.requests().len();
            assert!(next_bytes(&mut stream, py).is_none());
            assert!(next_bytes(&mut stream, py).is_none());
            assert_eq!(mock.requests().len(), count);
        }
        let mock = mock_blob(b"x");
        let mut stream = stream(py, &mock, 0, None, 1, 4).unwrap();
        assert_eq!(stream.size(), 1);
        assert_eq!(next_bytes(&mut stream, py).unwrap(), b"x");
        assert!(next_bytes(&mut stream, py).is_none());
        assert_ranges(&mock, &[(0, 3)]);
    });
}

#[test]
fn parallel_partitions_are_ordered_within_lazy_windows() {
    Python::initialize();
    Python::attach(|py| {
        let mock = mock_blob(b"abcdefghijklmn");
        let mut stream = stream(py, &mock, 0, None, 3, 2).unwrap();
        assert_eq!(stream.size(), 14);
        assert_ranges(&mock, &[(0, 1), (2, 3), (4, 5)]);
        let first = stream.__next__(py).unwrap().unwrap();
        assert_eq!(first.bind(py).as_bytes(), b"abcdef");
        assert_eq!(mock.requests().len(), 3);
        assert_eq!(next_bytes(&mut stream, py).unwrap(), b"ghijkl");
        assert_ranges(&mock, &[(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11)]);
        assert_eq!(next_bytes(&mut stream, py).unwrap(), b"mn");
        assert!(next_bytes(&mut stream, py).is_none());
        assert_eq!(first.bind(py).as_bytes(), b"abcdef");
        assert_ranges(
            &mock,
            &[(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13)],
        );
        for request in mock.requests() {
            if !matches!(range(&request), Some((0, 1) | (6, 7) | (12, 13))) {
                assert_eq!(
                    request.headers.get_optional_str(&"if-match".into()),
                    Some("\"stable\"")
                );
            }
        }
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
            let mock = mock_blob(b"abcdefgh");
            let mut stream = stream(py, &mock, offset, length, 1, 3).unwrap();
            assert_eq!(stream.size(), expected.len() as u64);
            let mut bytes = Vec::new();
            while let Some(chunk) = next_bytes(&mut stream, py) {
                bytes.extend(chunk);
            }
            assert_eq!(bytes, expected);
            assert_ranges(&mock, &expected_ranges);
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
            (Some("bytes 0-1/4"), b"a".as_slice(), 0),
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
fn later_window_errors_are_terminal_and_preserve_yielded_bytes() {
    Python::initialize();
    Python::attach(|py| {
        for failure in ["truncated", "malformed", "http"] {
            let mock =
                MockHttpClient::new(
                    move |request| match range(request).expect("Ranged request") {
                        (0, 1) => blob_response(request, b"abcdef"),
                        (2, 3) => match failure {
                            "truncated" => response(
                                StatusCode::PartialContent,
                                &[("content-range", "bytes 2-3/6"), ("content-length", "2")],
                                b"c".to_vec(),
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
                        unexpected => panic!("Unexpected range: {unexpected:?}"),
                    },
                );
            let mut stream = stream(py, &mock, 0, None, 1, 2).unwrap();
            let first = stream.__next__(py).unwrap().unwrap();
            let error = stream.__next__(py).unwrap_err();
            assert!(
                error.is_instance_of::<crate::errors::NativeTransferError>(py),
                "{failure}"
            );
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
            assert!(stream.failure.is_some());
            for _ in 0..3 {
                let repeated = stream.__next__(py).unwrap_err();
                assert!(repeated.value(py).is(error.value(py)));
            }
            assert_eq!(stream.size(), 6);
            assert_eq!(first.bind(py).as_bytes(), b"ab");
            assert_ranges(&mock, &[(0, 1), (2, 3)]);
        }
    });
}

#[test]
fn python_iteration_and_size_getter() {
    Python::initialize();
    Python::attach(|py| {
        let mock = mock_blob(b"abcde");
        let stream = Py::new(py, stream(py, &mock, 0, None, 1, 2).unwrap()).unwrap();
        let object = stream.bind(py);
        assert_eq!(object.getattr("size").unwrap().extract::<u64>().unwrap(), 5);
        let iterator = object.try_iter().unwrap();
        assert!(iterator.as_any().is(object.as_any()));
        let chunks: Vec<Vec<u8>> = iterator
            .map(|item| item.unwrap().cast::<PyBytes>().unwrap().as_bytes().to_vec())
            .collect();
        assert_eq!(chunks, [b"ab".to_vec(), b"cd".to_vec(), b"e".to_vec()]);
        assert!(object.try_iter().unwrap().next().is_none());
        assert_eq!(object.getattr("size").unwrap().extract::<u64>().unwrap(), 5);
        assert_ranges(&mock, &[(0, 1), (2, 3), (4, 4)]);
    });
}

#[test]
fn binding_options_reach_download_requests() {
    Python::initialize();
    Python::attach(|py| {
        let mock = mock_blob(b"abcdefgh");
        let mut stream = download_with_client(
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
        .unwrap();
        assert_eq!(stream.size(), 6);
        assert_eq!(next_bytes(&mut stream, py).unwrap(), b"bcd");
        assert_eq!(next_bytes(&mut stream, py).unwrap(), b"efg");
        assert!(next_bytes(&mut stream, py).is_none());
        assert_ranges(&mock, &[(1, 3), (4, 6)]);
        for request in mock.requests() {
            for (header, expected) in [
                ("x-ms-lease-id", "lease"),
                ("x-ms-encryption-key", "key"),
                ("x-ms-encryption-key-sha256", "hash"),
                ("x-ms-encryption-algorithm", "AES256"),
                ("if-match", "\"match\""),
                ("if-none-match", "\"not-match\""),
                ("if-modified-since", "Tue, 14 Nov 2023 22:13:20 GMT"),
                ("if-unmodified-since", "Tue, 14 Nov 2023 22:15:00 GMT"),
                ("x-ms-if-tags", "\"tag\"='value'"),
            ] {
                assert_eq!(
                    request.headers.get_optional_str(&header.into()),
                    Some(expected),
                    "{header}"
                );
            }
            let query: Vec<_> = request.url.query_pairs().collect();
            assert!(query
                .iter()
                .any(|(name, value)| name == "versionid" && value == "version"));
            assert!(query
                .iter()
                .any(|(name, value)| name == "timeout" && value == "17"));
        }
    });
}

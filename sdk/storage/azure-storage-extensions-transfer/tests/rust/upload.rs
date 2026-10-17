// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;
use crate::test_support::{response, MockHttpClient, RecordedRequest};
use azure_core::http::{AsyncRawResponse, StatusCode};
use pyo3::types::PyString;

#[derive(Default)]
struct UploadOptions<'a> {
    overwrite: bool,
    content_type: Option<&'a str>,
    content_encoding: Option<&'a str>,
    content_language: Option<&'a str>,
    content_disposition: Option<&'a str>,
    cache_control: Option<&'a str>,
    content_md5: Option<Vec<u8>>,
    metadata: Option<HashMap<String, String>>,
    tags: Option<HashMap<String, String>>,
    lease_id: Option<&'a str>,
    encryption_key: Option<&'a str>,
    encryption_key_sha256: Option<&'a str>,
    encryption_algorithm: Option<&'a str>,
    encryption_scope: Option<&'a str>,
    if_match: Option<&'a str>,
    if_none_match: Option<&'a str>,
    if_modified_since: Option<i64>,
    if_unmodified_since: Option<i64>,
    if_tags: Option<&'a str>,
    immutability_policy_expiry: Option<i64>,
    immutability_policy_mode: Option<&'a str>,
    legal_hold: Option<bool>,
    tier: Option<&'a str>,
    timeout: Option<i32>,
    max_concurrency: Option<usize>,
    max_block_size: Option<u64>,
}

impl UploadOptions<'_> {
    fn run<'py>(
        self,
        py: Python<'py>,
        transport: &std::sync::Arc<MockHttpClient>,
        payload: &[u8],
    ) -> PyResult<Bound<'py, PyDict>> {
        upload_blob_with_client(
            py,
            transport.client(),
            PyBytes::new(py, payload).as_any(),
            self.overwrite,
            self.content_type,
            self.content_encoding,
            self.content_language,
            self.content_disposition,
            self.cache_control,
            self.content_md5,
            self.metadata,
            self.tags,
            self.lease_id,
            self.encryption_key,
            self.encryption_key_sha256,
            self.encryption_algorithm,
            self.encryption_scope,
            self.if_match,
            self.if_none_match,
            self.if_modified_since,
            self.if_unmodified_since,
            self.if_tags,
            self.immutability_policy_expiry,
            self.immutability_policy_mode,
            self.legal_hold,
            self.tier,
            self.timeout,
            self.max_concurrency,
            self.max_block_size,
        )
    }
}

fn component(request: &RecordedRequest) -> Option<String> {
    request
        .url
        .query_pairs()
        .find(|(name, _)| name == "comp")
        .map(|(_, value)| value.into_owned())
}

fn header(request: &RecordedRequest, name: &str) -> Option<String> {
    request
        .headers
        .iter()
        .find(|(key, _)| key.as_str() == name)
        .map(|(_, value)| value.as_str().to_owned())
}

fn created(request: &RecordedRequest) -> azure_core::Result<AsyncRawResponse> {
    assert_eq!(request.method, "PUT");
    match component(request).as_deref() {
        None | Some("block") | Some("blocklist") => {
            response(StatusCode::Created, &[], Bytes::new())
        }
        other => panic!("Unexpected upload request: {other:?}"),
    }
}

#[test]
fn upload_empty_small_and_exact_partition_boundary() {
    Python::initialize();
    for payload in [b"".as_slice(), b"abc".as_slice(), b"abcd".as_slice()] {
        let transport = MockHttpClient::new(|request| {
            assert_eq!(component(request), None);
            created(request)
        });
        Python::attach(|py| {
            let result = UploadOptions {
                max_block_size: Some(4),
                ..Default::default()
            }
            .run(py, &transport, payload)
            .unwrap();
            assert!(result.is_empty());
        });
        let requests = transport.requests();
        assert_eq!(requests.len(), 1);
        assert_eq!(requests[0].body, payload);
        assert_eq!(
            header(&requests[0], "content-length"),
            Some(payload.len().to_string())
        );
        assert_eq!(
            header(&requests[0], "x-ms-blob-type").as_deref(),
            Some("BlockBlob")
        );
        assert_eq!(header(&requests[0], "if-none-match").as_deref(), Some("*"));
    }
}

#[test]
fn upload_partitioned_stages_exact_contents_and_commits_in_payload_order() {
    Python::initialize();
    let transport = MockHttpClient::new(|request| {
        assert!(matches!(
            component(request).as_deref(),
            Some("block" | "blocklist")
        ));
        created(request)
    });
    Python::attach(|py| {
        assert!(UploadOptions {
            max_concurrency: Some(3),
            max_block_size: Some(4),
            ..Default::default()
        }
        .run(py, &transport, b"abcdefghij")
        .unwrap()
        .is_empty());
    });
    let requests = transport.requests();
    assert_eq!(requests.len(), 4);
    let stages: Vec<_> = requests
        .iter()
        .filter(|r| component(r).as_deref() == Some("block"))
        .collect();
    assert_eq!(stages.len(), 3);
    let commits: Vec<_> = requests
        .iter()
        .filter(|r| component(r).as_deref() == Some("blocklist"))
        .collect();
    assert_eq!(commits.len(), 1);
    let xml = std::str::from_utf8(&commits[0].body).unwrap();
    let committed_ids: Vec<_> = xml
        .split("<Latest>")
        .skip(1)
        .map(|value| value.split("</Latest>").next().unwrap())
        .collect();
    assert_eq!(committed_ids.len(), 3, "{xml}");
    for (id, expected) in committed_ids
        .iter()
        .zip([b"abcd".as_slice(), b"efgh", b"ij"])
    {
        let matches: Vec<_> = stages
            .iter()
            .filter(|request| {
                request
                    .url
                    .query_pairs()
                    .any(|(name, value)| name == "blockid" && value == *id)
            })
            .collect();
        assert_eq!(matches.len(), 1);
        assert_eq!(matches[0].body, expected);
    }
    assert_eq!(header(commits[0], "if-none-match").as_deref(), Some("*"));
    assert!(stages.iter().all(|r| header(r, "if-none-match").is_none()));
}

#[test]
fn upload_overwrite_and_explicit_access_conditions() {
    Python::initialize();
    let cases = [
        (UploadOptions::default(), Some(("if-none-match", "*"))),
        (
            UploadOptions {
                overwrite: true,
                ..Default::default()
            },
            None,
        ),
        (
            UploadOptions {
                if_match: Some("\"etag\""),
                ..Default::default()
            },
            Some(("if-match", "\"etag\"")),
        ),
        (
            UploadOptions {
                if_none_match: Some("\"other\""),
                ..Default::default()
            },
            Some(("if-none-match", "\"other\"")),
        ),
        (
            UploadOptions {
                if_modified_since: Some(0),
                ..Default::default()
            },
            Some(("if-modified-since", "Thu, 01 Jan 1970 00:00:00 GMT")),
        ),
        (
            UploadOptions {
                if_unmodified_since: Some(0),
                ..Default::default()
            },
            Some(("if-unmodified-since", "Thu, 01 Jan 1970 00:00:00 GMT")),
        ),
        (
            UploadOptions {
                if_tags: Some("\"key\"='value'"),
                ..Default::default()
            },
            Some(("x-ms-if-tags", "\"key\"='value'")),
        ),
    ];
    for (options, expected) in cases {
        let transport = MockHttpClient::new(created);
        Python::attach(|py| {
            options.run(py, &transport, b"body").unwrap();
        });
        let requests = transport.requests();
        assert_eq!(requests.len(), 1);
        if let Some((name, value)) = expected {
            assert_eq!(header(&requests[0], name).as_deref(), Some(value));
        }
        if !matches!(expected, Some(("if-none-match", _))) {
            assert_eq!(header(&requests[0], "if-none-match"), None);
        }
    }
}

#[test]
fn upload_grouped_options_reach_single_and_partitioned_requests() {
    Python::initialize();
    for block_size in [64, 4] {
        let transport = MockHttpClient::new(created);
        Python::attach(|py| {
            UploadOptions {
                content_type: Some("text/plain"),
                content_encoding: Some("gzip"),
                content_language: Some("en-US"),
                content_disposition: Some("attachment"),
                cache_control: Some("no-cache"),
                content_md5: Some(vec![1, 2, 3]),
                metadata: Some(HashMap::from([("owner".into(), "offline".into())])),
                tags: Some(HashMap::from([("key".into(), "value with space".into())])),
                lease_id: Some("lease-id"),
                encryption_key: Some("a2V5"),
                encryption_key_sha256: Some("aGFzaA=="),
                encryption_algorithm: Some("AES256"),
                encryption_scope: Some("scope"),
                if_match: Some("\"etag\""),
                if_modified_since: Some(0),
                if_unmodified_since: Some(86400),
                if_tags: Some("\"key\"='value'"),
                immutability_policy_expiry: Some(172800),
                immutability_policy_mode: Some("locked"),
                legal_hold: Some(true),
                tier: Some("Cool"),
                timeout: Some(17),
                max_concurrency: Some(2),
                max_block_size: Some(block_size),
                ..Default::default()
            }
            .run(py, &transport, b"abcdefghij")
            .unwrap();
        });
        let requests = transport.requests();
        assert_eq!(requests.len(), if block_size == 64 { 1 } else { 4 });
        let finals: Vec<_> = requests
            .iter()
            .filter(|r| component(r).as_deref() != Some("block"))
            .collect();
        assert_eq!(finals.len(), 1);
        for (name, expected) in [
            ("x-ms-blob-content-type", "text/plain"),
            ("x-ms-blob-content-encoding", "gzip"),
            ("x-ms-blob-content-language", "en-US"),
            ("x-ms-blob-content-disposition", "attachment"),
            ("x-ms-blob-cache-control", "no-cache"),
            ("x-ms-blob-content-md5", "AQID"),
            ("x-ms-meta-owner", "offline"),
            ("if-match", "\"etag\""),
            ("if-modified-since", "Thu, 01 Jan 1970 00:00:00 GMT"),
            ("if-unmodified-since", "Fri, 02 Jan 1970 00:00:00 GMT"),
            ("x-ms-if-tags", "\"key\"='value'"),
            ("x-ms-access-tier", "Cool"),
            (
                "x-ms-immutability-policy-until-date",
                "Sat, 03 Jan 1970 00:00:00 GMT",
            ),
            ("x-ms-immutability-policy-mode", "locked"),
            ("x-ms-legal-hold", "true"),
        ] {
            assert_eq!(header(finals[0], name).as_deref(), Some(expected), "{name}");
        }
        let tags = header(finals[0], "x-ms-tags").unwrap();
        let tags_url =
            azure_core::http::Url::parse(&format!("https://example.test/?{tags}")).unwrap();
        assert_eq!(
            tags_url.query_pairs().collect::<Vec<_>>(),
            [("key".into(), "value with space".into())]
        );
        assert!(header(finals[0], "if-none-match").is_none());
        for request in &requests {
            for (name, expected) in [
                ("x-ms-lease-id", "lease-id"),
                ("x-ms-encryption-key", "a2V5"),
                ("x-ms-encryption-key-sha256", "aGFzaA=="),
                ("x-ms-encryption-algorithm", "AES256"),
                ("x-ms-encryption-scope", "scope"),
            ] {
                assert_eq!(header(request, name).as_deref(), Some(expected), "{name}");
            }
            assert!(request
                .url
                .query_pairs()
                .any(|(name, value)| name == "timeout" && value == "17"));
        }
    }
}

#[test]
fn upload_response_contains_exact_supported_python_types() {
    Python::initialize();
    for block_size in [64, 4] {
        let transport = MockHttpClient::new(|request| {
            created(request)?;
            response(
                StatusCode::Created,
                &[
                    ("etag", "\"result\""),
                    ("last-modified", "Wed, 21 Oct 2015 07:28:00 GMT"),
                    ("content-md5", "AQID"),
                    ("x-ms-content-crc64", "BAUG"),
                    ("x-ms-encryption-key-sha256", "hash"),
                    ("x-ms-encryption-scope", "scope"),
                    ("x-ms-version-id", "version"),
                ],
                Bytes::new(),
            )
        });
        Python::attach(|py| {
            let result = UploadOptions {
                max_block_size: Some(block_size),
                ..Default::default()
            }
            .run(py, &transport, b"abcdefghij")
            .unwrap();
            assert_eq!(result.len(), 7);
            for (name, expected) in [
                ("etag", "\"result\""),
                ("last_modified", "2015-10-21 7:28:00.0 +00:00:00"),
                ("encryption_key_sha256", "hash"),
                ("encryption_scope", "scope"),
                ("version_id", "version"),
            ] {
                let value = result.get_item(name).unwrap().unwrap();
                assert!(value.is_exact_instance_of::<PyString>(), "{name}");
                assert_eq!(value.extract::<String>().unwrap(), expected);
            }
            for (name, expected) in [("content_md5", [1, 2, 3]), ("content_crc64", [4, 5, 6])] {
                let value = result.get_item(name).unwrap().unwrap();
                assert!(value.is_exact_instance_of::<PyBytes>(), "{name}");
                assert_eq!(value.cast::<PyBytes>().unwrap().as_bytes(), expected);
            }
        });
        assert_eq!(
            transport.requests().len(),
            if block_size == 64 { 1 } else { 4 }
        );
    }
}

#[test]
fn upload_failures_return_errors_and_failed_block_never_commits() {
    Python::initialize();
    for block_size in [64, 4] {
        let transport = MockHttpClient::new(move |request| {
            assert_eq!(request.method, "PUT");
            assert_eq!(
                component(request).as_deref(),
                if block_size == 64 {
                    None
                } else {
                    Some("block")
                }
            );
            response(
                StatusCode::BadRequest,
                &[("x-ms-error-code", "InvalidBlock")],
                Bytes::from_static(
                    b"<Error><Code>InvalidBlock</Code><Message>offline failure</Message></Error>",
                ),
            )
        });
        Python::attach(|py| {
            assert!(UploadOptions {
                max_block_size: Some(block_size),
                max_concurrency: Some(1),
                ..Default::default()
            }
            .run(py, &transport, b"abcdefghij")
            .is_err());
        });
        let requests = transport.requests();
        assert_eq!(requests.len(), 1);
        assert!(requests
            .iter()
            .all(|request| component(request).as_deref() != Some("blocklist")));
    }
}

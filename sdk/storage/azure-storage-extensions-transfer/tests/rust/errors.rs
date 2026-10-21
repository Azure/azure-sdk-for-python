// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;
use azure_core::http::{headers::Headers, RawResponse, StatusCode};

#[test]
fn http_errors_preserve_raw_diagnostics() {
    Python::initialize();
    Python::attach(|py| {
        for status in [
            StatusCode::Unauthorized,
            StatusCode::Forbidden,
            StatusCode::NotFound,
            StatusCode::Conflict,
            StatusCode::PreconditionFailed,
            StatusCode::RequestedRangeNotSatisfiable,
            StatusCode::TooManyRequests,
            StatusCode::InternalServerError,
        ] {
            for body in [
                b"".as_slice(),
                b"<Error><Code>BlobNotFound</Code></Error>",
                br#"{"error":{"code":"BlobNotFound"}}"#,
                b"\xff",
            ] {
                let mut headers = Headers::new();
                headers.insert("x-ms-request-id", "request-id");
                headers.insert("x-ms-error-code", "BlobNotFound");
                let raw = RawResponse::from_bytes(status, headers, body.to_vec());
                let error = azure_core::Error::with_message(
                    ErrorKind::HttpResponse {
                        status,
                        error_code: Some("BlobNotFound".into()),
                        raw_response: Some(Box::new(raw)),
                    },
                    "service failure",
                )
                .with_context("outer context");
                let converted = PyErr::from(AzureError(error));
                assert!(converted.is_instance_of::<NativeTransferError>(py));
                let value = converted.value(py);
                assert_eq!(
                    value.getattr("kind").unwrap().extract::<String>().unwrap(),
                    "http"
                );
                assert_eq!(
                    value
                        .getattr("status_code")
                        .unwrap()
                        .extract::<u16>()
                        .unwrap(),
                    u16::from(status)
                );
                assert_eq!(
                    value
                        .getattr("error_code")
                        .unwrap()
                        .extract::<String>()
                        .unwrap(),
                    "BlobNotFound"
                );
                assert_eq!(
                    value
                        .getattr("body")
                        .unwrap()
                        .cast::<PyBytes>()
                        .unwrap()
                        .as_bytes(),
                    body
                );
                assert_eq!(
                    value
                        .getattr("headers")
                        .unwrap()
                        .get_item("x-ms-request-id")
                        .unwrap()
                        .extract::<String>()
                        .unwrap(),
                    "request-id"
                );
                assert!(!value.hasattr("io_error_kind").unwrap());
            }
        }
    });
}

#[test]
fn status_only_errors_and_non_http_errors_have_complete_shape() {
    Python::initialize();
    Python::attach(|py| {
        for (kind, category) in [
            (ErrorKind::Connection, "connection"),
            (ErrorKind::Io, "io"),
            (ErrorKind::DataConversion, "data_conversion"),
            (ErrorKind::Credential, "credential"),
            (ErrorKind::Other, "other"),
            (
                ErrorKind::HttpResponse {
                    status: StatusCode::NotFound,
                    error_code: None,
                    raw_response: None,
                },
                "http",
            ),
        ] {
            let converted =
                PyErr::from(AzureError(azure_core::Error::with_message(kind, "failure")));
            let value = converted.value(py);
            assert_eq!(
                value.getattr("kind").unwrap().extract::<String>().unwrap(),
                category
            );
            assert_eq!(
                value
                    .getattr("message")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                if category == "http" {
                    "Not Found"
                } else {
                    "failure"
                }
            );
            assert_eq!(value.getattr("headers").unwrap().len().unwrap(), 0);
            assert_eq!(value.getattr("additional_info").unwrap().len().unwrap(), 0);
            for attribute in ["body", "error_code", "request_id", "normalization_error"] {
                assert!(value.getattr(attribute).unwrap().is_none(), "{attribute}");
            }
            if category == "http" {
                assert_eq!(
                    value
                        .getattr("status_code")
                        .unwrap()
                        .extract::<u16>()
                        .unwrap(),
                    404
                );
            } else {
                assert!(value.getattr("status_code").unwrap().is_none());
            }
        }
    });
}

#[test]
fn io_source_classification_survives_context() {
    Python::initialize();
    Python::attach(|py| {
        for (kind, io_kind, expected) in [
            (
                ErrorKind::Io,
                std::io::ErrorKind::UnexpectedEof,
                "incomplete_read",
            ),
            (ErrorKind::Io, std::io::ErrorKind::InvalidData, "io"),
            (ErrorKind::Io, std::io::ErrorKind::TimedOut, "io"),
            (ErrorKind::Io, std::io::ErrorKind::ConnectionReset, "io"),
            (
                ErrorKind::Connection,
                std::io::ErrorKind::UnexpectedEof,
                "connection",
            ),
        ] {
            let error = azure_core::Error::new(kind, std::io::Error::new(io_kind, "I/O failure"))
                .with_context("inner context")
                .with_context("outer context");
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
            assert!(!converted.value(py).hasattr("io_error_kind").unwrap());
        }
    });
}

fn http_error(
    header_code: Option<&str>,
    candidate_code: Option<&str>,
    body: Option<&[u8]>,
) -> azure_core::Error {
    let raw_response = body.map(|body| {
        let mut headers = Headers::new();
        headers.insert("x-ms-request-id", "request-id");
        if let Some(code) = header_code {
            headers.insert("x-ms-error-code", code.to_owned());
        }
        Box::new(RawResponse::from_bytes(
            StatusCode::Conflict,
            headers,
            body.to_vec(),
        ))
    });
    azure_core::Error::with_message(
        ErrorKind::HttpResponse {
            status: StatusCode::Conflict,
            error_code: candidate_code.map(str::to_owned),
            raw_response,
        },
        "original HTTP failure",
    )
}

#[test]
fn storage_error_normalizes_service_details_and_preserves_unknown_codes() {
    Python::initialize();
    Python::attach(|py| {
        let body = br#"<Error>
            <Code>BodyCode</Code><Message>service message</Message>
            <Reason>service reason</Reason>
            <AuthenticationErrorDetail>authentication detail</AuthenticationErrorDetail>
            <CopySourceStatusCode>403</CopySourceStatusCode>
            <CopySourceErrorCode>SourceError</CopySourceErrorCode>
            <CopySourceErrorMessage>source failure</CopySourceErrorMessage>
            <Detail>extra information</Detail><reason>shadowed reason</reason>
        </Error>"#;
        let converted = PyErr::from(AzureError(http_error(
            Some("FutureServiceCode"),
            Some("CandidateCode"),
            Some(body),
        )));
        let value = converted.value(py);
        assert_eq!(value.to_string(), "service message");
        assert_eq!(
            value
                .getattr("message")
                .unwrap()
                .extract::<String>()
                .unwrap(),
            "service message"
        );
        assert_eq!(
            value
                .getattr("error_code")
                .unwrap()
                .extract::<String>()
                .unwrap(),
            "FutureServiceCode"
        );
        assert_eq!(
            value
                .getattr("request_id")
                .unwrap()
                .extract::<String>()
                .unwrap(),
            "request-id"
        );
        assert!(value.getattr("normalization_error").unwrap().is_none());
        let additional = value
            .getattr("additional_info")
            .unwrap()
            .extract::<std::collections::HashMap<String, String>>()
            .unwrap();
        assert_eq!(
            additional,
            std::collections::HashMap::from([
                ("Detail".to_owned(), "extra information".to_owned()),
                ("reason".to_owned(), "service reason".to_owned()),
                (
                    "authentication_error_detail".to_owned(),
                    "authentication detail".to_owned()
                ),
                ("copy_source_status_code".to_owned(), "403".to_owned()),
                (
                    "copy_source_error_code".to_owned(),
                    "SourceError".to_owned()
                ),
                (
                    "copy_source_error_message".to_owned(),
                    "source failure".to_owned()
                ),
            ])
        );
        assert_eq!(
            value
                .getattr("body")
                .unwrap()
                .cast::<PyBytes>()
                .unwrap()
                .as_bytes(),
            body
        );
    });
}

#[test]
fn failed_normalization_does_not_replace_http_failure() {
    Python::initialize();
    Python::attach(|py| {
        for body in [
            b"<Error><Message>unterminated".as_slice(),
            br#"{"error":{"code":"JsonCode","message":"JSON message"}}"#,
            b"\xff",
        ] {
            let converted = PyErr::from(AzureError(http_error(
                Some("HeaderCode"),
                Some("CandidateCode"),
                Some(body),
            )));
            let value = converted.value(py);
            assert_eq!(value.to_string(), "original HTTP failure");
            assert_eq!(
                value.getattr("kind").unwrap().extract::<String>().unwrap(),
                "http"
            );
            assert_eq!(
                value
                    .getattr("status_code")
                    .unwrap()
                    .extract::<u16>()
                    .unwrap(),
                409
            );
            assert_eq!(
                value
                    .getattr("error_code")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "CandidateCode"
            );
            assert_eq!(
                value
                    .getattr("request_id")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "request-id"
            );
            assert_eq!(value.getattr("additional_info").unwrap().len().unwrap(), 0);
            assert!(!value
                .getattr("normalization_error")
                .unwrap()
                .extract::<String>()
                .unwrap()
                .is_empty());
            assert_eq!(
                value
                    .getattr("body")
                    .unwrap()
                    .cast::<PyBytes>()
                    .unwrap()
                    .as_bytes(),
                body
            );
        }
    });
}

#[test]
fn missing_fields_retain_original_diagnostics() {
    Python::initialize();
    Python::attach(|py| {
        for body in [
            None,
            Some(b"".as_slice()),
            Some(b"<Error><Code>BodyCode</Code></Error>".as_slice()),
        ] {
            let converted = PyErr::from(AzureError(http_error(None, Some("CandidateCode"), body)));
            let value = converted.value(py);
            assert_eq!(
                value
                    .getattr("error_code")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "CandidateCode"
            );
            assert!(value.getattr("normalization_error").unwrap().is_none());
            assert_eq!(
                value.to_string(),
                if body.is_none_or(|body| body.is_empty()) {
                    "Conflict"
                } else {
                    "original HTTP failure"
                }
            );
        }
        let converted = PyErr::from(AzureError(http_error(
            None,
            None,
            Some(b"<Error><Code>BodyOnlyCode</Code><Message>body message</Message></Error>"),
        )));
        assert!(converted.value(py).getattr("error_code").unwrap().is_none());
        assert_eq!(converted.value(py).to_string(), "body message");
    });
}

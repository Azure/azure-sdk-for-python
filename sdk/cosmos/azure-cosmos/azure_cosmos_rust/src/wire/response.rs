// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use pyo3::exceptions::{
    PyAttributeError, PyRuntimeError, PyRuntimeWarning, PyTypeError, PyValueError,
};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyTuple};
use serde::{Deserialize, Serialize};

use azure_data_cosmos_driver::{
    error::{CosmosError, CosmosStatus},
    models::{CosmosResponse, ResponseBody},
};

use super::diagnostics::record_diagnostics;
use super::errors::{_DriverTransportError, _UnsupportedQueryFeatureError};
use super::feed_range::{FeedRangeFromPartitionKeyError, FeedRangeFromPartitionKeyPayload};

/// Opt-in POC envelope: (unchanged response tuple, attempt payload).
/// A response-less driver exception carries the same payload privately.
pub(super) fn tuple_from_result_with_attempts<'py>(
    py: Python<'py>,
    response_result: Result<CosmosResponse, CosmosError>,
) -> PyResult<Bound<'py, PyTuple>> {
    let diagnostics = match &response_result {
        Ok(response) => Some(response.diagnostics()),
        Err(error) => error.diagnostics(),
    };
    let response = tuple_from_result(py, response_result);
    let payload = match diagnostics {
        Some(diagnostics) => {
            attempt_payload_or_error(py, super::diagnostics::attempt_payload(py, &diagnostics))
        }
        None => py.None(),
    };
    match response {
        Ok(response) => Ok(PyTuple::new_bound(
            py,
            [response.into_any().unbind(), payload],
        )),
        Err(error) => {
            if error.is_instance_of::<_DriverTransportError>(py) && !payload.is_none(py) {
                attach_attempt_payload(py, &error, payload);
            }
            Err(error)
        }
    }
}

fn attach_attempt_payload(py: Python<'_>, error: &PyErr, payload: PyObject) {
    if error
        .value_bound(py)
        .setattr("_cosmos_attempt_payload", payload)
        .is_err()
    {
        const MESSAGE: &str =
            "Rust attempt POC could not attach diagnostics; operation error is unchanged";
        if PyErr::warn_bound(py, &py.get_type_bound::<PyRuntimeWarning>(), MESSAGE, 1).is_err() {
            // Warning filters or hooks must not replace the original operation error.
            PyRuntimeWarning::new_err(MESSAGE).write_unraisable_bound(py, None);
        }
    }
}

fn attempt_payload_or_error(py: Python<'_>, payload: PyResult<Bound<'_, PyDict>>) -> PyObject {
    match payload {
        Ok(payload) => payload.into_any().unbind(),
        // Python reports rejected detail without exposing the conversion error.
        Err(_) => "attempt payload conversion failed".into_py(py),
    }
}

/// Turn the Rust driver's `Result<CosmosResponse, CosmosError>` into a
/// binding response tuple. A CosmosError carrying a response (404 / 409
/// / 412 / ...) uses the same tuple shape as success for Python's error mapping.
/// Without a response, statuses 400 and 412 become synthesized error tuples;
/// other statuses become `_DriverTransportError`. The latter does not prove a
/// transport-only failure or that no request was sent.
pub(super) fn tuple_from_result<'py>(
    py: Python<'py>,
    response_result: Result<CosmosResponse, CosmosError>,
) -> PyResult<Bound<'py, PyTuple>> {
    match response_result {
        Ok(response) => backend_response_tuple_from_success(py, response),
        Err(cosmos_error) => {
            if let Some(raw_http_error) =
                backend_response_tuple_from_cosmos_error(py, &cosmos_error)?
            {
                Ok(raw_http_error)
            } else if matches!(u16::from(cosmos_error.status().status_code()), 400 | 412) {
                let (status, sub_status) = status_code_and_sub_status(cosmos_error.status());
                let headers = PyDict::new_bound(py);
                if sub_status != 0 {
                    headers.set_item("x-ms-substatus", sub_status.to_string())?;
                }
                let diagnostics = if let Some(diagnostics) = cosmos_error.diagnostics() {
                    headers.set_item(
                        "x-ms-request-charge",
                        diagnostics.total_request_charge().to_string(),
                    )?;
                    Some(record_diagnostics(diagnostics))
                } else {
                    None
                };
                let body =
                    serde_json::to_vec(&serde_json::json!({"message": cosmos_error.to_string()}))
                        .map_err(|error| PyValueError::new_err(error.to_string()))?;
                backend_response_tuple(
                    py,
                    status,
                    sub_status,
                    headers,
                    &body,
                    diagnostics.as_deref(),
                )
            } else {
                // No wire response: combine any attached diagnostics into the
                // process-wide counters when diagnostics are available.
                record_diagnostics_for_responseless(&cosmos_error);
                // Report a typed transport error (Display preserves the
                // Cosmos status) the Python wrapper maps to
                // ServiceResponseError, rather than a bare RuntimeError.
                Err(_DriverTransportError::new_err(format!(
                    "driver execute_singleton_operation failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// Convert a query page, or synthesize an empty `{"Documents":[]}` page for `None`.
/// Unsupported-query status becomes `_UnsupportedQueryFeatureError` without
/// replaying through legacy. Other errors return an attached response tuple or,
/// without one, raise `_DriverTransportError`. Unlike the point-operation path,
/// response-less 400/412 errors are not synthesized into tuples here.
pub(super) fn tuple_from_feed_result<'py>(
    py: Python<'py>,
    response_result: Result<Option<CosmosResponse>, CosmosError>,
) -> PyResult<Bound<'py, PyTuple>> {
    match response_result {
        Ok(Some(response)) => backend_response_tuple_from_feed_success(py, response),
        Ok(None) => {
            let response_headers = PyDict::new_bound(py);
            backend_response_tuple(py, 200, 0, response_headers, br#"{"Documents":[]}"#, None)
        }
        Err(cosmos_error) => {
            if cosmos_error.status() == CosmosStatus::CLIENT_UNSUPPORTED_QUERY_FEATURE {
                return Err(_UnsupportedQueryFeatureError::new_err(
                    cosmos_error.to_string(),
                ));
            }
            if let Some(raw_http_error) =
                backend_response_tuple_from_cosmos_error_feed(py, &cosmos_error)?
            {
                Ok(raw_http_error)
            } else {
                record_diagnostics_for_responseless(&cosmos_error);
                Err(_DriverTransportError::new_err(format!(
                    "driver execute_operation failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// Database-feed variant of [`tuple_from_feed_result`].
///
/// Wraps item-list bodies in `{"Databases":[...]}` and supplies an empty envelope
/// for `None`; raw byte bodies pass through. Errors with attached responses use
/// the feed-error converter; response-less errors become `_DriverTransportError`.
/// Matching the envelope does not establish full legacy response parity.
pub(super) fn tuple_from_database_feed_result<'py>(
    py: Python<'py>,
    response_result: Result<Option<CosmosResponse>, CosmosError>,
) -> PyResult<Bound<'py, PyTuple>> {
    tuple_from_database_feed_result_for(py, response_result, "list_databases")
}

/// Convert a database-query result into a `Databases` response tuple.
/// Unsupported query plans are returned as `_UnsupportedQueryFeatureError`.
pub(super) fn tuple_from_query_databases_result<'py>(
    py: Python<'py>,
    response_result: Result<Option<CosmosResponse>, CosmosError>,
) -> PyResult<Bound<'py, PyTuple>> {
    if let Err(cosmos_error) = &response_result {
        if cosmos_error.status() == CosmosStatus::CLIENT_UNSUPPORTED_QUERY_FEATURE {
            return Err(_UnsupportedQueryFeatureError::new_err(
                cosmos_error.to_string(),
            ));
        }
    }
    tuple_from_database_feed_result_for(py, response_result, "query_databases")
}

/// Convert a container-feed result into a `DocumentCollections` response tuple.
pub(super) fn tuple_from_container_feed_result<'py>(
    py: Python<'py>,
    response_result: Result<Option<CosmosResponse>, CosmosError>,
) -> PyResult<Bound<'py, PyTuple>> {
    tuple_from_named_feed_result_for(
        py,
        response_result,
        "list_containers",
        b"DocumentCollections",
        br#"{"DocumentCollections":[]}"#,
    )
}

/// Convert a container-query result into a `DocumentCollections` response tuple.
/// Unsupported query plans are returned as `_UnsupportedQueryFeatureError`.
pub(super) fn tuple_from_query_containers_result<'py>(
    py: Python<'py>,
    response_result: Result<Option<CosmosResponse>, CosmosError>,
) -> PyResult<Bound<'py, PyTuple>> {
    if let Err(cosmos_error) = &response_result {
        if cosmos_error.status() == CosmosStatus::CLIENT_UNSUPPORTED_QUERY_FEATURE {
            return Err(_UnsupportedQueryFeatureError::new_err(
                cosmos_error.to_string(),
            ));
        }
    }
    tuple_from_named_feed_result_for(
        py,
        response_result,
        "query_containers",
        b"DocumentCollections",
        br#"{"DocumentCollections":[]}"#,
    )
}

/// Convert a database feed using the operation name in transport errors.
fn tuple_from_database_feed_result_for<'py>(
    py: Python<'py>,
    response_result: Result<Option<CosmosResponse>, CosmosError>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    tuple_from_named_feed_result_for(
        py,
        response_result,
        operation_name,
        b"Databases",
        br#"{"Databases":[]}"#,
    )
}

/// Convert a resource feed into the named JSON array used by Python.
fn tuple_from_named_feed_result_for<'py>(
    py: Python<'py>,
    response_result: Result<Option<CosmosResponse>, CosmosError>,
    operation_name: &str,
    envelope_key: &[u8],
    empty_body: &[u8],
) -> PyResult<Bound<'py, PyTuple>> {
    match response_result {
        Ok(Some(response)) => {
            backend_response_tuple_from_named_feed_success(py, response, envelope_key)
        }
        Ok(None) => {
            let response_headers = PyDict::new_bound(py);
            backend_response_tuple(py, 200, 0, response_headers, empty_body, None)
        }
        Err(cosmos_error) => {
            if let Some(raw_http_error) =
                backend_response_tuple_from_cosmos_error_feed(py, &cosmos_error)?
            {
                Ok(raw_http_error)
            } else {
                record_diagnostics_for_responseless(&cosmos_error);
                Err(_DriverTransportError::new_err(format!(
                    "driver {operation_name} failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// Return partition-key ranges in a binding response tuple.
/// Its body contains a PartitionKeyRanges list with id, minInclusive, and
/// maxExclusive fields for each range.
pub(super) fn tuple_from_partition_key_ranges_result<'py>(
    py: Python<'py>,
    response_result: Result<
        Option<Vec<azure_data_cosmos_driver::models::partition_key_range::PartitionKeyRange>>,
        CosmosError,
    >,
) -> PyResult<Bound<'py, PyTuple>> {
    match response_result {
        Ok(Some(ranges)) => {
            let response_headers = PyDict::new_bound(py);
            response_headers.set_item("content-type", "application/json")?;
            // Synthesized compatibility header, not the number of returned ranges
            // or a header copied from this operation's HTTP response.
            response_headers.set_item("x-ms-item-count", "0")?;
            let body = partition_key_ranges_to_response_body(&ranges)?;
            backend_response_tuple(py, 200, 0, response_headers, &body, None)
        }
        Ok(None) => Err(_DriverTransportError::new_err(
            "driver resolve_all_partition_key_ranges returned no routing map",
        )),
        Err(cosmos_error) => {
            if let Some(raw_http_error) =
                backend_response_tuple_from_cosmos_error_feed(py, &cosmos_error)?
            {
                Ok(raw_http_error)
            } else {
                record_diagnostics_for_responseless(&cosmos_error);
                Err(_DriverTransportError::new_err(format!(
                    "driver resolve_all_partition_key_ranges failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// Return a computed feed range in a binding response tuple.
/// Its body contains Range with min, max, isMinInclusive, and isMaxInclusive fields.
pub(super) fn tuple_from_feed_range_from_partition_key_result<'py>(
    py: Python<'py>,
    response_result: Result<FeedRangeFromPartitionKeyPayload, FeedRangeFromPartitionKeyError>,
) -> PyResult<Bound<'py, PyTuple>> {
    match response_result {
        Ok(payload) => {
            let response_headers = PyDict::new_bound(py);
            let body = feed_range_to_response_body(&payload)?;
            backend_response_tuple(py, 200, 0, response_headers, &body, None)
        }
        Err(FeedRangeFromPartitionKeyError::Validation(message)) => {
            Err(PyValueError::new_err(message))
        }
        Err(FeedRangeFromPartitionKeyError::LegacyAttribute(message)) => {
            Err(PyAttributeError::new_err(message))
        }
        Err(FeedRangeFromPartitionKeyError::LegacyType(message)) => {
            Err(PyTypeError::new_err(message))
        }
        Err(FeedRangeFromPartitionKeyError::Cosmos(cosmos_error)) => {
            if let Some(raw_http_error) =
                backend_response_tuple_from_cosmos_error_feed(py, &cosmos_error)?
            {
                Ok(raw_http_error)
            } else {
                record_diagnostics_for_responseless(&cosmos_error);
                Err(_DriverTransportError::new_err(format!(
                    "driver feed_range_from_partition_key failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// Offer-feed variant of `tuple_from_feed_result`: a complete offer/throughput query
/// uses the `{"Offers":[...]}` envelope. Single-page raw bytes pass through;
/// multiple pages are combined. No responses become an empty `{"Offers":[]}`.
/// Errors with attached responses
/// use the feed-error converter; other errors become `_DriverTransportError`,
/// without assuming they were transport-only failures.
pub(super) fn tuple_from_offer_feed_result<'py>(
    py: Python<'py>,
    response_result: Result<Vec<CosmosResponse>, CosmosError>,
) -> PyResult<Bound<'py, PyTuple>> {
    match response_result {
        Ok(responses) => backend_response_tuple_from_offer_feed_success(py, responses),
        Err(cosmos_error) => {
            if let Some(raw_http_error) =
                backend_response_tuple_from_cosmos_error_feed(py, &cosmos_error)?
            {
                Ok(raw_http_error)
            } else {
                record_diagnostics_for_responseless(&cosmos_error);
                Err(_DriverTransportError::new_err(format!(
                    "driver execute_operation failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// Put a local subset-comparison result into a binding response tuple.
/// For true, the body is `{"IsSubset":true}`; validation errors raise ValueError
/// instead of returning a tuple.
pub(super) fn tuple_from_is_feed_range_subset_result<'py>(
    py: Python<'py>,
    result: Result<bool, String>,
) -> PyResult<Bound<'py, PyTuple>> {
    match result {
        Ok(is_subset) => {
            let response_headers = PyDict::new_bound(py);
            let body: &[u8] = if is_subset {
                br#"{"IsSubset":true}"#
            } else {
                br#"{"IsSubset":false}"#
            };
            backend_response_tuple(py, 200, 0, response_headers, body, None)
        }
        Err(message) => Err(PyValueError::new_err(message)),
    }
}

/// Assemble a binding response tuple; the Python wrapper constructs BackendResponse.
/// The separate container-metadata success contract does not use this helper.
fn backend_response_tuple<'py>(
    py: Python<'py>,
    status_code: i64,
    sub_status: i64,
    response_headers: Bound<'py, PyDict>,
    body: &[u8],
    diagnostics: Option<&str>,
) -> PyResult<Bound<'py, PyTuple>> {
    // Binding response tuple contract:
    // (status_code, sub_status, headers, body, diagnostics_or_none).
    let body_py = PyBytes::new_bound(py, body);
    let diagnostics_py = match diagnostics {
        Some(value) => value.into_py(py),
        None => py.None().into_py(py),
    };
    let items: [PyObject; 5] = [
        status_code.into_py(py),
        sub_status.into_py(py),
        response_headers.into_any().unbind(),
        body_py.into_any().unbind(),
        diagnostics_py,
    ];
    Ok(PyTuple::new_bound(py, &items))
}

/// Build the reply tuple for a successful point operation: read status and
/// sub-status, record available diagnostics, convert driver headers, and copy
/// the body. An unexpected feed-shaped body is rejected.
fn backend_response_tuple_from_success<'py>(
    py: Python<'py>,
    response: azure_data_cosmos_driver::models::CosmosResponse,
) -> PyResult<Bound<'py, PyTuple>> {
    let status = response.status();
    let (status_code, sub_status) = status_code_and_sub_status(status);
    let diagnostics = record_diagnostics(response.diagnostics());
    // Convert the Rust driver's headers for Python response parsing, including
    // last_response_headers. This is not the original HTTP header collection.
    let driver_headers = response.headers();
    let response_headers = response_headers_dict(py, driver_headers)?;

    match response.into_body() {
        ResponseBody::NoPayload => backend_response_tuple(
            py,
            status_code,
            sub_status,
            response_headers,
            b"",
            Some(diagnostics.as_str()),
        ),
        ResponseBody::Bytes(body) => backend_response_tuple(
            py,
            status_code,
            sub_status,
            response_headers,
            body.as_ref(),
            Some(diagnostics.as_str()),
        ),
        ResponseBody::Items(items) => Err(PyRuntimeError::new_err(format!(
            "unexpected feed response body for point operation: got {} item(s)",
            items.len()
        ))),
    }
}

/// Convert a query page, wrapping item-list bodies in `{"Documents":[...]}`.
/// Already serialized body bytes pass through without another wrapper.
fn backend_response_tuple_from_feed_success<'py>(
    py: Python<'py>,
    response: azure_data_cosmos_driver::models::CosmosResponse,
) -> PyResult<Bound<'py, PyTuple>> {
    backend_response_tuple_from_named_feed_success(py, response, b"Documents")
}

/// Map the driver's typed `ResponseBody` to a flat `Vec<u8>` suitable for the
/// binding response tuple's body bytes, later stored in BackendResponse.body.
///
/// `NoPayload` becomes empty bytes, `Bytes` is copied, and an unexpected
/// `Items` feed body raises `PyRuntimeError`; items are not concatenated.
fn response_body_to_vec(body: ResponseBody) -> PyResult<Vec<u8>> {
    match body {
        ResponseBody::NoPayload => Ok(Vec::new()),
        ResponseBody::Bytes(b) => Ok(b.to_vec()),
        ResponseBody::Items(items) => Err(PyRuntimeError::new_err(format!(
            "unexpected feed response body for point operation: got {} item(s)",
            items.len()
        ))),
    }
}

/// Wrap item-list query results in `{"Documents":[...]}` for the Python parser.
/// `NoPayload` becomes an empty envelope. Raw `Bytes` pass through unchanged;
/// this helper does not validate or wrap their contents.
fn query_response_body_to_vec(body: ResponseBody) -> PyResult<Vec<u8>> {
    named_feed_response_body_to_vec(body, b"Documents")
}

#[derive(Deserialize, Serialize)]
struct OfferFeedBody {
    #[serde(rename = "Offers")]
    offers: Vec<Box<serde_json::value::RawValue>>,
}

/// Combine offer pages, retaining the final response's headers rather than a
/// synthetic total charge. Raw values preserve offer JSON without retyping it.
fn backend_response_tuple_from_offer_feed_success<'py>(
    py: Python<'py>,
    mut responses: Vec<CosmosResponse>,
) -> PyResult<Bound<'py, PyTuple>> {
    let Some(last) = responses.pop() else {
        return backend_response_tuple(
            py,
            200,
            0,
            PyDict::new_bound(py),
            br#"{"Offers":[]}"#,
            None,
        );
    };
    if responses.is_empty() {
        return backend_response_tuple_from_named_feed_success(py, last, b"Offers");
    }
    let (status_code, sub_status) = status_code_and_sub_status(last.status());
    let response_headers = response_headers_dict(py, last.headers())?;
    let mut body = OfferFeedBody { offers: Vec::new() };
    let mut diagnostics = String::new();
    for response in responses.into_iter().chain(std::iter::once(last)) {
        diagnostics = record_diagnostics(response.diagnostics());
        let bytes = named_feed_response_body_to_vec(response.into_body(), b"Offers")?;
        let page: OfferFeedBody = serde_json::from_slice(&bytes)
            .map_err(|error| PyValueError::new_err(format!("Invalid read_offer page: {error}")))?;
        body.offers.extend(page.offers);
    }
    let bytes = serde_json::to_vec(&body)
        .map_err(|error| PyValueError::new_err(format!("Invalid read_offer result: {error}")))?;
    backend_response_tuple(
        py,
        status_code,
        sub_status,
        response_headers,
        &bytes,
        Some(&diagnostics),
    )
}

/// Convert a successful feed response into a binding response tuple, wrapping
/// item-list bodies in the JSON object named by `envelope_name`.
///
/// One function serves `Documents`, `Databases`, `Offers`, and
/// `DocumentCollections`. The Python wrapper expects the matching field when
/// extracting rows, for example Documents for an order query.
fn backend_response_tuple_from_named_feed_success<'py>(
    py: Python<'py>,
    response: azure_data_cosmos_driver::models::CosmosResponse,
    envelope_name: &[u8],
) -> PyResult<Bound<'py, PyTuple>> {
    let status = response.status();
    let (status_code, sub_status) = status_code_and_sub_status(status);
    let diagnostics = record_diagnostics(response.diagnostics());
    let response_headers = response_headers_dict(py, response.headers())?;
    match response.into_body() {
        // Pass existing bytes straight to Python without allocating a Vec. The
        // helper keeps its Bytes arm for callers that require an owned body.
        ResponseBody::Bytes(body) => backend_response_tuple(
            py,
            status_code,
            sub_status,
            response_headers,
            body.as_ref(),
            Some(diagnostics.as_str()),
        ),
        body => {
            let body_vec = named_feed_response_body_to_vec(body, envelope_name)?;
            backend_response_tuple(
                py,
                status_code,
                sub_status,
                response_headers,
                &body_vec,
                Some(diagnostics.as_str()),
            )
        }
    }
}

/// Wrap feed items in the REST envelope named by `envelope_name`.
///
/// A raw pre-built [`ResponseBody::Bytes`] body passes through unchanged.
fn named_feed_response_body_to_vec(body: ResponseBody, envelope_name: &[u8]) -> PyResult<Vec<u8>> {
    match body {
        ResponseBody::NoPayload => {
            let mut out = Vec::with_capacity(envelope_name.len() + 7);
            out.extend_from_slice(b"{\"");
            out.extend_from_slice(envelope_name);
            out.extend_from_slice(b"\":[]}");
            Ok(out)
        }
        ResponseBody::Bytes(b) => Ok(b.to_vec()),
        ResponseBody::Items(items) => {
            let item_bytes = items.iter().map(|item| item.len()).sum::<usize>();
            let separators = items.len().saturating_sub(1);
            let mut out = Vec::with_capacity(envelope_name.len() + 7 + item_bytes + separators);
            out.extend_from_slice(b"{\"");
            out.extend_from_slice(envelope_name);
            out.extend_from_slice(b"\":[");
            for (index, item) in items.iter().enumerate() {
                if index > 0 {
                    out.push(b',');
                }
                out.extend_from_slice(item.as_ref());
            }
            out.extend_from_slice(b"]}");
            Ok(out)
        }
    }
}

#[derive(Serialize)]
struct PartitionKeyRangesEnvelope {
    #[serde(rename = "PartitionKeyRanges")]
    partition_key_ranges: Vec<PartitionKeyRangeWire>,
}

#[derive(Serialize)]
struct PartitionKeyRangeWire {
    id: String,
    #[serde(rename = "minInclusive")]
    min_inclusive: String,
    #[serde(rename = "maxExclusive")]
    max_exclusive: String,
}

#[derive(Serialize)]
struct FeedRangeEnvelope<'a> {
    #[serde(rename = "Range")]
    range: FeedRangeWire<'a>,
}

#[derive(Serialize)]
struct FeedRangeWire<'a> {
    min: &'a str,
    max: &'a str,
    #[serde(rename = "isMinInclusive")]
    is_min_inclusive: bool,
    #[serde(rename = "isMaxInclusive")]
    is_max_inclusive: bool,
}

/// Serialize the driver's partition-key ranges into the
/// `{"PartitionKeyRanges":[{id,minInclusive,maxExclusive}, ...]}` body the
/// read_feed_ranges wrapper parses.
fn partition_key_ranges_to_response_body(
    ranges: &[azure_data_cosmos_driver::models::partition_key_range::PartitionKeyRange],
) -> PyResult<Vec<u8>> {
    let partition_key_ranges = ranges
        .iter()
        .map(|range| PartitionKeyRangeWire {
            id: range.id.clone(),
            min_inclusive: range.min_inclusive.to_hex(),
            max_exclusive: range.max_exclusive.to_hex(),
        })
        .collect();
    let envelope = PartitionKeyRangesEnvelope {
        partition_key_ranges,
    };
    serde_json::to_vec(&envelope).map_err(|e| {
        PyRuntimeError::new_err(format!(
            "failed to serialize read_feed_ranges response body: {e}"
        ))
    })
}

fn feed_range_to_response_body(payload: &FeedRangeFromPartitionKeyPayload) -> PyResult<Vec<u8>> {
    let envelope = FeedRangeEnvelope {
        range: FeedRangeWire {
            min: payload.min.as_str(),
            max: payload.max.as_str(),
            is_min_inclusive: true,
            is_max_inclusive: payload.is_max_inclusive,
        },
    };
    serde_json::to_vec(&envelope).map_err(|e| {
        PyRuntimeError::new_err(format!(
            "failed to serialize feed_range_from_partition_key response body: {e}"
        ))
    })
}

/// Combine attempt counters for a response-less `CosmosError` that still carries
/// `DiagnosticsContext` (for example, a client-side end-to-end timeout that
/// tracked wire attempts before the deadline fired).
///
/// Call exactly once per response-less `CosmosError` path, **before** converting
/// to `_DriverTransportError`.  Do not call for wire-response errors -- those are
/// already counted by `backend_response_tuple_from_cosmos_error` /
/// `backend_response_tuple_from_cosmos_error_feed`.
fn record_diagnostics_for_responseless(error: &CosmosError) {
    if let Some(diag) = error.diagnostics() {
        record_diagnostics(diag);
    }
}

/// Convert an attached driver response, or return `None` if there is no response.
/// Absence alone does not distinguish a local failure from one after a request.
fn backend_response_tuple_from_cosmos_error<'py>(
    py: Python<'py>,
    error: &CosmosError,
) -> PyResult<Option<Bound<'py, PyTuple>>> {
    let response = match error.response() {
        Some(r) => r,
        None => return Ok(None),
    };

    let status = response.status();
    let (status_code, sub_status) = status_code_and_sub_status(status);
    let diagnostics = record_diagnostics(response.diagnostics());

    let response_headers = response_headers_dict(py, response.headers())?;

    let body_vec = response_body_to_vec(response.body().clone())?;
    Ok(Some(backend_response_tuple(
        py,
        status_code,
        sub_status,
        response_headers,
        &body_vec,
        Some(diagnostics.as_str()),
    )?))
}

/// Query-page version of `backend_response_tuple_from_cosmos_error`: same handling
/// of an error that carries a wire response, with the query body envelope.
fn backend_response_tuple_from_cosmos_error_feed<'py>(
    py: Python<'py>,
    error: &CosmosError,
) -> PyResult<Option<Bound<'py, PyTuple>>> {
    let response = match error.response() {
        Some(r) => r,
        None => return Ok(None),
    };

    let diagnostics = record_diagnostics(response.diagnostics());
    Ok(Some(backend_response_tuple_from_feed_error_parts(
        py,
        response.status(),
        response.headers(),
        response.body().clone(),
        diagnostics.as_str(),
    )?))
}

/// Build the Python tuple for a feed error after the driver has exposed its
/// typed wire status, headers, body, and diagnostics.
fn backend_response_tuple_from_feed_error_parts<'py>(
    py: Python<'py>,
    status: CosmosStatus,
    driver_headers: &azure_data_cosmos_driver::models::CosmosResponseHeaders,
    body: ResponseBody,
    diagnostics: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    let (status_code, sub_status) = status_code_and_sub_status(status);
    let response_headers = response_headers_dict(py, driver_headers)?;
    let body_vec = query_response_body_to_vec(body)?;
    backend_response_tuple(
        py,
        status_code,
        sub_status,
        response_headers,
        &body_vec,
        Some(diagnostics),
    )
}

/// Return the HTTP status and Cosmos substatus used by the Python response tuple.
/// Missing substatus values become zero.
fn status_code_and_sub_status(status: CosmosStatus) -> (i64, i64) {
    (
        u16::from(status.status_code()) as i64,
        status.sub_status().map(|s| s.value() as i64).unwrap_or(0),
    )
}

/// Copy the driver's `to_raw_headers()` output into a Python dict of strings.
/// Header inclusion and serialization are defined by that driver conversion;
/// this is not a copy of the original HTTP header collection or a guarantee
/// of legacy-header parity. Repeated names are overwritten by later assignments.
fn response_headers_dict<'py>(
    py: Python<'py>,
    h: &azure_data_cosmos_driver::models::CosmosResponseHeaders,
) -> PyResult<Bound<'py, PyDict>> {
    let out = PyDict::new_bound(py);
    for (name, value) in h.to_raw_headers().iter() {
        out.set_item(name.as_str(), value.as_str())?;
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::{
        _DriverTransportError, _UnsupportedQueryFeatureError, attach_attempt_payload,
        attempt_payload_or_error, backend_response_tuple_from_feed_error_parts,
        feed_range_to_response_body, named_feed_response_body_to_vec,
        record_diagnostics_for_responseless, response_body_to_vec, response_headers_dict,
        tuple_from_database_feed_result, tuple_from_feed_result,
        tuple_from_partition_key_ranges_result, tuple_from_result, tuple_from_result_with_attempts,
        FeedRangeFromPartitionKeyPayload,
    };
    use azure_core::Bytes;
    use azure_data_cosmos_driver::error::{CosmosError, CosmosStatus};
    use azure_data_cosmos_driver::models::{
        partition_key_range::PartitionKeyRange, CosmosResponse, CosmosResponseHeaders, ResponseBody,
    };
    use pyo3::prelude::*;
    use pyo3::types::PyDict;

    use super::super::diagnostics::{BINDING_ATTEMPT_COUNT, BINDING_RETRY_COUNT};
    use std::sync::atomic::Ordering;

    async fn create_read_and_conflict() -> (CosmosResponse, CosmosResponse, CosmosError) {
        use azure_data_cosmos_driver::{
            in_memory_emulator::{InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion},
            models::{
                AccountReference, CosmosOperation, ItemReference, PartitionKey,
                PartitionKeyDefinition,
            },
            options::{
                BinaryEncodingOptions, ContentResponseOnWrite, DriverOptions,
                OperationOptionsBuilder,
            },
        };
        use std::sync::Arc;

        let url = azure_core::http::Url::parse("https://telemetry.emulator.local").unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap(),
        ));
        emulator.store().create_database("sales");
        emulator.store().create_container(
            "sales",
            "orders",
            PartitionKeyDefinition::from("/customerId"),
        );
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5"))
                    .with_operation_options(
                        OperationOptionsBuilder::new()
                            .with_binary_encoding(BinaryEncodingOptions::new().with_enabled(false))
                            .with_content_response_on_write(ContentResponseOnWrite::Enabled)
                            .build(),
                    )
                    .build(),
            )
            .await
            .unwrap();
        let container = driver
            .resolve_container("sales", "orders", Default::default())
            .await
            .unwrap();
        let create = || {
            CosmosOperation::create_item(ItemReference::from_name(
                &container,
                PartitionKey::from("customer-17"),
                "order-17",
            ))
            .with_body(br#"{"id":"order-17","customerId":"customer-17"}"#.to_vec())
        };
        let response = driver
            .execute_singleton_operation(create(), Default::default())
            .await
            .unwrap();
        let read = driver
            .execute_singleton_operation(
                CosmosOperation::read_item(ItemReference::from_name(
                    &container,
                    PartitionKey::from("customer-17"),
                    "order-17",
                )),
                Default::default(),
            )
            .await
            .unwrap();
        let error = driver
            .execute_singleton_operation(create(), Default::default())
            .await
            .unwrap_err();
        assert_eq!(u16::from(error.status().status_code()), 409);
        assert!(error.response().is_some());
        (response, read, error)
    }

    fn tuple_with_rust_preparation_released<'py>(
        py: Python<'py>,
        response: CosmosResponse,
    ) -> PyResult<Bound<'py, pyo3::types::PyTuple>> {
        let (status, sub_status, diagnostics, headers, body) = py.allow_threads(move || {
            let (status, sub_status) = super::status_code_and_sub_status(response.status());
            let diagnostics = super::record_diagnostics(response.diagnostics());
            let headers = response.headers().to_raw_headers();
            (status, sub_status, diagnostics, headers, response.into_body())
        });
        let python_headers = PyDict::new_bound(py);
        for (name, value) in headers.iter() {
            python_headers.set_item(name.as_str(), value.as_str())?;
        }
        match body {
            ResponseBody::Bytes(bytes) => super::backend_response_tuple(
                py, status, sub_status, python_headers, bytes.as_ref(), Some(&diagnostics),
            ),
            ResponseBody::NoPayload => super::backend_response_tuple(
                py, status, sub_status, python_headers, b"", Some(&diagnostics),
            ),
            ResponseBody::Items(items) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
                "unexpected feed response body for point operation: got {} item(s)",
                items.len()
            ))),
        }
    }

    #[tokio::test]
    async fn released_preparation_preserves_read_response_and_counters() {
        pyo3::prepare_freethreaded_python();
        let (_, read, _) = create_read_and_conflict().await;
        Python::with_gil(|py| {
            assert_eq!(u16::from(read.status().status_code()), 200);
            let before = BINDING_ATTEMPT_COUNT.load(Ordering::Relaxed);
            let current = super::backend_response_tuple_from_success(py, read.clone()).unwrap();
            let proposed = tuple_with_rust_preparation_released(py, read.clone()).unwrap();
            assert!(current.eq(&proposed).unwrap());
            // Other native tests can update the process-wide counter concurrently.
            assert!(BINDING_ATTEMPT_COUNT.load(Ordering::Relaxed)
                >= before + 2 * read.diagnostics().request_count() as u64);
        });
    }

    #[test]
    #[ignore = "offline microbenchmark; run explicitly with --release --ignored --nocapture"]
    fn measure_response_preparation_gil() {
        use std::hint::black_box;
        use std::time::Instant;

        assert!(!cfg!(debug_assertions), "Use --release for this benchmark");
        pyo3::prepare_freethreaded_python();
        let runtime = tokio::runtime::Runtime::new().unwrap();
        let (_, read, _) = runtime.block_on(create_read_and_conflict());
        let iterations = 10_000;
        let samples = 7;
        let mut current_ns = Vec::new();
        let mut released_ns = Vec::new();
        let mut formatting_ns = Vec::new();
        let mut diagnostics_ns = Vec::new();
        let mut headers_ns = Vec::new();
        Python::with_gil(|py| {
            let current = super::backend_response_tuple_from_success(py, read.clone()).unwrap();
            let proposed = tuple_with_rust_preparation_released(py, read.clone()).unwrap();
            assert!(current.eq(&proposed).unwrap());
            for _ in 0..1_000 {
                drop(super::backend_response_tuple_from_success(py, read.clone()).unwrap());
                drop(tuple_with_rust_preparation_released(py, read.clone()).unwrap());
            }
            let diag = read.diagnostics();
            for sample in 0..samples {
                for released in if sample % 2 == 0 { [false, true] } else { [true, false] } {
                    let start = Instant::now();
                    for _ in 0..iterations {
                        let response = black_box(read.clone());
                        let tuple = if released {
                            tuple_with_rust_preparation_released(py, response)
                        } else {
                            super::backend_response_tuple_from_success(py, response)
                        }.unwrap();
                        drop(black_box(tuple));
                    }
                    let ns = start.elapsed().as_nanos() as f64 / iterations as f64;
                    if released { released_ns.push(ns); } else { current_ns.push(ns); }
                }
                let start = Instant::now();
                for _ in 0..iterations {
                    drop(black_box(black_box(&diag).to_string()));
                }
                formatting_ns.push(start.elapsed().as_nanos() as f64 / iterations as f64);
                let start = Instant::now();
                for _ in 0..iterations {
                    drop(black_box(super::record_diagnostics(black_box(diag.clone()))));
                }
                diagnostics_ns.push(start.elapsed().as_nanos() as f64 / iterations as f64);
                let start = Instant::now();
                for _ in 0..iterations {
                    drop(black_box(black_box(read.headers()).to_raw_headers()));
                }
                headers_ns.push(start.elapsed().as_nanos() as f64 / iterations as f64);
            }
            println!("RESPONSE_PREPARATION_BENCHMARK={}", serde_json::json!({
                "scope": "Local no-network release benchmark; completed in-memory-driver read response; no GIL contender",
                "iterations_per_sample": iterations, "samples": samples,
                "body_bytes": match read.body() { ResponseBody::Bytes(b) => b.len(), _ => 0 },
                "header_count": read.headers().to_raw_headers().iter().count(),
                "request_count": diag.request_count(),
                "response_tuple_parity": true,
                "current_conversion_ns": current_ns,
                "released_preparation_conversion_ns": released_ns,
                "diag_to_string_ns": formatting_ns,
                "record_diagnostics_ns": diagnostics_ns,
                "rust_raw_headers_ns": headers_ns
            }));
        });
    }

    #[tokio::test]
    async fn attempt_envelope_preserves_success_and_conflict_driver_records() {
        pyo3::prepare_freethreaded_python();
        let (success, _, conflict) = create_read_and_conflict().await;
        for result in [Ok(success), Err(conflict)] {
            let driver_response = match &result {
                Ok(response) => response,
                Err(error) => error.response().unwrap(),
            };
            let expected_status = u16::from(driver_response.status().status_code());
            let diagnostics = driver_response.diagnostics();
            assert!(diagnostics.request_count() > 0);
            assert_eq!(
                u16::from(
                    diagnostics
                        .requests()
                        .last()
                        .unwrap()
                        .status()
                        .status_code()
                ),
                expected_status
            );
            Python::with_gil(|py| {
                let ordinary = tuple_from_result(py, result.clone()).unwrap();
                let envelope = tuple_from_result_with_attempts(py, result).unwrap();
                assert_eq!(envelope.len(), 2);
                let response = envelope.get_item(0).unwrap();
                let response = response.downcast::<pyo3::types::PyTuple>().unwrap();
                assert!(response.eq(&ordinary).unwrap());
                assert_eq!(response.len(), 5);
                assert_eq!(
                    response.get_item(0).unwrap().extract::<u16>().unwrap(),
                    expected_status
                );
                assert!(!response
                    .get_item(4)
                    .unwrap()
                    .extract::<String>()
                    .unwrap()
                    .is_empty());
                let body = response.get_item(3).unwrap().extract::<Vec<u8>>().unwrap();
                let body: serde_json::Value = serde_json::from_slice(&body).unwrap();
                if expected_status == 201 {
                    assert_eq!(body["id"], "order-17");
                }
                let payload = envelope.get_item(1).unwrap();
                assert_eq!(
                    payload
                        .get_item("schema_version")
                        .unwrap()
                        .extract::<u32>()
                        .unwrap(),
                    1
                );
                assert_eq!(
                    payload
                        .get_item("request_count")
                        .unwrap()
                        .extract::<usize>()
                        .unwrap(),
                    diagnostics.request_count()
                );
                assert_eq!(
                    payload
                        .get_item("retained_request_count")
                        .unwrap()
                        .extract::<usize>()
                        .unwrap(),
                    diagnostics.retained_request_count()
                );
                assert!(payload.get_item("error").unwrap().is_none());
                let rows = payload.get_item("attempts").unwrap();
                assert_eq!(rows.len().unwrap(), diagnostics.requests().len());
                for (index, request) in diagnostics.requests().iter().enumerate() {
                    let row = rows.get_item(index).unwrap();
                    assert_eq!(
                        row.get_item("driver_status_code")
                            .unwrap()
                            .extract::<u16>()
                            .unwrap(),
                        u16::from(request.status().status_code())
                    );
                    assert_eq!(
                        row.get_item("execution_context")
                            .unwrap()
                            .extract::<String>()
                            .unwrap(),
                        request.execution_context().as_str()
                    );
                    let start = row.get_item("start_ns").unwrap().extract::<u64>().unwrap();
                    let end = row.get_item("end_ns").unwrap().extract::<u64>().unwrap();
                    assert_eq!(
                        u128::from(end - start),
                        request
                            .completed_at()
                            .unwrap()
                            .duration_since(request.started_at())
                            .as_nanos()
                    );
                }
            });
        }
    }

    #[tokio::test]
    async fn attempt_tracing_preserves_responseless_errors_and_available_diagnostics() {
        pyo3::prepare_freethreaded_python();
        let (_, _, conflict) = create_read_and_conflict().await;
        let diagnostics = conflict.diagnostics().unwrap();
        assert!(diagnostics.request_count() > 0);
        Python::with_gil(|py| {
            for status in [
                azure_core::http::StatusCode::BadRequest,
                azure_core::http::StatusCode::PreconditionFailed,
                azure_core::http::StatusCode::RequestTimeout,
            ] {
                let error = CosmosError::builder()
                    .with_status(CosmosStatus::new(status))
                    .with_message("synthetic error with retained diagnostics")
                    .with_diagnostics(diagnostics.clone())
                    .build();
                assert!(error.response().is_none());
                let ordinary = tuple_from_result(py, Err(error.clone()));
                let result = tuple_from_result_with_attempts(py, Err(error));
                let payload = if status == azure_core::http::StatusCode::RequestTimeout {
                    let error = result.unwrap_err();
                    let ordinary = ordinary.unwrap_err();
                    assert!(error.is_instance_of::<_DriverTransportError>(py));
                    assert_eq!(error.to_string(), ordinary.to_string());
                    assert!(error
                        .value_bound(py)
                        .getattr("args")
                        .unwrap()
                        .eq(ordinary.value_bound(py).getattr("args").unwrap())
                        .unwrap());
                    assert!(!ordinary
                        .value_bound(py)
                        .hasattr("_cosmos_attempt_payload")
                        .unwrap());
                    error
                        .value_bound(py)
                        .getattr("_cosmos_attempt_payload")
                        .unwrap()
                } else {
                    let envelope = result.unwrap();
                    assert!(envelope.get_item(0).unwrap().eq(ordinary.unwrap()).unwrap());
                    assert_eq!(
                        envelope
                            .get_item(0)
                            .unwrap()
                            .get_item(0)
                            .unwrap()
                            .extract::<u16>()
                            .unwrap(),
                        u16::from(status)
                    );
                    envelope.get_item(1).unwrap()
                };
                assert_eq!(
                    payload
                        .get_item("request_count")
                        .unwrap()
                        .extract::<usize>()
                        .unwrap(),
                    diagnostics.request_count()
                );
                assert_eq!(
                    payload
                        .get_item("retained_request_count")
                        .unwrap()
                        .extract::<usize>()
                        .unwrap(),
                    diagnostics.retained_request_count()
                );
                let attempts = payload.get_item("attempts").unwrap();
                assert_eq!(attempts.len().unwrap(), diagnostics.requests().len());
                for (index, request) in diagnostics.requests().iter().enumerate() {
                    let row = attempts.get_item(index).unwrap();
                    assert_eq!(
                        row.get_item("driver_status_code")
                            .unwrap()
                            .extract::<u16>()
                            .unwrap(),
                        u16::from(request.status().status_code())
                    );
                    let start = row.get_item("start_ns").unwrap().extract::<u64>().unwrap();
                    let end = row.get_item("end_ns").unwrap().extract::<u64>().unwrap();
                    assert_eq!(
                        u128::from(end - start),
                        request
                            .completed_at()
                            .unwrap()
                            .duration_since(request.started_at())
                            .as_nanos()
                    );
                }
            }
        });
    }

    #[test]
    fn attempt_exception_without_diagnostics_keeps_original_error() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let error = CosmosError::builder()
                .with_status(CosmosStatus::new(
                    azure_core::http::StatusCode::RequestTimeout,
                ))
                .with_message("driver failure without diagnostics")
                .build();
            let ordinary = tuple_from_result(py, Err(error.clone())).unwrap_err();
            let error = tuple_from_result_with_attempts(py, Err(error)).unwrap_err();
            assert!(error.is_instance_of::<_DriverTransportError>(py));
            assert_eq!(error.to_string(), ordinary.to_string());
            assert!(!error
                .value_bound(py)
                .hasattr("_cosmos_attempt_payload")
                .unwrap());
        });
    }

    #[test]
    fn attempt_attachment_keeps_exception_identity_args_and_message() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let error = _DriverTransportError::new_err("driver failure");
            let original = error.value_bound(py).clone();
            let args = original.getattr("args").unwrap();
            let message = error.to_string();
            let payload = attempt_payload_or_error(
                py,
                Err(pyo3::exceptions::PyValueError::new_err("PRIVATE")),
            );
            attach_attempt_payload(py, &error, payload);
            assert!(error.value_bound(py).is(&original));
            assert!(error.value_bound(py).getattr("args").unwrap().is(&args));
            assert_eq!(error.to_string(), message);
            assert_eq!(
                error
                    .value_bound(py)
                    .getattr("_cosmos_attempt_payload")
                    .unwrap()
                    .extract::<String>()
                    .unwrap(),
                "attempt payload conversion failed"
            );
        });
    }

    #[test]
    fn attempt_attachment_failure_reports_without_replacing_error() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = pyo3::types::PyModule::from_code_bound(
                py,
                r#"
class RejectDiagnostics(RuntimeError):
    def __setattr__(self, name, value):
        raise RuntimeError("PRIVATE")

warnings = []
unraisable = []

def record_warning(message, *args, **kwargs):
    warnings.append(str(message))

def record_unraisable(args):
    unraisable.append(str(args.exc_value))
"#,
                "test_attempt_attachment.py",
                "test_attempt_attachment",
            )
            .unwrap();
            let warnings = py.import_bound("warnings").unwrap();
            let sys = py.import_bound("sys").unwrap();
            for action in ["always", "error"] {
                let error = PyErr::from_value_bound(
                    module
                        .getattr("RejectDiagnostics")
                        .unwrap()
                        .call1(("driver failure",))
                        .unwrap(),
                );
                let original = error.value_bound(py).clone();
                let context = warnings.call_method0("catch_warnings").unwrap();
                context.call_method0("__enter__").unwrap();
                warnings.call_method1("simplefilter", (action,)).unwrap();
                warnings
                    .setattr("showwarning", module.getattr("record_warning").unwrap())
                    .unwrap();
                let original_hook = sys.getattr("unraisablehook").unwrap();
                sys.setattr(
                    "unraisablehook",
                    module.getattr("record_unraisable").unwrap(),
                )
                .unwrap();

                attach_attempt_payload(py, &error, "PRIVATE".into_py(py));

                sys.setattr("unraisablehook", original_hook).unwrap();
                context
                    .call_method1("__exit__", (py.None(), py.None(), py.None()))
                    .unwrap();
                assert!(error.value_bound(py).is(&original));
                assert_eq!(
                    original
                        .getattr("args")
                        .unwrap()
                        .extract::<(String,)>()
                        .unwrap(),
                    ("driver failure".to_string(),)
                );
                assert!(!original.hasattr("_cosmos_attempt_payload").unwrap());
            }
            for name in ["warnings", "unraisable"] {
                let messages = module
                    .getattr(name)
                    .unwrap()
                    .extract::<Vec<String>>()
                    .unwrap();
                assert_eq!(messages.len(), 1);
                assert!(messages[0].contains("could not attach diagnostics"));
                assert!(!messages[0].contains("PRIVATE"));
            }
        });
    }

    #[test]
    fn attempt_conversion_error_is_reportable_data_not_a_database_error() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let payload = attempt_payload_or_error(
                py,
                Err(pyo3::exceptions::PyValueError::new_err(
                    "private conversion details",
                )),
            );
            assert_eq!(
                payload.extract::<String>(py).unwrap(),
                "attempt payload conversion failed"
            );
        });
    }

    #[test]
    fn attempt_envelope_preserves_synthetic_error_without_attempt_diagnostics() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let error = CosmosError::builder()
                .with_status(CosmosStatus::new(azure_core::http::StatusCode::BadRequest))
                .with_message("invalid request")
                .build();
            let envelope = tuple_from_result_with_attempts(py, Err(error)).unwrap();
            assert_eq!(envelope.len(), 2);
            assert!(envelope.get_item(1).unwrap().is_none());
            assert_eq!(
                envelope
                    .get_item(0)
                    .unwrap()
                    .get_item(0)
                    .unwrap()
                    .extract::<u16>()
                    .unwrap(),
                400
            );
        });
    }

    #[test]
    fn database_feed_items_use_databases_envelope() {
        let body = named_feed_response_body_to_vec(
            ResponseBody::Items(vec![
                Bytes::from_static(br#"{"id":"db-1"}"#),
                Bytes::from_static(br#"{"id":"db-2"}"#),
            ]),
            b"Databases",
        )
        .expect("database feed items should serialize");

        assert_eq!(body, br#"{"Databases":[{"id":"db-1"},{"id":"db-2"}]}"#);
    }

    #[test]
    fn database_feed_service_errors_preserve_wire_tuple_fields() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            for status_code in [
                azure_core::http::StatusCode::Forbidden,
                azure_core::http::StatusCode::NotFound,
                azure_core::http::StatusCode::TooManyRequests,
            ] {
                let status = CosmosStatus::new(status_code).with_sub_status(1002);
                let mut headers = CosmosResponseHeaders::default();
                headers.continuation = Some("error-continuation".to_string());
                headers.retry_after_ms = Some(17);
                let tuple = backend_response_tuple_from_feed_error_parts(
                    py,
                    status,
                    &headers,
                    ResponseBody::Bytes(Bytes::from_static(
                        br#"{"code":"SyntheticError","message":"database feed failed"}"#,
                    )),
                    "synthetic diagnostics",
                )
                .expect("service error should map to a Python backend tuple");

                assert_eq!(
                    tuple.get_item(0).unwrap().extract::<u16>().unwrap(),
                    u16::from(status_code)
                );
                assert_eq!(tuple.get_item(1).unwrap().extract::<u16>().unwrap(), 1002);
                let tuple_headers = tuple.get_item(2).unwrap();
                let tuple_headers = tuple_headers.downcast::<PyDict>().unwrap();
                assert_eq!(
                    tuple_headers
                        .get_item("x-ms-continuation")
                        .unwrap()
                        .unwrap()
                        .extract::<String>()
                        .unwrap(),
                    "error-continuation"
                );
                assert_eq!(
                    tuple_headers
                        .get_item("x-ms-retry-after-ms")
                        .unwrap()
                        .unwrap()
                        .extract::<String>()
                        .unwrap(),
                    "17"
                );
                assert_eq!(
                    tuple.get_item(3).unwrap().extract::<Vec<u8>>().unwrap(),
                    br#"{"code":"SyntheticError","message":"database feed failed"}"#
                );
                assert_eq!(
                    tuple.get_item(4).unwrap().extract::<String>().unwrap(),
                    "synthetic diagnostics"
                );
            }
        });
    }

    #[test]
    fn unsupported_query_feature_uses_typed_binding_error() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let error = CosmosError::builder()
                .with_status(CosmosStatus::CLIENT_UNSUPPORTED_QUERY_FEATURE)
                .with_message("unsupported query feature: ORDER BY")
                .build();

            let py_error = tuple_from_feed_result(py, Err(error)).unwrap_err();

            assert!(py_error.is_instance_of::<_UnsupportedQueryFeatureError>(py));
        });
    }

    // ---- read_feed_ranges body parsing ----------------------------------------

    #[test]
    fn read_feed_ranges_tuple_sets_minimal_headers() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let ranges = vec![PartitionKeyRange::new("0".to_string(), "", "FF")];
            let tuple = tuple_from_partition_key_ranges_result(py, Ok(Some(ranges)))
                .expect("successful read_feed_ranges should map to backend tuple");
            let headers_any = tuple.get_item(2).expect("headers slot must exist");
            let headers = headers_any
                .downcast::<PyDict>()
                .expect("headers slot must be a dict");
            assert_eq!(
                headers
                    .get_item("content-type")
                    .expect("dict lookup should succeed")
                    .expect("content-type should be present")
                    .extract::<String>()
                    .expect("content-type must be string"),
                "application/json"
            );
            assert_eq!(
                headers
                    .get_item("x-ms-item-count")
                    .expect("dict lookup should succeed")
                    .expect("x-ms-item-count should be present")
                    .extract::<String>()
                    .expect("x-ms-item-count must be string"),
                "0"
            );
        });
    }

    #[test]
    fn read_feed_ranges_tuple_rejects_missing_routing_map() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let err = tuple_from_partition_key_ranges_result(py, Ok(None))
                .expect_err("missing routing map must raise a transport error");
            assert!(
                err.to_string()
                    .contains("driver resolve_all_partition_key_ranges returned no routing map"),
                "unexpected error: {err}"
            );
        });
    }

    #[test]
    fn feed_range_payload_serializes_expected_shape() {
        let payload = FeedRangeFromPartitionKeyPayload {
            min: "3C".to_string(),
            max: "3CFF".to_string(),
            is_max_inclusive: false,
        };
        let body = feed_range_to_response_body(&payload).expect("serialization should succeed");
        let json: serde_json::Value =
            serde_json::from_slice(&body).expect("body must be valid JSON");
        assert_eq!(json["Range"]["min"], "3C");
        assert_eq!(json["Range"]["max"], "3CFF");
        assert_eq!(json["Range"]["isMinInclusive"], true);
        assert_eq!(json["Range"]["isMaxInclusive"], false);
    }

    #[test]
    fn response_headers_dict_maps_present_fields_and_skips_missing() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let mut headers = CosmosResponseHeaders::new();
            headers.continuation = Some("ct-1".to_string());
            headers.item_count = Some(7);
            headers.server_duration_ms = Some(12.5);
            headers.lsn = Some(42);
            headers.retry_after_ms = Some(250);
            headers.gateway_version = Some("gateway/1".to_string());
            headers.service_version = Some("2026-07-01".to_string());
            headers.has_tentative_writes = Some(true);
            headers.partition_key_range_id = Some("3".to_string());
            headers.internal_partition_id = Some("p-1".to_string());
            headers.collection_index_transformation_progress = Some(88);
            headers.collection_lazy_indexing_progress = Some(91);

            let out = response_headers_dict(py, &headers).expect("header copy should succeed");

            // Expected strings from the synthetic driver-header fixture.
            // No service response or legacy backend is compared here.
            for (name, expected) in [
                ("x-ms-continuation", "ct-1"),
                ("x-ms-item-count", "7"),
                ("x-ms-request-duration-ms", "12.5"),
                ("lsn", "42"),
                ("x-ms-retry-after-ms", "250"),
                ("x-ms-gatewayversion", "gateway/1"),
                ("x-ms-serviceversion", "2026-07-01"),
                ("x-ms-cosmos-allow-tentative-writes", "True"),
                ("x-ms-documentdb-partitionkeyrangeid", "3"),
                ("x-ms-cosmos-internal-partition-id", "p-1"),
                (
                    "x-ms-documentdb-collection-index-transformation-progress",
                    "88",
                ),
                ("x-ms-documentdb-collection-lazy-indexing-progress", "91"),
            ] {
                assert_eq!(
                    out.get_item(name)
                        .expect("dict lookup should succeed")
                        .unwrap_or_else(|| panic!("{name} should be present"))
                        .extract::<String>()
                        .unwrap_or_else(|_| panic!("{name} must be a string")),
                    expected
                );
            }

            assert!(
                out.get_item("x-ms-activity-id")
                    .expect("dict lookup should succeed")
                    .is_none(),
                "missing driver fields must not be emitted"
            );
        });
    }

    #[test]
    fn response_headers_dict_reencodes_index_metrics_to_base64() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let mut headers = CosmosResponseHeaders::new();
            // The driver stores this decoded; Python base64-decodes whatever we
            // hand it, so it has to leave here in the encoded wire form.
            headers.index_metrics = Some(r#"{"UtilizedIndexes":[]}"#.to_string());

            let out = response_headers_dict(py, &headers).expect("header copy should succeed");

            let emitted = out
                .get_item("x-ms-cosmos-index-utilization")
                .expect("dict lookup should succeed")
                .expect("index utilization should be present")
                .extract::<String>()
                .expect("index utilization must be a string");

            let decoded =
                azure_core::base64::decode(&emitted).expect("emitted value must be valid base64");
            assert_eq!(
                String::from_utf8(decoded).expect("decoded value must be utf-8"),
                r#"{"UtilizedIndexes":[]}"#
            );
        });
    }

    #[test]
    fn point_response_body_rejects_feed_shape() {
        let body = ResponseBody::from_items(vec![Bytes::from_static(br#"{"id":"a"}"#)]);
        let err = response_body_to_vec(body).expect_err("feed shape must not be flattened");
        assert!(
            err.to_string().contains("unexpected feed response body"),
            "unexpected error: {err}"
        );
    }

    // record_diagnostics_for_responseless tests --------------------------

    #[test]
    fn responseless_error_without_diagnostics_does_not_increment_counters() {
        let before_attempts = BINDING_ATTEMPT_COUNT.load(Ordering::Relaxed);
        let before_retries = BINDING_RETRY_COUNT.load(Ordering::Relaxed);

        // A pure synthetic error with no diagnostics attached.
        let error = CosmosError::builder()
            .with_status(CosmosStatus::new(
                azure_core::http::StatusCode::RequestTimeout,
            ))
            .with_message("synthetic timeout")
            .build();

        record_diagnostics_for_responseless(&error);

        assert_eq!(
            BINDING_ATTEMPT_COUNT.load(Ordering::Relaxed),
            before_attempts,
            "no-diagnostics error must not increment attempt counter"
        );
        assert_eq!(
            BINDING_RETRY_COUNT.load(Ordering::Relaxed),
            before_retries,
            "no-diagnostics error must not increment retry counter"
        );
    }

    #[test]
    fn responseless_error_surfaces_transport_error_not_runtime_error() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let error = CosmosError::builder()
                .with_status(CosmosStatus::new(
                    azure_core::http::StatusCode::RequestTimeout,
                ))
                .with_message("end-to-end operation timeout exceeded (5s)")
                .build();

            let py_error = tuple_from_result(py, Err(error)).unwrap_err();

            assert!(
                py_error.is_instance_of::<_DriverTransportError>(py),
                "response-less CosmosError must raise _DriverTransportError"
            );
        });
    }

    #[test]
    fn local_validation_and_precondition_errors_retain_status_and_message() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            for status in [
                CosmosStatus::CLIENT_BAD_REQUEST,
                CosmosStatus::SERIALIZATION_REQUEST_BODY_INVALID,
                CosmosStatus::new(azure_core::http::StatusCode::PreconditionFailed),
            ] {
                let error = CosmosError::builder()
                    .with_status(status)
                    .with_message("local patch rejected")
                    .build();
                let tuple = tuple_from_result(py, Err(error)).unwrap();
                assert_eq!(
                    tuple.get_item(0).unwrap().extract::<u16>().unwrap(),
                    u16::from(status.status_code())
                );
                assert_eq!(
                    tuple.get_item(1).unwrap().extract::<u16>().unwrap(),
                    status.sub_status().map(|s| s.value()).unwrap_or(0)
                );
                let bytes = tuple.get_item(3).unwrap().extract::<Vec<u8>>().unwrap();
                let body: serde_json::Value = serde_json::from_slice(&bytes).unwrap();
                assert!(body["message"]
                    .as_str()
                    .unwrap()
                    .contains("local patch rejected"));
                let headers = tuple.get_item(2).unwrap();
                let headers = headers.downcast::<PyDict>().unwrap();
                assert!(!headers.contains("etag").unwrap());
                assert!(!headers.contains("x-ms-request-charge").unwrap());
                assert!(!headers.contains("x-ms-activity-id").unwrap());
            }
        });
    }

    #[test]
    fn responseless_feed_error_surfaces_transport_error_not_runtime_error() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let error = CosmosError::builder()
                .with_status(CosmosStatus::new(
                    azure_core::http::StatusCode::RequestTimeout,
                ))
                .with_message("end-to-end operation timeout exceeded (5s)")
                .build();

            let py_error = tuple_from_feed_result(py, Err(error)).unwrap_err();

            assert!(
                py_error.is_instance_of::<_DriverTransportError>(py),
                "response-less feed CosmosError must raise _DriverTransportError"
            );
        });
    }

    #[test]
    fn responseless_database_feed_error_surfaces_transport_error() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let error = CosmosError::builder()
                .with_status(CosmosStatus::new(
                    azure_core::http::StatusCode::RequestTimeout,
                ))
                .with_message("database feed transport failed")
                .build();

            let py_error = tuple_from_database_feed_result(py, Err(error)).unwrap_err();

            assert!(py_error.is_instance_of::<_DriverTransportError>(py));
            assert!(py_error
                .to_string()
                .contains("driver list_databases failed"));
        });
    }
}

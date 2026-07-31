// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use pyo3::exceptions::{PyAttributeError, PyRuntimeError, PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyTuple};

use serde::Serialize;

use azure_data_cosmos_driver::{
    error::{CosmosError, CosmosStatus},
    models::{CosmosResponse, ResponseBody},
};

use super::diagnostics::record_diagnostics;
use super::errors::{DriverTransportError, UnsupportedQueryFeatureError};
use super::feed_range::{FeedRangeFromPartitionKeyError, FeedRangeFromPartitionKeyPayload};

/// Turn the driver's `Result<CosmosResponse, CosmosError>` into the
/// `BackendResponse` tuple. A CosmosError carrying a wire response (404 / 409
/// / 412 / ...) becomes the same tuple shape as success so the Python parser raises
/// the right typed exception; only a response-less error (transport failure,
/// client-side validation) becomes a `DriverTransportError`, which the Python
/// backend maps to azure-core's `ServiceResponseError`.
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
            } else {
                // No wire response: combine any attached diagnostics into the
                // process-wide attempt counters so timeouts and transport
                // failures are counted alongside successful operations.
                record_diagnostics_for_responseless(&cosmos_error);
                // Report a typed transport error (Display preserves the
                // Cosmos status) the Python layer maps to
                // ServiceResponseError, rather than a bare RuntimeError.
                Err(DriverTransportError::new_err(format!(
                    "driver execute_singleton_operation failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// Turn the driver's query reply into the tuple the Python parser reads. Handles
/// the three outcomes: a page of rows becomes a success reply; `None` (no rows)
/// becomes an empty `{"Documents":[]}` page; an error carrying a real service
/// response (e.g. a 400) becomes the same tuple shape so the Python parser raises
/// the right Cosmos error, while a pure transport failure becomes a Rust error.
/// Feed variant of `tuple_from_result`, which handles single-document replies.
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
                return Err(UnsupportedQueryFeatureError::new_err(
                    cosmos_error.to_string(),
                ));
            }
            if let Some(raw_http_error) =
                backend_response_tuple_from_cosmos_error_feed(py, &cosmos_error)?
            {
                Ok(raw_http_error)
            } else {
                record_diagnostics_for_responseless(&cosmos_error);
                Err(DriverTransportError::new_err(format!(
                    "driver execute_operation failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// Feed-range variant: returns a JSON body in the shape
/// `{"PartitionKeyRanges":[{"id","minInclusive","maxExclusive"}, ...]}`.
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
            // Match the wire contract observed on core-python for pkranges:
            // this feed response reports x-ms-item-count as "0".
            response_headers.set_item("x-ms-item-count", "0")?;
            let body = partition_key_ranges_to_response_body(&ranges)?;
            backend_response_tuple(py, 200, 0, response_headers, &body, None)
        }
        Ok(None) => Err(DriverTransportError::new_err(
            "driver resolve_all_partition_key_ranges returned no routing map",
        )),
        Err(cosmos_error) => {
            if let Some(raw_http_error) =
                backend_response_tuple_from_cosmos_error_feed(py, &cosmos_error)?
            {
                Ok(raw_http_error)
            } else {
                record_diagnostics_for_responseless(&cosmos_error);
                Err(DriverTransportError::new_err(format!(
                    "driver resolve_all_partition_key_ranges failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// feed_range_from_partition_key variant: returns a JSON body in the shape
/// `{"Range":{"min","max","isMinInclusive","isMaxInclusive"}}`.
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
                Err(DriverTransportError::new_err(format!(
                    "driver feed_range_from_partition_key failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// Offer-feed variant of `tuple_from_feed_result`: an offer/throughput query page
/// becomes a success reply whose body is the `{"Offers":[...]}` envelope the Python
/// offer parser reads; `None` (no offers) becomes an empty `{"Offers":[]}` page; an
/// error carrying a real service response (e.g. a 400) becomes the same tuple shape
/// so the parser raises the right Cosmos error, while a pure transport failure
/// becomes a Rust error.
pub(super) fn tuple_from_offer_feed_result<'py>(
    py: Python<'py>,
    response_result: Result<Option<CosmosResponse>, CosmosError>,
) -> PyResult<Bound<'py, PyTuple>> {
    match response_result {
        Ok(Some(response)) => backend_response_tuple_from_offer_feed_success(py, response),
        Ok(None) => {
            let response_headers = PyDict::new_bound(py);
            backend_response_tuple(py, 200, 0, response_headers, br#"{"Offers":[]}"#, None)
        }
        Err(cosmos_error) => {
            if let Some(raw_http_error) =
                backend_response_tuple_from_cosmos_error_feed(py, &cosmos_error)?
            {
                Ok(raw_http_error)
            } else {
                record_diagnostics_for_responseless(&cosmos_error);
                Err(DriverTransportError::new_err(format!(
                    "driver execute_operation failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// Shape the boolean result (or a validation error) into the `BackendResponse`
/// 5-tuple the python parser reads, with a `{"IsSubset": <bool>}` body.
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

/// Assemble the fixed 5-part reply the Python backend reads. Every success and
/// wire-error path ends here, so the tuple shape stays identical no matter which
/// operation or backend produced it.
fn backend_response_tuple<'py>(
    py: Python<'py>,
    status_code: i64,
    sub_status: i64,
    response_headers: Bound<'py, PyDict>,
    body: &[u8],
    diagnostics: Option<&str>,
) -> PyResult<Bound<'py, PyTuple>> {
    // Python backend tuple contract:
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
/// sub-status, combine this operation's wire attempts into the diagnostics counters,
/// copy the response headers under their wire names, and convert the body.
fn backend_response_tuple_from_success<'py>(
    py: Python<'py>,
    response: azure_data_cosmos_driver::models::CosmosResponse,
) -> PyResult<Bound<'py, PyTuple>> {
    let status = response.status();
    let status_code = u16::from(status.status_code()) as i64;
    // SubStatusCode wraps a u16; use ``.value()`` to read it.
    let sub_status = status.sub_status().map(|s| s.value() as i64).unwrap_or(0);
    // Combine this operation's per-attempt wire diagnostics into the process-wide
    // attempt/retry counters before stringifying them (see BINDING_ATTEMPT_COUNT).
    // `diagnostics()` is a low-cost Arc clone; the read touches only in-memory records.
    let diagnostics = record_diagnostics(response.diagnostics());
    // dict keyed by the actual `x-ms-...` wire-header names. This is what
    // the Python parser (`_helpers/_response_parse.py`) reads to populate
    // `client_connection.last_response_headers`, so customer code that
    // does e.g. `last_response_headers["etag"]` keeps working on the
    // Rust path.
    let driver_headers = response.headers();
    let response_headers = PyDict::new_bound(py);
    write_response_headers(&response_headers, driver_headers)?;

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

/// Query-page version of `backend_response_tuple_from_success`: same steps, but the
/// body is wrapped in the `{"Documents":[...]}` envelope the query parser reads.
fn backend_response_tuple_from_feed_success<'py>(
    py: Python<'py>,
    response: azure_data_cosmos_driver::models::CosmosResponse,
) -> PyResult<Bound<'py, PyTuple>> {
    let status = response.status();
    let status_code = u16::from(status.status_code()) as i64;
    let sub_status = status.sub_status().map(|s| s.value() as i64).unwrap_or(0);
    let diagnostics = record_diagnostics(response.diagnostics());
    let response_headers = PyDict::new_bound(py);
    write_response_headers(&response_headers, response.headers())?;
    let body_vec = query_response_body_to_vec(response.into_body())?;
    backend_response_tuple(
        py,
        status_code,
        sub_status,
        response_headers,
        &body_vec,
        Some(diagnostics.as_str()),
    )
}

/// Map the driver's typed `ResponseBody` to a flat `Vec<u8>` suitable for the
/// Python `BackendResponse.body` bytes field.
///
/// `ResponseBody` is an enum (`NoPayload | Bytes | Items`); `create_item`
/// always produces a single payload (or no payload when the caller passed
/// `no_response=True`), so we never expect the `Items` feed-shape here.
/// We concatenate it as a defensive fallback rather than panic — if it ever
/// fires the test harness will show a body mismatch that's easier to
/// diagnose than an unwrap panic from inside the binding.
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

/// Wrap the driver's query results into the `{"Documents":[ ... ]}` JSON envelope
/// the Python query parser expects — the same shape the Cosmos REST service
/// returns for a query. The driver returns the rows as a list of item bytes
/// (or raw bytes, or nothing); this assembles them into that envelope so the parser
/// can read a Rust-served page without knowing it came from Rust. No rows becomes
/// `{"Documents":[]}`.
fn query_response_body_to_vec(body: ResponseBody) -> PyResult<Vec<u8>> {
    match body {
        ResponseBody::NoPayload => Ok(br#"{"Documents":[]}"#.to_vec()),
        ResponseBody::Bytes(b) => Ok(b.to_vec()),
        ResponseBody::Items(items) => {
            let mut out = Vec::with_capacity(16 + items.iter().map(|i| i.len()).sum::<usize>());
            out.extend_from_slice(br#"{"Documents":["#);
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

/// Offer version of `backend_response_tuple_from_feed_success`: identical status /
/// diagnostics / header handling, but the body rows are wrapped in the
/// `{"Offers":[...]}` envelope instead of `{"Documents":[...]}`.
fn backend_response_tuple_from_offer_feed_success<'py>(
    py: Python<'py>,
    response: azure_data_cosmos_driver::models::CosmosResponse,
) -> PyResult<Bound<'py, PyTuple>> {
    let status = response.status();
    let status_code = u16::from(status.status_code()) as i64;
    let sub_status = status.sub_status().map(|s| s.value() as i64).unwrap_or(0);
    let diagnostics = record_diagnostics(response.diagnostics());
    let response_headers = PyDict::new_bound(py);
    write_response_headers(&response_headers, response.headers())?;
    let body_vec = offer_response_body_to_vec(response.into_body())?;
    backend_response_tuple(
        py,
        status_code,
        sub_status,
        response_headers,
        &body_vec,
        Some(diagnostics.as_str()),
    )
}

/// Response side: wrap the driver's offer rows in the `{"Offers":[...]}` envelope the
/// Python parser expects (same key the REST service returns). The query text went OUT
/// in `run_read_offer_future`; here we shape the rows on the way back. No rows becomes
/// `{"Offers":[]}`; a raw pre-built body (`Bytes`) passes through unchanged.
fn offer_response_body_to_vec(body: ResponseBody) -> PyResult<Vec<u8>> {
    match body {
        ResponseBody::NoPayload => Ok(br#"{"Offers":[]}"#.to_vec()),
        ResponseBody::Bytes(b) => Ok(b.to_vec()),
        ResponseBody::Items(items) => {
            // Envelope overhead: `{"Offers":[` (11 bytes) + `]}` (2 bytes) = 13.
            let mut out = Vec::with_capacity(13 + items.iter().map(|i| i.len()).sum::<usize>());
            out.extend_from_slice(br#"{"Offers":["#);
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
/// to `DriverTransportError`.  Do not call for wire-response errors — those are
/// already counted by `backend_response_tuple_from_cosmos_error` /
/// `backend_response_tuple_from_cosmos_error_feed`.
fn record_diagnostics_for_responseless(error: &CosmosError) {
    if let Some(diag) = error.diagnostics() {
        record_diagnostics(diag);
    }
}

/// Entry point that computes is_feed_range_subset (sync). This is a pure local
/// computation, so unlike the network operations it needs no driver handle and
/// does not touch the Tokio runtime.
/// failures, client validation, timeouts before any HTTP round-trip).
/// The caller falls back to a generic `PyRuntimeError` in that case.
fn backend_response_tuple_from_cosmos_error<'py>(
    py: Python<'py>,
    error: &CosmosError,
) -> PyResult<Option<Bound<'py, PyTuple>>> {
    let response = match error.response() {
        Some(r) => r,
        None => return Ok(None),
    };

    let status = response.status();
    let status_code = u16::from(status.status_code()) as i64;
    let sub_status = status.sub_status().map(|s| s.value() as i64).unwrap_or(0);
    // Wire-error responses still made real attempts -- combine them in too so the
    // counters cover the full round-trip count, not just successes.
    let diagnostics = record_diagnostics(response.diagnostics());

    let response_headers = PyDict::new_bound(py);
    write_response_headers(&response_headers, response.headers())?;

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

    let status = response.status();
    let status_code = u16::from(status.status_code()) as i64;
    let sub_status = status.sub_status().map(|s| s.value() as i64).unwrap_or(0);
    let diagnostics = record_diagnostics(response.diagnostics());

    let response_headers = PyDict::new_bound(py);
    write_response_headers(&response_headers, response.headers())?;
    let body_vec = query_response_body_to_vec(response.body().clone())?;
    Ok(Some(backend_response_tuple(
        py,
        status_code,
        sub_status,
        response_headers,
        &body_vec,
        Some(diagnostics.as_str()),
    )?))
}

/// Copy every populated field on the driver's `CosmosResponseHeaders` into a
/// Python dict keyed by the wire-header name the Python parser expects.
///
/// Only fields that are `Some(_)` are written, so callers that read a missing
/// header get `KeyError` rather than `None` (matches what the legacy
/// core-Python path emits today).
fn write_response_headers(
    out: &Bound<'_, PyDict>,
    h: &azure_data_cosmos_driver::models::CosmosResponseHeaders,
) -> PyResult<()> {
    if let Some(v) = h.activity_id.as_ref() {
        out.set_item("x-ms-activity-id", v.as_str())?;
    }
    if let Some(v) = h.request_charge {
        // RequestCharge wraps an f64; render with the same formatting as the
        // legacy path (no trailing zero stripping; let Display do its job).
        out.set_item("x-ms-request-charge", format!("{}", f64::from(v)))?;
    }
    if let Some(v) = h.session_token.as_ref() {
        out.set_item("x-ms-session-token", v.as_str())?;
    }
    if let Some(v) = h.etag.as_ref() {
        out.set_item("etag", v.to_string())?;
    }
    if let Some(v) = h.continuation.as_ref() {
        out.set_item("x-ms-continuation", v.as_str())?;
    }
    if let Some(v) = h.item_count {
        out.set_item("x-ms-item-count", v)?;
    }
    if let Some(v) = h.substatus {
        // SubStatusCode wraps a u16; ``.value()`` reads it.
        out.set_item("x-ms-substatus", v.value() as u32)?;
    }
    if let Some(v) = h.index_metrics.as_ref() {
        out.set_item("x-ms-cosmos-index-utilization", v.as_str())?;
    }
    if let Some(v) = h.query_metrics.as_ref() {
        out.set_item("x-ms-documentdb-query-metrics", v.as_str())?;
    }
    if let Some(v) = h.server_duration_ms {
        out.set_item("x-ms-request-duration-ms", v)?;
    }
    if let Some(v) = h.lsn {
        out.set_item("lsn", v)?;
    }
    if let Some(v) = h.item_lsn {
        out.set_item("x-ms-item-lsn", v)?;
    }
    if let Some(v) = h.local_lsn {
        out.set_item("x-ms-cosmos-llsn", v)?;
    }
    if let Some(v) = h.item_local_lsn {
        out.set_item("x-ms-cosmos-item-llsn", v)?;
    }
    if let Some(v) = h.global_committed_lsn {
        out.set_item("x-ms-global-committed-lsn", v)?;
    }
    if let Some(v) = h.quorum_acked_lsn {
        out.set_item("x-ms-quorum-acked-lsn", v)?;
    }
    if let Some(v) = h.quorum_acked_local_lsn {
        out.set_item("x-ms-cosmos-quorum-acked-llsn", v)?;
    }
    if let Some(v) = h.retry_after_ms {
        out.set_item("x-ms-retry-after-ms", v)?;
    }
    if let Some(v) = h.correlated_activity_id.as_ref() {
        out.set_item("x-ms-cosmos-correlated-activityid", v.as_str())?;
    }
    if let Some(v) = h.transport_request_id {
        out.set_item("x-ms-transport-request-id", v)?;
    }
    if let Some(v) = h.number_of_read_regions {
        out.set_item("x-ms-number-of-read-regions", v)?;
    }
    if let Some(v) = h.last_state_change_utc.as_ref() {
        out.set_item("x-ms-last-state-change-utc", v.as_str())?;
    }
    if let Some(v) = h.offer_replace_pending {
        out.set_item("x-ms-offer-replace-pending", v)?;
    }
    // Additional modeled fields the driver populates that the legacy path also put in
    // last_response_headers: partition-key-range id, internal partition id,
    // resource quota and usage, gateway and service version, script log
    // results, the tentative-writes flag, and index-transformation /
    // lazy-indexing progress.
    // x-ms-alt-content-path / x-ms-content-path are still pub(crate) on the
    // driver (owner_full_name / owner_id) and will appear here once the
    // driver makes them public.
    if let Some(v) = h.gateway_version.as_ref() {
        out.set_item("x-ms-gatewayversion", v.as_str())?;
    }
    if let Some(v) = h.service_version.as_ref() {
        out.set_item("x-ms-serviceversion", v.as_str())?;
    }
    if let Some(v) = h.resource_quota.as_ref() {
        out.set_item("x-ms-resource-quota", v.as_str())?;
    }
    if let Some(v) = h.resource_usage.as_ref() {
        out.set_item("x-ms-resource-usage", v.as_str())?;
    }
    if let Some(v) = h.has_tentative_writes {
        out.set_item("x-ms-cosmos-allow-tentative-writes", v)?;
    }
    if let Some(v) = h.partition_key_range_id.as_ref() {
        out.set_item("x-ms-documentdb-partitionkeyrangeid", v.as_str())?;
    }
    if let Some(v) = h.internal_partition_id.as_ref() {
        out.set_item("x-ms-cosmos-internal-partition-id", v.as_str())?;
    }
    if let Some(v) = h.log_results.as_ref() {
        out.set_item("x-ms-documentdb-script-log-results", v.as_str())?;
    }
    if let Some(v) = h.collection_index_transformation_progress {
        out.set_item(
            "x-ms-documentdb-collection-index-transformation-progress",
            v,
        )?;
    }
    if let Some(v) = h.collection_lazy_indexing_progress {
        out.set_item("x-ms-documentdb-collection-lazy-indexing-progress", v)?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{
        feed_range_to_response_body, record_diagnostics_for_responseless, response_body_to_vec,
        tuple_from_feed_result, tuple_from_partition_key_ranges_result, tuple_from_result,
        write_response_headers, DriverTransportError, FeedRangeFromPartitionKeyPayload,
        UnsupportedQueryFeatureError,
    };
    use azure_core::Bytes;
    use azure_data_cosmos_driver::error::{CosmosError, CosmosStatus};
    use azure_data_cosmos_driver::models::{
        partition_key_range::PartitionKeyRange, CosmosResponseHeaders, ResponseBody,
    };
    use pyo3::prelude::*;
    use pyo3::types::PyDict;

    use super::super::diagnostics::{BINDING_ATTEMPT_COUNT, BINDING_RETRY_COUNT};
    use std::sync::atomic::Ordering;

    #[test]
    fn unsupported_query_feature_uses_typed_binding_error() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let error = CosmosError::builder()
                .with_status(CosmosStatus::CLIENT_UNSUPPORTED_QUERY_FEATURE)
                .with_message("unsupported query feature: ORDER BY")
                .build();

            let py_error = tuple_from_feed_result(py, Err(error)).unwrap_err();

            assert!(py_error.is_instance_of::<UnsupportedQueryFeatureError>(py));
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
    fn write_response_headers_maps_present_fields_and_skips_missing() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let out = PyDict::new_bound(py);
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

            write_response_headers(&out, &headers).expect("header copy should succeed");

            assert_eq!(
                out.get_item("x-ms-continuation")
                    .expect("dict lookup should succeed")
                    .expect("continuation should be present")
                    .extract::<String>()
                    .expect("continuation must be string"),
                "ct-1"
            );
            assert_eq!(
                out.get_item("x-ms-item-count")
                    .expect("dict lookup should succeed")
                    .expect("item count should be present")
                    .extract::<u32>()
                    .expect("item count must be u32"),
                7
            );
            assert_eq!(
                out.get_item("x-ms-request-duration-ms")
                    .expect("dict lookup should succeed")
                    .expect("request duration should be present")
                    .extract::<f64>()
                    .expect("request duration must be f64"),
                12.5
            );
            assert_eq!(
                out.get_item("x-ms-cosmos-allow-tentative-writes")
                    .expect("dict lookup should succeed")
                    .expect("tentative writes should be present")
                    .extract::<bool>()
                    .expect("tentative writes must be bool"),
                true
            );
            assert_eq!(
                out.get_item("x-ms-documentdb-collection-index-transformation-progress")
                    .expect("dict lookup should succeed")
                    .expect("index transformation progress should be present")
                    .extract::<i64>()
                    .expect("index transformation progress must be i64"),
                88
            );

            assert!(
                out.get_item("x-ms-activity-id")
                    .expect("dict lookup should succeed")
                    .is_none(),
                "missing driver fields must not be emitted"
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

    // ── record_diagnostics_for_responseless tests ─────────────────────────────

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
                py_error.is_instance_of::<DriverTransportError>(py),
                "response-less CosmosError must raise DriverTransportError"
            );
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
                py_error.is_instance_of::<DriverTransportError>(py),
                "response-less feed CosmosError must raise DriverTransportError"
            );
        });
    }
}

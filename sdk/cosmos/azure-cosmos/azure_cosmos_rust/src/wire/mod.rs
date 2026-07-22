// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Shared request and response translation between Python and the Rust driver.
//! Operation-specific execution lives in `items`, `query`, `feed_range`, and
//! `offers`; this module owns the behavior all four families need:
//!
//!   * Request (down): look up the rust driver by handle, parse the container
//!     link and partition key, sort the customer's headers into the fields the
//!     driver takes as typed options vs. a plain header pass-through, build the
//!     operation options, then run the operation on the shared Tokio runtime.
//!   * Reply (up): turn the driver's response -- or an error that still carries a
//!     wire response, like a 404/409 -- into the 5-tuple `BackendResponse` the
//!     Python parser reads; copy every response header into a Python dict keyed by
//!     the real `x-ms-...` wire names; and map a response-less failure to a typed
//!     error the Python layer converts to `ServiceResponseError`.
//!
//! Keeping this behavior here prevents operation families from implementing
//! header mapping, error mapping, and response conversion differently.
//!
//! Terminology (consistent with `factory.py`, `rust.py`, `credential.rs`,
//! `documents/`, `runtime.rs`): binding = this compiled `_rust` extension; rust
//! driver = the `CosmosDriver` engine; shared Tokio runtime = the one process-wide
//! Tokio thread pool that runs the driver's work; driver handle = the string
//! naming which rust driver a client uses.

use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::Duration;

use pyo3::exceptions::{PyAttributeError, PyRuntimeError, PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyTuple};

use azure_core::http::headers::{HeaderName, HeaderValue};
use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::{CosmosError, CosmosStatus},
    models::{
        ActivityId, CosmosOperation, CosmosResponse, FeedRange, ItemReference, PartitionKey,
        PartitionKeyDefinition, PartitionKeyKind, PartitionKeyValue, PartitionKeyVersion,
        ResponseBody, SessionToken,
    },
    options::{
        AvailabilityStrategy, ContentResponseOnWrite, EndToEndOperationLatencyPolicy,
        ExcludedRegions, HedgeThreshold, HedgingStrategy, OperationOptionsBuilder,
    },
};
use serde::{Deserialize, Serialize};

use crate::feed_range_subset::compute_is_feed_range_subset;
use crate::runtime::{drivers, require_runtime_context};

// A NEW exception type, defined here, for a driver operation that failed
// *without* a wire response (transport failure, client-side validation, a timeout
// before any HTTP round-trip). It keeps the existing exception contract intact in
// two ways: it subclasses `RuntimeError` (so any code that already catches
// `RuntimeError` keeps working), and the Python backend translates it into
// azure-core's `ServiceResponseError` so customer
// `except (ServiceRequestError, ServiceResponseError)` handlers and the SDK's
// transport-retry policies behave the same as on the legacy azure-core path,
// instead of seeing a bare `RuntimeError`. (This matches the
// `AsyncCredentialBridgeReentrantError(RuntimeError)` convention on the Python
// side.) One honest limitation: the driver's `CosmosError` carries no
// transport-vs-response classification, so the binding cannot faithfully split
// `ServiceRequestError` from `ServiceResponseError`; it maps to
// `ServiceResponseError`, preserves the typed Cosmos status (rendered by
// `CosmosError`'s Display) in the message, and chains the original error as the
// cause.
// pyo3's `create_exception!` expansion references `cfg(feature = "gil-refs")`,
// a pyo3 feature this destination crate does not declare; the cfg is evaluated
// here (not in pyo3), producing a benign `unexpected_cfgs` warning from
// external-macro code. Scope the allow to just this generated item.
#[allow(unexpected_cfgs)]
mod transport_error {
    pyo3::create_exception!(
        azure_cosmos_rust,
        DriverTransportError,
        pyo3::exceptions::PyRuntimeError,
        "A Cosmos driver operation failed without a wire response (transport failure, \
         client-side validation, or a pre-HTTP timeout)."
    );
}
pub use transport_error::DriverTransportError;

#[allow(unexpected_cfgs)]
mod unsupported_query_error {
    pyo3::create_exception!(
        azure_cosmos_rust,
        UnsupportedQueryFeatureError,
        pyo3::exceptions::PyRuntimeError,
        "The Cosmos driver cannot execute this query plan."
    );
}
pub use unsupported_query_error::UnsupportedQueryFeatureError;

// ---------------------------------------------------------------------------
// Binding-invocation counter (a check for the perf drill, not part of serving
// requests)
// ---------------------------------------------------------------------------
//
// A plain running count, in this process, of how many times the rust binding
// actually ran an item operation. It exists only so the perf drill can catch its
// single biggest risk: trusting the COSMOS_BACKEND label. A results row tagged
// "rust" that actually ran the core-python path would mislabel every number on
// it. This counter answers "did the rust binding really run this?" from INSIDE
// the binding: every item operation, sync or async, bumps it on entry to the
// driver runner below. The perf harness reads it through `_rust.operation_count()`
// and stamps the per-window delta on each row; a core-python process never calls
// the binding, so for it this number never moves. Nothing in the request path
// ever reads it to change behavior -- remove it and customer requests behave
// identically; you just lose the check. `Relaxed` ordering is enough: we only
// need a correct running total, not ordering against other memory.
pub(crate) static BINDING_OP_COUNT: AtomicU64 = AtomicU64::new(0);

/// Per-attempt wire diagnostics counters (tail-latency root-cause investigation).
///
/// `BINDING_OP_COUNT` counts *operations the caller asked for*; these two count
/// *wire attempts the driver actually made* for them. The driver surfaces every
/// attempt on the response as structured diagnostics
/// (`CosmosResponse::diagnostics()` -> `DiagnosticsContext`): one
/// `RequestDiagnostics` per attempt, each tagged with an `execution_context`
/// (`initial` for a first try, or `retry` / `transport_retry` / `hedging` /
/// `region_failover` / `circuit_breaker_probe` for anything the driver
/// re-issued). We fold those records into two process-wide totals so the perf
/// harness can prove, from inside the binding, how many round trips a run really
/// made -- the thing a raw operation count hides:
///   * `BINDING_ATTEMPT_COUNT` -- total attempts (`request_count()` summed).
///     ~1 per clean create/read; ~2 per PATCH, because the driver runs PATCH as a
///     client-side Read-Modify-Write (an internal Read plus an ETag-guarded
///     Replace), so one PATCH op costs two wire round trips.
///   * `BINDING_RETRY_COUNT` -- attempts whose `execution_context` is NOT
///     `initial`, i.e. genuine driver-issued retries / failovers / hedges. Stays
///     0 unless the retry machinery actually fired (a write retried on 503/429
///     then succeeding records 0 terminal errors but a nonzero retry here).
/// Both are read-only observability, `Relaxed` like `BINDING_OP_COUNT`; nothing
/// in the request path reads them to change behavior. Reading the already-built
/// `DiagnosticsContext` is a cheap in-memory walk (no I/O, no logging), so folding
/// it in is safe even during a latency measurement without perturbing the tail.
pub(crate) static BINDING_ATTEMPT_COUNT: AtomicU64 = AtomicU64::new(0);
pub(crate) static BINDING_RETRY_COUNT: AtomicU64 = AtomicU64::new(0);

/// Total item operations that have entered the rust binding's driver runner in
/// this process (see `BINDING_OP_COUNT`). Exposed to Python as
/// `_rust.operation_count()` so the perf harness can confirm, from a counter
/// bumped inside the binding, that the rust path really ran the work a row claims.
#[pyfunction]
pub(crate) fn operation_count() -> u64 {
    BINDING_OP_COUNT.load(Ordering::Relaxed)
}

/// Total wire attempts recorded across every completed operation in this process
/// (see `BINDING_ATTEMPT_COUNT`). Exposed to Python as `_rust.attempt_count()`.
#[pyfunction]
pub(crate) fn attempt_count() -> u64 {
    BINDING_ATTEMPT_COUNT.load(Ordering::Relaxed)
}

/// Total non-`initial` wire attempts -- driver-issued retries / failovers /
/// hedges -- recorded across every completed operation in this process (see
/// `BINDING_RETRY_COUNT`). Exposed to Python as `_rust.retry_count()`.
#[pyfunction]
pub(crate) fn retry_count() -> u64 {
    BINDING_RETRY_COUNT.load(Ordering::Relaxed)
}

// ---------------------------------------------------------------------------
// Shared singleton-operation runner (sync + async)
// ---------------------------------------------------------------------------

/// no-op.
struct AbortOnDrop(tokio::task::AbortHandle);

impl Drop for AbortOnDrop {
    fn drop(&mut self) {
        self.0.abort();
    }
}

/// Look up the cached driver for a client handle, or raise if `init_client`
/// has not run yet (or the client was already closed).
fn lookup_driver(handle: &str) -> PyResult<Arc<CosmosDriver>> {
    drivers()
        .read()
        .get(handle)
        .map(|entry| Arc::clone(&entry.driver))
        .ok_or_else(|| {
            PyRuntimeError::new_err(format!(
                "no driver registered for handle {handle:?}; call init_client first"
            ))
        })
}

/// Turn the driver's `Result<CosmosResponse, CosmosError>` into the
/// `BackendResponse` tuple. A CosmosError carrying a wire response (404 / 409
/// / 412 / ...) becomes the same tuple shape as success so the Python parser raises
/// the right typed exception; only a response-less error (transport failure,
/// client-side validation) becomes a `DriverTransportError`, which the Python
/// backend maps to azure-core's `ServiceResponseError`.
fn tuple_from_result<'py>(
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
                // No wire response: surface a typed transport error (Display
                // preserves the Cosmos status) the Python layer maps to
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
fn tuple_from_feed_result<'py>(
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
                Err(DriverTransportError::new_err(format!(
                    "driver execute_operation failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// Feed-range variant: returns a JSON body in the shape
/// `{"PartitionKeyRanges":[{"id","minInclusive","maxExclusive"}, ...]}`.
fn tuple_from_partition_key_ranges_result<'py>(
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
            // this feed response surfaces x-ms-item-count as "0".
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
                Err(DriverTransportError::new_err(format!(
                    "driver resolve_all_partition_key_ranges failed: {cosmos_error}"
                )))
            }
        }
    }
}

/// feed_range_from_partition_key variant: returns a JSON body in the shape
/// `{"Range":{"min","max","isMinInclusive","isMaxInclusive"}}`.
fn tuple_from_feed_range_from_partition_key_result<'py>(
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
                Err(DriverTransportError::new_err(format!(
                    "driver feed_range_from_partition_key failed: {cosmos_error}"
                )))
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Shared prepared-request input extraction
// ---------------------------------------------------------------------------
//
// Each entry point pulls its inputs off the PreparedRequest with these before
// handing a CosmosOperation builder to run_item_operation.

pub(crate) fn extract_common_prepared_inputs<'py>(
    prepared: &Bound<'py, PyAny>,
) -> PyResult<(String, String, OpModifiers)> {
    let container_link: String = prepared.getattr("container_link")?.extract()?;
    let partition_key_header: String = prepared.getattr("partition_key_header")?.extract()?;
    let headers_obj = prepared.getattr("headers")?;
    let headers_dict: &Bound<'py, PyDict> = headers_obj.downcast::<PyDict>()?;
    let modifiers = extract_op_modifiers(headers_dict)?;
    Ok((container_link, partition_key_header, modifiers))
}

pub(crate) fn extract_body_bytes<'py>(prepared: &Bound<'py, PyAny>) -> PyResult<Vec<u8>> {
    prepared.getattr("body_bytes")?.extract()
}

#[derive(Deserialize)]
struct ReadFeedRangesBody {
    #[serde(rename = "forceRefresh", default)]
    force_refresh: bool,
}

pub(crate) fn parse_read_feed_ranges_force_refresh(body_bytes: &[u8]) -> PyResult<bool> {
    if body_bytes.is_empty() {
        return Ok(false);
    }
    let parsed: ReadFeedRangesBody = serde_json::from_slice(body_bytes).map_err(|e| {
        PyValueError::new_err(format!(
            "read_feed_ranges body must be valid JSON object with optional boolean forceRefresh: {e}"
        ))
    })?;
    Ok(parsed.force_refresh)
}

pub(crate) fn extract_read_feed_ranges_force_refresh<'py>(
    prepared: &Bound<'py, PyAny>,
) -> PyResult<bool> {
    let body_bytes = extract_body_bytes(prepared)?;
    parse_read_feed_ranges_force_refresh(&body_bytes)
}

pub(crate) fn extract_required_item_id<'py>(
    prepared: &Bound<'py, PyAny>,
    error_message: &'static str,
) -> PyResult<String> {
    prepared
        .getattr("item_id")?
        .extract::<Option<String>>()?
        .ok_or_else(|| PyValueError::new_err(error_message))
}

// ---------------------------------------------------------------------------
// Shared header → modifier translation
// ---------------------------------------------------------------------------
//
// run_item_operation calls this for every op to walk PreparedRequest.headers
// and pick out the entries the driver models as typed fields (activity-id,
// session token, no_response, excluded_regions, end-to-end timeout).
// Everything else goes through the driver's custom_headers passthrough.

pub(crate) struct OpModifiers {
    activity_header: Option<String>,
    session_header: Option<String>,
    // ``no_response=True`` -> Disabled, otherwise Enabled. The runner
    // applies this on writes (create / upsert / replace) and ignores it on
    // reads / deletes, which have no body to suppress.
    content_response_on_write: ContentResponseOnWrite,
    excluded_regions_value: Option<ExcludedRegions>,
    end_to_end_timeout: Option<EndToEndOperationLatencyPolicy>,
    // Per-request cross-region hedging control lifted from the
    // ``availabilityStrategy`` option-key. ``Disabled`` turns hedging off for
    // this request (the ``availability_strategy=False`` case); ``Hedging(..)``
    // turns it on with the caller's threshold. ``None`` means the caller did
    // not set it and the driver keeps its default.
    availability_strategy: Option<AvailabilityStrategy>,
    custom_headers: HashMap<HeaderName, HeaderValue>,
}

/// Option-keys that legitimately ride in the ``PreparedRequest.headers`` dict
/// but are NOT wire headers: they are consumed elsewhere in the Python prep
/// (``disableAutomaticIdGeneration`` -> id minting) or lifted to a typed
/// driver field (``partitionKey`` -> the partition-key argument), so
/// `extract_op_modifiers` correctly drops them. Listed here only so the
/// ``COSMOS_WIRE_STRICT`` diagnostic does not flag these expected drops as
/// drift. Compared against the lowercased key.
const INTENTIONALLY_IGNORED_OPTION_KEYS: &[&str] =
    &["disableautomaticidgeneration", "partitionkey"];

fn is_intentionally_ignored_option_key(lower: &str) -> bool {
    INTENTIONALLY_IGNORED_OPTION_KEYS.contains(&lower)
}

/// ``COSMOS_WIRE_STRICT=1`` (or ``true``) turns the silent drop of an
/// unrecognized option-key in `extract_op_modifiers` into a hard error, so a
/// Python-side wire knob that was never wired into Rust is caught in tests/CI
/// instead of producing wrong wire bytes with green tests. Unset by default
/// => production behavior is unchanged (lenient silent drop). Read only when a
/// genuinely unrecognized, non-allowlisted key is encountered (rare/never in
/// production), so the hot path pays nothing.
fn wire_strict_enabled() -> bool {
    std::env::var("COSMOS_WIRE_STRICT")
        .map(|v| v == "1" || v.eq_ignore_ascii_case("true"))
        .unwrap_or(false)
}

/// Parse the compact ``availabilityStrategy`` wire value the Python prep emits
/// into the driver's typed strategy. The Python side normalizes the customer's
/// ``availability_strategy`` (bool or threshold dict) to one of:
///   - ``"disabled"``            -> hedging off for this request
///   - ``"enabled:<threshold_ms>"`` -> hedging on with that primary threshold
/// A zero / unparseable threshold falls back to hedging with no explicit
/// threshold (the driver's default). Returns ``None`` for an empty value.
fn parse_availability_strategy(value: &str) -> Option<AvailabilityStrategy> {
    let trimmed = value.trim();
    if trimmed.is_empty() {
        return None;
    }
    if trimmed.eq_ignore_ascii_case("disabled") {
        return Some(AvailabilityStrategy::Disabled);
    }
    // "enabled" or "enabled:<threshold_ms>".
    let threshold_ms = trimmed
        .split_once(':')
        .and_then(|(_, ms)| ms.trim().parse::<u64>().ok());
    let hedging = match threshold_ms.and_then(|ms| HedgeThreshold::new(Duration::from_millis(ms))) {
        Some(threshold) => HedgingStrategy::new(threshold),
        // No usable threshold -> fall back to the driver's default threshold.
        None => HedgingStrategy::new(
            HedgeThreshold::new(Duration::from_millis(DEFAULT_HEDGE_THRESHOLD_MS))
                .expect("default hedge threshold is positive"),
        ),
    };
    Some(AvailabilityStrategy::Hedging(hedging))
}

/// Default primary hedge threshold, matching the Python SDK's
/// ``DEFAULT_THRESHOLD_MS`` (see ``_availability_strategy_config``).
const DEFAULT_HEDGE_THRESHOLD_MS: u64 = 500;

fn extract_op_modifiers(headers_dict: &Bound<'_, PyDict>) -> PyResult<OpModifiers> {
    let mut activity_header: Option<String> = None;
    let mut session_header: Option<String> = None;
    // ``no_response=True`` -> Disabled, otherwise Enabled. The driver
    // default is Disabled, so we must set this explicitly to return a
    // body on writes when the caller did not opt out.
    let mut content_response_on_write: ContentResponseOnWrite = ContentResponseOnWrite::Enabled;
    // ``excluded_locations`` kwarg -> typed ExcludedRegions on the
    // driver. The Python helper writes the raw list of region names
    // under the option-key ``excludedLocations``. ``None`` here means
    // the kwarg was not set and the driver picks the default.
    let mut excluded_regions_value: Option<ExcludedRegions> = None;
    // ``timeout`` (seconds) kwarg -> driver end-to-end latency policy.
    // The Python helper writes it under the sentinel header name
    // ``__overall_timeout_seconds`` because the rust path skips the
    // azure-core pipeline that would normally consume ``timeout``.
    // Sub-second values are clamped by the driver to its 1-second
    // minimum.
    let mut end_to_end_timeout: Option<EndToEndOperationLatencyPolicy> = None;
    // ``availability_strategy`` kwarg -> typed cross-region hedging control on
    // the driver. The Python helper writes a compact string under the
    // ``availabilityStrategy`` option-key (see parse_availability_strategy).
    let mut availability_strategy: Option<AvailabilityStrategy> = None;
    // Per-request headers the driver does not model as typed fields
    // (intended-collection-rid, indexing directive, pre/post triggers,
    // priority, throughput bucket, If-Match / If-None-Match) flow
    // through the driver's custom-headers passthrough.
    let mut custom_headers: HashMap<HeaderName, HeaderValue> = HashMap::new();
    for (key, value) in headers_dict.iter() {
        let key_str: String = key.extract()?;
        let lower = key_str.to_ascii_lowercase();
        // Typed fields on the driver operation — handled out of band.
        if lower == "x-ms-activity-id" {
            activity_header = Some(value.extract()?);
            continue;
        }
        // Accept both the wire-name and the helper's camelCase
        // option-key form so the value reaches the driver either way.
        if lower == "x-ms-session-token" || lower == "sessiontoken" {
            session_header = Some(value.extract()?);
            continue;
        }
        // ``no_response`` lifted to the typed options field.
        if lower == "responsepayloadonwritedisabled" {
            // Truthy -> caller asked for "no body"; falsy -> caller
            // explicitly asked for the body.
            content_response_on_write = if value.is_truthy()? {
                ContentResponseOnWrite::Disabled
            } else {
                ContentResponseOnWrite::Enabled
            };
            continue;
        }
        // ``excludedLocations`` -> typed ExcludedRegions on the driver.
        // Accepts any iterable of region-name strings; each element is
        // normalised by the driver via Region::from.
        if lower == "excludedlocations" {
            let regions: Vec<String> = value.extract().map_err(|e| {
                PyValueError::new_err(format!(
                    "excluded_locations must be a sequence of region name strings: {e}"
                ))
            })?;
            excluded_regions_value = Some(regions.into_iter().collect::<ExcludedRegions>());
            continue;
        }
        // Sentinel header carrying the customer's ``timeout`` kwarg.
        // Accepts int or float; non-positive or non-finite values are
        // ignored to match the legacy behaviour.
        if lower == "__overall_timeout_seconds" {
            let seconds: f64 = value.extract().map_err(|e| {
                PyValueError::new_err(format!(
                    "__overall_timeout_seconds must be an int/float number of seconds: {e}"
                ))
            })?;
            if seconds.is_finite() && seconds > 0.0 {
                end_to_end_timeout = Some(EndToEndOperationLatencyPolicy::new(
                    Duration::from_secs_f64(seconds),
                ));
            }
            continue;
        }
        // ``availabilityStrategy`` -> typed cross-region hedging control.
        if lower == "availabilitystrategy" {
            let strategy_str: String = value.extract().map_err(|e| {
                PyValueError::new_err(format!(
                    "availabilityStrategy must be a string ('disabled' or 'enabled[:<ms>]'): {e}"
                ))
            })?;
            availability_strategy = parse_availability_strategy(&strategy_str);
            continue;
        }
        // ``initialHeaders`` -> arbitrary customer headers forwarded verbatim.
        // The Python prep hands these as a nested dict (rather than flattening
        // them into the top-level headers map) so their provenance is explicit:
        // every entry is a customer-supplied header and is forwarded as-is,
        // including non-``x-ms-`` names the option-key translation below would
        // otherwise drop. Keeping them separate from the option-key stream also
        // means COSMOS_WIRE_STRICT still guards genuine option-key drift.
        if lower == "initialheaders" {
            let inner: &Bound<'_, PyDict> = value.downcast().map_err(|e| {
                PyValueError::new_err(format!(
                    "initialHeaders must be a dict of header name -> value: {e}"
                ))
            })?;
            for (header_key, header_value) in inner.iter() {
                let header_key_str: String = header_key.extract()?;
                let header_value_str: String = match header_value.extract::<String>() {
                    Ok(s) => s,
                    Err(_) => header_value.str()?.to_string(),
                };
                custom_headers.insert(
                    HeaderName::from(header_key_str.to_ascii_lowercase()),
                    HeaderValue::from(header_value_str),
                );
            }
            continue;
        }
        // Everything else: translate the helper's option-key name
        // (or accept an already-wire-name string) to the ``x-ms-...``
        // header the service expects, then push to custom headers.
        // Unknown keys are dropped, matching the legacy behaviour.
        let wire_name: Option<&'static str> = match lower.as_str() {
            "pretriggerinclude" => Some("x-ms-documentdb-pre-trigger-include"),
            "posttriggerinclude" => Some("x-ms-documentdb-post-trigger-include"),
            "indexingdirective" => Some("x-ms-indexing-directive"),
            "prioritylevel" => Some("x-ms-cosmos-priority-level"),
            "throughputbucket" => Some("x-ms-cosmos-throughput-bucket"),
            "containerrid" => Some("x-ms-cosmos-intended-collection-rid"),
            // Read-side cache-validation kwarg. Accept the option-key
            // form as a defensive fallback; the Python prep already
            // writes the wire-name form directly (truthy-only gate
            // means `0` never reaches here).
            "maxintegratedcachestaleness" => Some("x-ms-dedicatedgateway-max-age"),
            // If-Match / If-None-Match are listed explicitly because
            // they do not start with ``x-ms-``.
            "if-match" => Some("if-match"),
            "if-none-match" => Some("if-none-match"),
            // Already a wire-name header (caller-supplied
            // initial_headers, or a future site writing the wire name
            // directly). Forward as-is.
            other if other.starts_with("x-ms-") || other == "prefer" => None,
            // Unrecognized key. In normal operation a handful of
            // prep-internal option-keys (e.g. ``disableAutomaticIdGeneration``
            // on every create/upsert/replace, ``partitionKey``) ride in the
            // headers dict but are NOT wire headers -- they are consumed
            // elsewhere in the Python prep (id minting) or lifted to a typed
            // driver field (partition key), so dropping them here is correct
            // and matches the legacy path.
            //
            // The hazard (the silent-correctness landmine) is a *new* wire
            // knob added on the Python side (``flatten_options_to_headers`` /
            // ``COMMON_OPTIONS``) without a matching arm above: it would be
            // dropped here, producing wrong wire bytes with green tests.
            // ``COSMOS_WIRE_STRICT=1`` (for tests / CI / local dev) turns an
            // unrecognized, non-allowlisted key into a hard error so the drift
            // is caught immediately. Production leaves the env unset and keeps
            // the lenient silent drop, so there is ZERO behavior change unless
            // the flag is set. The allowlist check runs first so the hot path
            // (allowlisted keys) never reads the environment.
            _ => {
                if !is_intentionally_ignored_option_key(&lower) && wire_strict_enabled() {
                    return Err(PyValueError::new_err(format!(
                        "COSMOS_WIRE_STRICT: option-key '{key_str}' reached the Rust wire \
                         layer (extract_op_modifiers) with no translation arm; it would be \
                         silently dropped on the fast path, emitting wrong wire bytes. Add a \
                         wire-name arm here (and update \
                         _request_prep.RUST_HANDLED_OPTION_KEYS), or, if it is a non-wire \
                         prep-internal flag, add it to INTENTIONALLY_IGNORED_OPTION_KEYS."
                    )));
                }
                continue;
            }
        };
        // Stringify the value: Python may have written a non-str
        // (e.g. int for indexing_directive); coerce via str() so the
        // wire bytes match the legacy path.
        let value_str: String = match value.extract::<String>() {
            Ok(s) => s,
            Err(_) => value.str()?.to_string(),
        };
        let header_name = match wire_name {
            Some(name) => HeaderName::from_static(name),
            None => HeaderName::from(lower),
        };
        custom_headers.insert(header_name, HeaderValue::from(value_str));
    }

    Ok(OpModifiers {
        activity_header,
        session_header,
        content_response_on_write,
        excluded_regions_value,
        end_to_end_timeout,
        availability_strategy,
        custom_headers,
    })
}

/// Build an OperationOptions from the typed-field values the binding
/// lifted out of the headers dict. ``content_response`` is ``Some(_)`` for
/// the write ops (create / upsert / replace) and ``None`` for reads /
/// deletes, which leave the driver default in place.
fn build_operation_options(
    content_response: Option<ContentResponseOnWrite>,
    excluded_regions: Option<ExcludedRegions>,
    end_to_end_timeout: Option<EndToEndOperationLatencyPolicy>,
    availability_strategy: Option<AvailabilityStrategy>,
    custom_headers: HashMap<HeaderName, HeaderValue>,
) -> azure_data_cosmos_driver::options::OperationOptions {
    let mut builder = OperationOptionsBuilder::new();
    if let Some(cr) = content_response {
        builder = builder.with_content_response_on_write(cr);
    }
    if let Some(regions) = excluded_regions {
        builder = builder.with_excluded_regions(regions);
    }
    if let Some(policy) = end_to_end_timeout {
        builder = builder.with_end_to_end_latency_policy(policy);
    }
    if let Some(strategy) = availability_strategy {
        builder = builder.with_availability_strategy(strategy);
    }
    if !custom_headers.is_empty() {
        builder = builder.with_custom_headers(custom_headers);
    }
    builder.build()
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
    let items: Vec<PyObject> = vec![
        status_code.into_py(py),
        sub_status.into_py(py),
        response_headers.into_any().unbind(),
        body_py.into_any().unbind(),
        diagnostics_py,
    ];
    Ok(PyTuple::new_bound(py, &items))
}

/// Build the reply tuple for a successful point operation: read status and
/// sub-status, fold this operation's wire attempts into the diagnostics counters,
/// copy the response headers under their wire names, and convert the body.
fn backend_response_tuple_from_success<'py>(
    py: Python<'py>,
    response: azure_data_cosmos_driver::models::CosmosResponse,
) -> PyResult<Bound<'py, PyTuple>> {
    let status = response.status();
    let status_code = u16::from(status.status_code()) as i64;
    // SubStatusCode wraps a u16; use ``.value()`` to read it.
    let sub_status = status.sub_status().map(|s| s.value() as i64).unwrap_or(0);
    // Fold this operation's per-attempt wire diagnostics into the process-wide
    // attempt/retry counters before stringifying them (see BINDING_ATTEMPT_COUNT).
    // `diagnostics()` is a cheap Arc clone; the walk touches only in-memory records.
    let diag = response.diagnostics();
    BINDING_ATTEMPT_COUNT.fetch_add(diag.request_count() as u64, Ordering::Relaxed);
    let retries = diag
        .requests()
        .iter()
        .filter(|req| req.execution_context().as_str() != "initial")
        .count() as u64;
    BINDING_RETRY_COUNT.fetch_add(retries, Ordering::Relaxed);
    let diagnostics = diag.to_string();
    // dict keyed by the actual `x-ms-...` wire-header names. This is what
    // the Python parser (`_helpers/_response_parse.py`) reads to populate
    // `client_connection.last_response_headers`, so customer code that
    // does e.g. `last_response_headers["etag"]` keeps working on the
    // Rust path.
    let driver_headers = response.headers();
    let response_headers = PyDict::new_bound(py);
    write_response_headers(&response_headers, driver_headers)?;

    let body_vec = response_body_to_vec(response.into_body())?;
    backend_response_tuple(
        py,
        status_code,
        sub_status,
        response_headers,
        &body_vec,
        Some(diagnostics.as_str()),
    )
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
    let diag = response.diagnostics();
    BINDING_ATTEMPT_COUNT.fetch_add(diag.request_count() as u64, Ordering::Relaxed);
    let retries = diag
        .requests()
        .iter()
        .filter(|req| req.execution_context().as_str() != "initial")
        .count() as u64;
    BINDING_RETRY_COUNT.fetch_add(retries, Ordering::Relaxed);
    let diagnostics = diag.to_string();
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
/// fires the test harness will surface a body mismatch that's easier to
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
/// returns for a query. The driver hands back the rows as a list of item bytes
/// (or raw bytes, or nothing); this stitches them into that envelope so the parser
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

/// Offer-feed variant of `tuple_from_feed_result`: an offer/throughput query page
/// becomes a success reply whose body is the `{"Offers":[...]}` envelope the Python
/// offer parser reads; `None` (no offers) becomes an empty `{"Offers":[]}` page; an
/// error carrying a real service response (e.g. a 400) becomes the same tuple shape
/// so the parser raises the right Cosmos error, while a pure transport failure
/// becomes a Rust error.
fn tuple_from_offer_feed_result<'py>(
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
                Err(DriverTransportError::new_err(format!(
                    "driver execute_operation failed: {cosmos_error}"
                )))
            }
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
    let diag = response.diagnostics();
    BINDING_ATTEMPT_COUNT.fetch_add(diag.request_count() as u64, Ordering::Relaxed);
    let retries = diag
        .requests()
        .iter()
        .filter(|req| req.execution_context().as_str() != "initial")
        .count() as u64;
    BINDING_RETRY_COUNT.fetch_add(retries, Ordering::Relaxed);
    let diagnostics = diag.to_string();
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
struct PartitionKeyRangesEnvelope<'a> {
    #[serde(rename = "PartitionKeyRanges")]
    partition_key_ranges: Vec<PartitionKeyRangeWire<'a>>,
}

#[derive(Serialize)]
struct PartitionKeyRangeWire<'a> {
    id: &'a str,
    #[serde(rename = "minInclusive")]
    min_inclusive: &'a str,
    #[serde(rename = "maxExclusive")]
    max_exclusive: &'a str,
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
            id: range.id.as_str(),
            min_inclusive: range.min_inclusive.as_str(),
            max_exclusive: range.max_exclusive.as_str(),
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

// ---------------------------------------------------------------------------
// is_feed_range_subset (binding plumbing)
// ---------------------------------------------------------------------------
//
// The pure parse/normalize/compare math lives in `crate::feed_range_subset`
// (`compute_is_feed_range_subset`), which has no Python or wire dependencies. The
// functions below are the binding side: they run that computation -- sync and
// async -- and package the yes/no into the `BackendResponse` 5-tuple the python
// parser reads (`{"IsSubset": <bool>}`). There is no network call, so the sync
// entry needs no driver handle or Tokio runtime.

/// Shape the boolean result (or a validation error) into the `BackendResponse`
/// 5-tuple the python parser reads, with a `{"IsSubset": <bool>}` body.
fn tuple_from_is_feed_range_subset_result<'py>(
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
    // Wire-error responses still made real attempts -- fold them in too so the
    // counters cover the full round-trip count, not just successes.
    let diag = response.diagnostics();
    BINDING_ATTEMPT_COUNT.fetch_add(diag.request_count() as u64, Ordering::Relaxed);
    let retries = diag
        .requests()
        .iter()
        .filter(|req| req.execution_context().as_str() != "initial")
        .count() as u64;
    BINDING_RETRY_COUNT.fetch_add(retries, Ordering::Relaxed);
    let diagnostics = diag.to_string();

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
    let diag = response.diagnostics();
    BINDING_ATTEMPT_COUNT.fetch_add(diag.request_count() as u64, Ordering::Relaxed);
    let retries = diag
        .requests()
        .iter()
        .filter(|req| req.execution_context().as_str() != "initial")
        .count() as u64;
    BINDING_RETRY_COUNT.fetch_add(retries, Ordering::Relaxed);
    let diagnostics = diag.to_string();

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
    // driver (owner_full_name / owner_id) and will surface here once the
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

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// Parse "dbs/<db>/colls/<coll>" into ("<db>", "<coll>").
///
/// Reads the four segments off the split iterator instead of collecting into a
/// `Vec`, to avoid allocating one per call. The trailing `None` arm rejects a
/// path with extra segments.
fn parse_container_link(link: &str) -> PyResult<(String, String)> {
    let mut parts = link.split('/');
    match (
        parts.next(),
        parts.next(),
        parts.next(),
        parts.next(),
        parts.next(),
    ) {
        (Some("dbs"), Some(db), Some("colls"), Some(coll), None) => {
            Ok((db.to_string(), coll.to_string()))
        }
        _ => Err(PyValueError::new_err(format!(
            "container_link must be 'dbs/<db>/colls/<coll>', got {link:?}"
        ))),
    }
}

/// Parse the JSON-array partition-key header into a typed `PartitionKey`.
///
/// Accepts every shape the Python helper (`_helpers/_pk_wire.py`) emits:
///
///   * Single scalar:                 `["customerA"]`, `[123]`, `[true]`, `[null]`
///   * Undefined (PK path missing):   `[{}]`        -> `PartitionKeyValue::undefined()`
///   * Hierarchical (2 or 3 levels):  `["t1","r1"]`, `["t1","r1","s1"]`
///   * Hierarchical with missing leaf: `["t1",null]`
///
/// The one shape we still reject is the bare empty array `[]`, which the
/// driver overloads to mean "cross-partition query" (`PartitionKey::EMPTY`
/// emits the `x-ms-documentdb-query-enablecrosspartition` header instead of
/// `x-ms-documentdb-partitionkey: []`). Until the driver splits those two
/// concepts, we fail fast here so a partitionless-container write cannot
/// silently land in the wrong place.
fn parse_partition_key_header(header: &str) -> PyResult<PartitionKey> {
    let parsed: Vec<serde_json::Value> = serde_json::from_str(header).map_err(|e| {
        PyValueError::new_err(format!("invalid partition_key_header {header:?}: {e}"))
    })?;

    if parsed.is_empty() {
        return Err(PyValueError::new_err(
            "partition_key_header `[]` (NonePartitionKey / partitionless container) \
             is not yet supported on the Rust path: the driver overloads `PartitionKey::EMPTY` \
             to mean cross-partition query, so emitting it would target the wrong header. \
             Use the legacy backend for partitionless containers until the driver splits \
             those two concepts."
                .to_string(),
        ));
    }
    if parsed.len() > 3 {
        return Err(PyValueError::new_err(format!(
            "partition_key_header has {} components; Cosmos partition keys can have at most 3 levels",
            parsed.len()
        )));
    }

    let mut components: Vec<PartitionKeyValue> = Vec::with_capacity(parsed.len());
    for value in parsed {
        components.push(json_value_to_pk_component(value)?);
    }
    Ok(PartitionKey::from(components))
}

/// Partition-key header parser for feed_range_from_partition_key.
///
/// Unlike point operations, this API intentionally accepts:
/// - `[]` for the `_Empty` sentinel path (`NonePartitionKeyValue` on system-key containers),
/// - `[[]]` for an explicitly empty sequence value (`partition_key=[]`).
/// Both shapes are carried through with source metadata so run-time logic can preserve
/// legacy per-container semantics.
fn parse_feed_range_partition_key_header(header: &str) -> PyResult<FeedRangePartitionKeyInput> {
    let parsed: Vec<serde_json::Value> = serde_json::from_str(header).map_err(|e| {
        PyValueError::new_err(format!("invalid partition_key_header {header:?}: {e}"))
    })?;

    if parsed.len() > 3 {
        return Err(PyValueError::new_err(format!(
            "partition_key_header has {} components; Cosmos partition keys can have at most 3 levels",
            parsed.len()
        )));
    }
    if parsed.is_empty() {
        return Ok(FeedRangePartitionKeyInput {
            partition_key: PartitionKey::from(Vec::<PartitionKeyValue>::new()),
            source: FeedRangePartitionKeySource::EmptySentinel,
        });
    }
    if parsed.len() == 1 {
        if let serde_json::Value::Array(inner) = &parsed[0] {
            if inner.is_empty() {
                return Ok(FeedRangePartitionKeyInput {
                    partition_key: PartitionKey::from(Vec::<PartitionKeyValue>::new()),
                    source: FeedRangePartitionKeySource::ExplicitEmptySequence,
                });
            }
        }
    }

    let mut components: Vec<PartitionKeyValue> = Vec::with_capacity(parsed.len());
    for value in parsed {
        components.push(json_value_to_pk_component(value)?);
    }
    Ok(FeedRangePartitionKeyInput {
        partition_key: PartitionKey::from(components),
        source: FeedRangePartitionKeySource::Standard,
    })
}

/// Work out the query scope from the partition-key header string the wrapper set.
/// `[]` means search the whole container (cross-partition); a non-empty value like
/// `["alice-123"]` means search that one logical partition. Allows the 1-3 levels a
/// Cosmos partition key can have, and rejects anything longer or not valid JSON.
fn parse_query_target_header(header: &str) -> PyResult<QueryTarget> {
    let parsed: Vec<serde_json::Value> = serde_json::from_str(header).map_err(|e| {
        PyValueError::new_err(format!("invalid partition_key_header {header:?}: {e}"))
    })?;

    if parsed.is_empty() {
        return Ok(QueryTarget::CrossPartition);
    }
    if parsed.len() > 3 {
        return Err(PyValueError::new_err(format!(
            "partition_key_header has {} components; Cosmos partition keys can have at most 3 levels",
            parsed.len()
        )));
    }

    let mut components: Vec<PartitionKeyValue> = Vec::with_capacity(parsed.len());
    for value in parsed {
        components.push(json_value_to_pk_component(value)?);
    }
    Ok(QueryTarget::Partition(PartitionKey::from(components)))
}

/// Convert a single JSON-array element into a `PartitionKeyValue`.
fn json_value_to_pk_component(value: serde_json::Value) -> PyResult<PartitionKeyValue> {
    match value {
        // JSON null -> typed Null. Use the `NULL` const exposed on
        // `PartitionKeyValue` directly rather than going through the
        // `From<Option<T>>` impl, both for clarity and to avoid coupling
        // to that impl's continued existence across driver versions.
        serde_json::Value::Null => Ok(PartitionKeyValue::NULL),
        serde_json::Value::Bool(b) => Ok(PartitionKeyValue::from(b)),
        serde_json::Value::Number(n) => match n.as_f64() {
            Some(f) => Ok(PartitionKeyValue::from(f)),
            None => Err(PyValueError::new_err(format!(
                "non-finite number in partition key header: {n}"
            ))),
        },
        serde_json::Value::String(s) => Ok(PartitionKeyValue::from(s)),
        // Empty JSON object `{}` is the wire shape for "PK path missing
        // on this document" (Python's `_Undefined`). Map it to the
        // driver's dedicated ``UNDEFINED`` constant.
        serde_json::Value::Object(obj) if obj.is_empty() => Ok(PartitionKeyValue::UNDEFINED),
        // Anything else is not a valid partition-key component on the wire.
        other => Err(PyValueError::new_err(format!(
            "unsupported partition key value: {other}"
        ))),
    }
}

/// Read the document `id` out of a JSON body. The caller guarantees it is
/// present; we error if it is not rather than inventing one.
///
/// This reads only the `id` field and skips the rest of the document, so a
/// large body isn't parsed in full just to get one string. The `id` is kept as
/// a `Value` so a present-but-non-string value still gives the "no string id"
/// error.
#[derive(Deserialize)]
struct BodyId {
    id: Option<serde_json::Value>,
}

pub(crate) fn extract_item_id(body: &[u8]) -> PyResult<String> {
    let parsed: BodyId = serde_json::from_slice(body)
        .map_err(|e| PyValueError::new_err(format!("body is not valid JSON: {e}")))?;
    parsed
        .id
        .as_ref()
        .and_then(|v| v.as_str())
        .map(|s| s.to_string())
        .ok_or_else(|| PyValueError::new_err("body has no string `id` field"))
}

/// Resolve the item id for a create / upsert without re-parsing the whole body.
///
/// Python already holds the document dict and resolved its id during request prep
/// (`ensure_item_id` for create, the body's own id for upsert), so it carries the
/// id on `PreparedRequest.item_id`. Prefer that: reading one Python attribute is
/// O(1), whereas re-parsing the body to find `id` has no early exit -- serde must
/// scan the entire document to consume it. On a small item that is microseconds
/// against a multi-ms network call, but on a large body (e.g. a 256 KB blob) at
/// thousands/sec it is real, repeated CPU for one field Python already had.
///
/// Fall back to parsing the body only when the attribute is absent or empty -- an
/// older Python prep that did not set it. The fallback also preserves the existing
/// "body has no string `id`" / "non-string id" error behavior, because Python only
/// fills the attribute with a non-empty string id (anything else stays unset and
/// lands here). For create/upsert the body's id is authoritative and Python derived
/// `item_id` from that same body, so the attribute and the body always agree.
pub(crate) fn extract_create_item_id<'py>(
    prepared: &Bound<'py, PyAny>,
    body: &[u8],
) -> PyResult<String> {
    if let Some(id) = prepared
        .getattr("item_id")?
        .extract::<Option<String>>()?
        .filter(|s| !s.is_empty())
    {
        return Ok(id);
    }
    extract_item_id(body)
}

#[cfg(test)]
mod tests {
    use super::{
        extract_item_id, extract_op_modifiers, feed_range_to_response_body,
        is_intentionally_ignored_option_key, json_value_to_pk_component,
        maybe_handle_feed_range_partition_key_special_case, parse_availability_strategy,
        parse_container_link, parse_feed_range_partition_key_header, parse_partition_key_header,
        parse_query_target_header, parse_read_feed_ranges_force_refresh, response_body_to_vec,
        tuple_from_feed_result, tuple_from_partition_key_ranges_result, write_response_headers,
        FeedRangeFromPartitionKeyPayload, FeedRangePartitionKeySource, QueryTarget,
        UnsupportedQueryFeatureError, DEFAULT_HEDGE_THRESHOLD_MS,
    };
    use azure_core::http::headers::{HeaderName, HeaderValue};
    use azure_core::Bytes;
    use azure_data_cosmos_driver::error::{CosmosError, CosmosStatus};
    use azure_data_cosmos_driver::models::{
        partition_key_range::PartitionKeyRange, CosmosResponseHeaders, PartitionKeyDefinition,
        PartitionKeyKind, PartitionKeyVersion, ResponseBody,
    };
    use azure_data_cosmos_driver::options::{
        AvailabilityStrategy, HedgeThreshold, HedgingStrategy,
    };
    use pyo3::prelude::*;
    use pyo3::types::PyDict;
    use std::time::Duration;

    // Tests for the per-operation parsers: the container-link split, the
    // partition-key header parse, the body-id read, and the per-value
    // conversion. They build no Python objects, so they run under `cargo test`
    // on their own: the success cases check the parsed value, the bad inputs
    // check that an error comes back.

    // ---- parse_container_link -------------------------------------------------

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

    #[test]
    fn container_link_splits_db_and_collection() {
        // The one shape the resolver expects: dbs/<db>/colls/<coll>.
        let (db, coll) = parse_container_link("dbs/OrdersDB/colls/Customers").unwrap();
        assert_eq!(db, "OrdersDB");
        assert_eq!(coll, "Customers");
    }

    #[test]
    fn container_link_rejects_malformed_paths() {
        // Wrong prefixes, too few segments, a trailing extra segment, and an
        // empty string must all fail rather than yield a wrong (db, coll) that
        // would route the request to the wrong place.
        assert!(parse_container_link("colls/c/dbs/d").is_err()); // swapped keywords
        assert!(parse_container_link("dbs/OrdersDB").is_err()); // missing coll
        assert!(parse_container_link("dbs/d/colls/c/docs/x").is_err()); // extra segment
        assert!(parse_container_link("").is_err());
    }

    // ---- extract_item_id (create / upsert read the id from the body) ----------

    #[test]
    fn item_id_read_from_body_and_ignores_other_fields() {
        // Only `id` matters; the rest of the document is skipped, including when
        // it precedes/follows id, so it works regardless of field order.
        assert_eq!(extract_item_id(br#"{"id":"C-42"}"#).unwrap(), "C-42");
        assert_eq!(
            extract_item_id(br#"{"name":"Ada","id":"C-42","tags":["x"]}"#).unwrap(),
            "C-42"
        );
    }

    #[test]
    fn item_id_rejects_missing_invalid_and_non_string_id() {
        assert!(extract_item_id(br#"{"name":"Ada"}"#).is_err()); // no id
        assert!(extract_item_id(br#"{"id":42}"#).is_err()); // non-string id
        assert!(extract_item_id(b"not json").is_err()); // invalid JSON
    }

    // ---- parse_partition_key_header -------------------------------------------

    #[test]
    fn pk_header_accepts_every_supported_shape() {
        // Each shape the Python helper emits must parse: scalars, typed null,
        // boolean, the `[{}]` undefined marker, and 2- or 3-level hierarchical.
        for header in [
            r#"["customerA"]"#,
            "[123]",
            "[true]",
            "[null]",
            "[{}]",           // PK path missing -> undefined
            r#"["t1","r1"]"#, // hierarchical
            r#"["t1","r1","s1"]"#,
            r#"["t1",null]"#, // hierarchical with missing leaf
        ] {
            assert!(
                parse_partition_key_header(header).is_ok(),
                "should parse: {header}"
            );
        }
    }

    #[test]
    fn pk_header_rejects_empty_overflow_and_garbage() {
        // `[]` is overloaded by the driver to mean cross-partition query, so a
        // partitionless write must fail fast rather than land in the wrong place.
        assert!(parse_partition_key_header("[]").is_err());
        // Cosmos allows at most 3 levels.
        assert!(parse_partition_key_header(r#"["a","b","c","d"]"#).is_err());
        // Not a JSON array.
        assert!(parse_partition_key_header("nonsense").is_err());
    }

    // ---- parse_query_target_header ------------------------------------------

    #[test]
    fn query_target_header_accepts_partition_and_cross_partition_shapes() {
        assert!(matches!(
            parse_query_target_header("[]").unwrap(),
            QueryTarget::CrossPartition
        ));
        assert!(matches!(
            parse_query_target_header(r#"["customerA"]"#).unwrap(),
            QueryTarget::Partition(_)
        ));
        assert!(matches!(
            parse_query_target_header(r#"[null]"#).unwrap(),
            QueryTarget::Partition(_)
        ));
    }

    #[test]
    fn query_target_header_rejects_overflow_and_garbage() {
        assert!(parse_query_target_header(r#"["a","b","c","d"]"#).is_err());
        assert!(parse_query_target_header("nonsense").is_err());
    }

    // ---- parse_feed_range_partition_key_header -------------------------------

    #[test]
    fn feed_range_partition_key_header_accepts_empty_and_partition_shapes() {
        let empty = parse_feed_range_partition_key_header("[]").unwrap();
        assert_eq!(empty.partition_key.len(), 0);
        assert_eq!(empty.source, FeedRangePartitionKeySource::EmptySentinel);
        let explicit_empty_sequence = parse_feed_range_partition_key_header("[[]]").unwrap();
        assert_eq!(explicit_empty_sequence.partition_key.len(), 0);
        assert_eq!(
            explicit_empty_sequence.source,
            FeedRangePartitionKeySource::ExplicitEmptySequence
        );
        for header in [
            r#"["customerA"]"#,
            "[123]",
            "[true]",
            "[null]",
            "[{}]",
            r#"["t1","r1"]"#,
        ] {
            let parsed = parse_feed_range_partition_key_header(header).unwrap();
            assert_eq!(parsed.source, FeedRangePartitionKeySource::Standard);
            assert!(
                parsed.partition_key.len() >= 1,
                "standard header must produce partition-key components"
            );
        }
    }

    #[test]
    fn feed_range_partition_key_header_rejects_overflow_and_garbage() {
        assert!(parse_feed_range_partition_key_header(r#"["a","b","c","d"]"#).is_err());
        assert!(parse_feed_range_partition_key_header("nonsense").is_err());
    }

    #[test]
    fn feed_range_special_case_empty_sentinel_matches_legacy_v2_hashing() {
        let hash_v2 = PartitionKeyDefinition::from("/pk")
            .with_kind(PartitionKeyKind::Hash)
            .with_version(PartitionKeyVersion::V2);
        let payload = maybe_handle_feed_range_partition_key_special_case(
            &hash_v2,
            FeedRangePartitionKeySource::EmptySentinel,
        )
        .expect("v2 hash _Empty should be supported")
        .expect("v2 hash _Empty should short-circuit with payload");
        assert_eq!(payload.min, "00000000000000000000000000000000");
        assert_eq!(payload.max, "00000000000000000000000000000000");
        assert!(payload.is_max_inclusive);
    }

    #[test]
    fn feed_range_special_case_empty_sentinel_v1_matches_legacy_type_error() {
        let hash_v1 = PartitionKeyDefinition::from("/pk")
            .with_kind(PartitionKeyKind::Hash)
            .with_version(PartitionKeyVersion::V1);
        let err = maybe_handle_feed_range_partition_key_special_case(
            &hash_v1,
            FeedRangePartitionKeySource::EmptySentinel,
        )
        .expect_err("v1 hash _Empty should raise legacy type error");
        match err {
            super::FeedRangeFromPartitionKeyError::LegacyType(message) => {
                assert!(message.contains("Unexpected type for PK component"));
            }
            other => panic!("unexpected error: {other:?}"),
        }
    }

    #[test]
    fn feed_range_special_case_explicit_empty_sequence_matches_legacy_routing() {
        let hash_v2 = PartitionKeyDefinition::from("/pk")
            .with_kind(PartitionKeyKind::Hash)
            .with_version(PartitionKeyVersion::V2);
        let hash_err = maybe_handle_feed_range_partition_key_special_case(
            &hash_v2,
            FeedRangePartitionKeySource::ExplicitEmptySequence,
        )
        .expect_err("hash container should reject explicit empty sequence");
        match hash_err {
            super::FeedRangeFromPartitionKeyError::LegacyAttribute(message) => {
                assert!(message.contains("'int' object has no attribute 'upper'"));
            }
            other => panic!("unexpected error: {other:?}"),
        }

        let multihash_v2 = PartitionKeyDefinition::new(vec!["/a".into(), "/b".into()])
            .with_kind(PartitionKeyKind::MultiHash)
            .with_version(PartitionKeyVersion::V2);
        let passthrough = maybe_handle_feed_range_partition_key_special_case(
            &multihash_v2,
            FeedRangePartitionKeySource::ExplicitEmptySequence,
        )
        .expect("multihash explicit empty sequence should not error");
        assert!(passthrough.is_none());
    }

    // ---- read_feed_ranges body parsing ----------------------------------------

    #[test]
    fn read_feed_ranges_body_defaults_to_no_refresh_when_empty() {
        assert!(
            !parse_read_feed_ranges_force_refresh(b"").expect("empty body should default to false")
        );
    }

    #[test]
    fn read_feed_ranges_body_accepts_boolean_force_refresh() {
        assert!(
            parse_read_feed_ranges_force_refresh(br#"{"forceRefresh":true}"#)
                .expect("true should parse")
        );
        assert!(
            !parse_read_feed_ranges_force_refresh(br#"{"forceRefresh":false}"#)
                .expect("false should parse")
        );
        assert!(!parse_read_feed_ranges_force_refresh(br#"{}"#)
            .expect("missing forceRefresh should default to false"));
    }

    #[test]
    fn read_feed_ranges_body_rejects_invalid_shape() {
        assert!(parse_read_feed_ranges_force_refresh(br#"{"forceRefresh":"yes"}"#).is_err());
        assert!(parse_read_feed_ranges_force_refresh(br#"{"forceRefresh":1}"#).is_err());
        assert!(parse_read_feed_ranges_force_refresh(br#"not json"#).is_err());
    }

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

    // ---- json_value_to_pk_component -------------------------------------------

    #[test]
    fn pk_component_maps_scalars_and_undefined() {
        for v in ["null", "true", "1.5", r#""s""#, "{}"] {
            let value: serde_json::Value = serde_json::from_str(v).unwrap();
            assert!(json_value_to_pk_component(value).is_ok(), "should map: {v}");
        }
    }

    #[test]
    fn pk_component_rejects_non_empty_object_and_array() {
        let obj: serde_json::Value = serde_json::from_str(r#"{"a":1}"#).unwrap();
        assert!(json_value_to_pk_component(obj).is_err());
        let arr: serde_json::Value = serde_json::from_str("[1,2]").unwrap();
        assert!(json_value_to_pk_component(arr).is_err());
    }

    #[test]
    fn pk_component_accepts_large_integer_as_finite_f64() {
        // A large-integer partition key (> 2^53) is converted via `as_f64()`,
        // which lossily rounds it but still returns a *finite* Some(_), so the
        // "non-finite number" guard does not reject it. This is correct, not a
        // bug: Cosmos hashes numeric partition keys as IEEE-754 doubles on both
        // the client and the server, so the same rounding happens server-side
        // and routing stays consistent. This test pins that behavior so a future
        // change to integer-PK handling (e.g. attempting exact i64 routing) is a
        // conscious, reviewed decision rather than a silent regression.
        let big: serde_json::Value = serde_json::from_str("9007199254740993").unwrap(); // 2^53 + 1
        assert!(big.is_i64(), "fixture must be an integer, not a float");
        assert!(
            json_value_to_pk_component(big).is_ok(),
            "large integer PK must map to a finite f64 component without error"
        );
    }

    // ---- intentionally-ignored option-key allowlist ---------------------------

    #[test]
    fn ignored_allowlist_covers_prep_internal_keys_only() {
        // Prep-internal flags that legitimately ride in the headers dict but are
        // NOT wire headers must be on the allowlist, so COSMOS_WIRE_STRICT does
        // not flag the expected silent drop as drift. Keys are compared lowered.
        assert!(is_intentionally_ignored_option_key(
            "disableautomaticidgeneration"
        ));
        assert!(is_intentionally_ignored_option_key("partitionkey"));
        // A would-be new wire knob (or any real wire-name key) must NOT be on the
        // allowlist, so strict mode can catch Python<->Rust drift on it.
        assert!(!is_intentionally_ignored_option_key("indexingdirective"));
        assert!(!is_intentionally_ignored_option_key("somenewknob"));
        assert!(!is_intentionally_ignored_option_key(
            "x-ms-cosmos-priority-level"
        ));
    }

    #[test]
    fn timeout_header_rejects_non_numeric_values() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let headers = PyDict::new_bound(py);
            headers
                .set_item("__overall_timeout_seconds", "not-a-number")
                .expect("header assignment must succeed");
            let result = extract_op_modifiers(&headers);
            match result {
                Ok(_) => panic!("non-numeric timeout must be rejected"),
                Err(err) => {
                    assert!(
                        err.to_string().contains("__overall_timeout_seconds"),
                        "unexpected error: {err}"
                    );
                }
            }
        });
    }

    #[test]
    fn parse_availability_strategy_maps_disabled_and_enabled() {
        // False -> "disabled" on the Python side -> Disabled here.
        assert_eq!(
            parse_availability_strategy("disabled"),
            Some(AvailabilityStrategy::Disabled)
        );
        // True -> "enabled:500" (the SDK default threshold).
        assert_eq!(
            parse_availability_strategy("enabled:500"),
            Some(AvailabilityStrategy::Hedging(HedgingStrategy::new(
                HedgeThreshold::new(Duration::from_millis(500)).unwrap()
            )))
        );
        // A dict with a custom threshold.
        assert_eq!(
            parse_availability_strategy("enabled:250"),
            Some(AvailabilityStrategy::Hedging(HedgingStrategy::new(
                HedgeThreshold::new(Duration::from_millis(250)).unwrap()
            )))
        );
    }

    #[test]
    fn parse_availability_strategy_falls_back_to_default_on_bad_threshold() {
        // A zero / unparseable threshold still enables hedging, using the default.
        let expected = Some(AvailabilityStrategy::Hedging(HedgingStrategy::new(
            HedgeThreshold::new(Duration::from_millis(DEFAULT_HEDGE_THRESHOLD_MS)).unwrap(),
        )));
        assert_eq!(parse_availability_strategy("enabled:0"), expected);
        assert_eq!(parse_availability_strategy("enabled"), expected);
        assert_eq!(parse_availability_strategy("enabled:notanumber"), expected);
        // An empty value means "not set".
        assert_eq!(parse_availability_strategy(""), None);
    }

    #[test]
    fn availability_strategy_header_lifts_to_typed_field() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let headers = PyDict::new_bound(py);
            headers
                .set_item("availabilityStrategy", "disabled")
                .expect("header assignment must succeed");
            let modifiers = extract_op_modifiers(&headers).expect("extraction must succeed");
            assert_eq!(
                modifiers.availability_strategy,
                Some(AvailabilityStrategy::Disabled)
            );
            // It must NOT leak into custom headers.
            assert!(modifiers.custom_headers.is_empty());
        });
    }

    #[test]
    fn initial_headers_forward_verbatim_including_non_x_ms() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let inner = PyDict::new_bound(py);
            inner.set_item("x-trace-id", "abc-123").unwrap();
            inner.set_item("x-ms-custom", "v1").unwrap();
            let headers = PyDict::new_bound(py);
            headers.set_item("initialHeaders", inner).unwrap();

            let modifiers = extract_op_modifiers(&headers).expect("extraction must succeed");
            // Both the non-x-ms customer header and the x-ms one are forwarded
            // verbatim; neither is dropped nor lifted to a typed field.
            assert_eq!(
                modifiers
                    .custom_headers
                    .get(&HeaderName::from("x-trace-id".to_string())),
                Some(&HeaderValue::from("abc-123".to_string()))
            );
            assert_eq!(
                modifiers
                    .custom_headers
                    .get(&HeaderName::from("x-ms-custom".to_string())),
                Some(&HeaderValue::from("v1".to_string()))
            );
        });
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
}

mod feed_range;
mod items;
mod offers;
mod query;

#[cfg(test)]
use feed_range::maybe_handle_feed_range_partition_key_special_case;
use feed_range::{
    FeedRangeFromPartitionKeyError, FeedRangeFromPartitionKeyPayload, FeedRangePartitionKeyInput,
    FeedRangePartitionKeySource,
};
use query::QueryTarget;

pub(crate) use feed_range::{
    run_feed_range_from_partition_key_operation, run_feed_range_from_partition_key_operation_async,
    run_is_feed_range_subset_operation, run_is_feed_range_subset_operation_async,
    run_read_feed_ranges_operation, run_read_feed_ranges_operation_async,
};
pub(crate) use items::{run_item_operation, run_item_operation_async};
pub(crate) use offers::{
    run_read_offer_operation, run_read_offer_operation_async, run_replace_offer_operation,
    run_replace_offer_operation_async,
};
pub(crate) use query::{
    run_query_operation, run_query_operation_async, run_read_all_items_operation,
    run_read_all_items_operation_async,
};

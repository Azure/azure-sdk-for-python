// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! The shared request/reply translation between Python and the driver: the
//! singleton-operation runner, the header-to-typed-field translation, the
//! `BackendResponse` 4-tuple builders, and the partition-key / container-link
//! parsers. Every family's operations route through here.

use std::collections::HashMap;
use std::sync::Arc;
use std::time::Duration;

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyTuple};

use azure_core::http::headers::{HeaderName, HeaderValue};
use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{
        ActivityId, CosmosOperation, CosmosResponse, ItemReference, PartitionKey,
        PartitionKeyValue, ResponseBody, SessionToken,
    },
    options::{
        ContentResponseOnWrite, EndToEndOperationLatencyPolicy, ExcludedRegions,
        OperationOptionsBuilder,
    },
};
use serde::Deserialize;

use crate::runtime::{drivers, require_runtime_context};

// ---------------------------------------------------------------------------
// Shared singleton-operation runner
// ---------------------------------------------------------------------------
//
// All five per-item ops (create / upsert / replace / delete / read) run the
// same steps: look up the driver, parse the container link and partition key,
// then on the Tokio runtime with the GIL released resolve the container, build
// the operation, apply the activity-id / session-token headers, run it, and
// turn the CosmosResponse (or a CosmosError that carries a wire response) into
// the BackendResponse 4-tuple. Only three things vary per op, so each entry
// point passes them in: the item id, whether no_response applies (writes only),
// and a closure that builds the operation from the resolved ItemReference.

pub(crate) fn run_item_operation<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
    partition_key_header: &str,
    modifiers: OpModifiers,
    item_id: String,
    op_name: &str,
    honor_content_response: bool,
    build_op: impl FnOnce(ItemReference) -> CosmosOperation + Send,
) -> PyResult<Bound<'py, PyTuple>> {
    let driver = lookup_driver(handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let partition_key = parse_partition_key_header(partition_key_header)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    // Sync path: block the calling thread on the shared runtime until the driver
    // finishes. (The async sibling below spawns the very same future instead, so
    // both paths run identical driver work.)
    let response_result: Result<CosmosResponse, CosmosError> = py.allow_threads(|| {
        runtime_ctx.tokio_rt.block_on(run_singleton_future(
            driver,
            database_name,
            container_name,
            partition_key,
            item_id,
            modifiers,
            honor_content_response,
            build_op,
        ))
    });

    tuple_from_result(py, response_result)
}

/// Async sibling of `run_item_operation`: same inputs and identical driver work,
/// but instead of blocking a worker thread it spawns the driver future on the
/// shared runtime (the same one the driver was built on, so its connection pool
/// and timers stay on that runtime) and hands the asyncio event loop an awaitable
/// that resolves to the `BackendResponse` 4-tuple. Awaiting it uses no Python
/// thread per in-flight call.
/// Aborts the spawned driver task if this guard is dropped before the task has
/// finished. The bridged Python awaitable owns one of these; when asyncio cancels
/// the `await` (for example a client-side timeout, or the surrounding task being
/// cancelled) `pyo3-async-runtimes` drops the bridging future, which drops this
/// guard, which aborts the Tokio task -- so the in-flight driver operation is
/// actually cancelled (its connection released, no further work or RU spent)
/// instead of being detached and left to run to completion with its result thrown
/// away. On normal completion the task is already finished, so `abort()` is a
/// harmless no-op.
struct AbortOnDrop(tokio::task::AbortHandle);

impl Drop for AbortOnDrop {
    fn drop(&mut self) {
        self.0.abort();
    }
}

pub(crate) fn run_item_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
    partition_key_header: &str,
    modifiers: OpModifiers,
    item_id: String,
    op_name: &str,
    honor_content_response: bool,
    build_op: impl FnOnce(ItemReference) -> CosmosOperation + Send + 'static,
) -> PyResult<Bound<'py, PyAny>> {
    // Synchronous extraction (GIL held) -- identical to the sync path. Errors
    // here surface when the coroutine is created, before it is awaited.
    let driver = lookup_driver(handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let partition_key = parse_partition_key_header(partition_key_header)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    // Spawn the driver work on the shared runtime; `join` is a cheap handle the
    // bridge below awaits without holding the GIL or pinning a worker thread.
    let join = runtime_ctx.tokio_rt.spawn(run_singleton_future(
        driver,
        database_name,
        container_name,
        partition_key,
        item_id,
        modifiers,
        honor_content_response,
        build_op,
    ));

    // Propagate Python-side cancellation to the driver. Without this, cancelling
    // the awaitable would only drop the JoinHandle -- which *detaches* the Tokio
    // task, letting the operation run to completion in the background (holding a
    // connection, spending RU) with its result discarded. Holding this guard for
    // the lifetime of the bridging future means a cancelled `await` drops the
    // guard and aborts the task instead, so a client-side timeout actually stops
    // the work.
    let abort_guard = AbortOnDrop(join.abort_handle());

    // Bridge the Rust JoinHandle to a Python asyncio awaitable. The response
    // tuple is built under the GIL after the future resolves, exactly like the
    // sync path's `tuple_from_result`.
    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        // Keep the abort guard alive for exactly as long as we await the task; if
        // the Python future is cancelled, this block is dropped, dropping the
        // guard and aborting the task (see AbortOnDrop).
        let _abort_guard = abort_guard;
        let response_result = join.await.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err(
                    "cosmos async operation was cancelled before it completed",
                )
            } else {
                PyRuntimeError::new_err(format!(
                    "cosmos async operation task failed: {join_error}"
                ))
            }
        })?;
        Python::with_gil(|py| {
            tuple_from_result(py, response_result).map(|tuple| tuple.into_any().unbind())
        })
    })
}

/// Look up the cached driver for a client handle, or raise if `init_client`
/// has not run yet (or the client was already closed).
fn lookup_driver(handle: &str) -> PyResult<Arc<CosmosDriver>> {
    drivers()
        .read()
        .unwrap()
        .get(handle)
        .map(|entry| Arc::clone(&entry.driver))
        .ok_or_else(|| {
            PyRuntimeError::new_err(format!(
                "no driver registered for handle {handle:?}; call init_client first"
            ))
        })
}

/// The driver work shared by the sync and async runners: resolve the container,
/// build the operation from the per-op closure, apply the typed activity-id /
/// session-token / content-response / options, and execute it. Returns the raw
/// driver result; the callers turn it into the Python tuple under the GIL.
async fn run_singleton_future(
    driver: Arc<CosmosDriver>,
    database_name: String,
    container_name: String,
    partition_key: PartitionKey,
    item_id: String,
    modifiers: OpModifiers,
    honor_content_response: bool,
    build_op: impl FnOnce(ItemReference) -> CosmosOperation + Send,
) -> Result<CosmosResponse, CosmosError> {
    let container = driver
        .resolve_container(&database_name, &container_name)
        .await?;
    let item_ref = ItemReference::from_name(&container, partition_key, item_id);
    let mut op = build_op(item_ref);

    if let Some(activity) = modifiers.activity_header.as_ref() {
        if let Ok(uuid) = activity.parse::<uuid::Uuid>() {
            op = op.with_activity_id(ActivityId::from(uuid.to_string()));
        }
    }
    if let Some(session) = modifiers.session_header.as_ref() {
        op = op.with_session_token(SessionToken::from(session.clone()));
    }

    // no_response=True only applies to writes; delete / read pass
    // honor_content_response=false and keep the driver default.
    let content_response = if honor_content_response {
        Some(modifiers.content_response_on_write)
    } else {
        None
    };
    let options = build_operation_options(
        content_response,
        modifiers.excluded_regions_value,
        modifiers.end_to_end_timeout,
        modifiers.custom_headers,
    );

    driver.execute_singleton_operation(op, options).await
}

/// Turn the driver's `Result<CosmosResponse, CosmosError>` into the
/// `BackendResponse` 4-tuple. A CosmosError carrying a wire response (404 / 409
/// / 412 / ...) becomes the same 4-tuple as success so the Python parser raises
/// the right typed exception; only a response-less error (transport failure,
/// client-side validation) becomes a RuntimeError.
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
                Err(PyRuntimeError::new_err(format!(
                    "driver execute_singleton_operation failed: {cosmos_error}"
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
    custom_headers: HashMap<HeaderName, HeaderValue>,
}

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
            content_response_on_write = if value.is_truthy().unwrap_or(false) {
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
            if let Ok(seconds) = value.extract::<f64>() {
                if seconds.is_finite() && seconds > 0.0 {
                    end_to_end_timeout = Some(EndToEndOperationLatencyPolicy::new(
                        Duration::from_secs_f64(seconds),
                    ));
                }
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
            _ => continue,
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
    if !custom_headers.is_empty() {
        builder = builder.with_custom_headers(custom_headers);
    }
    builder.build()
}

fn backend_response_tuple<'py>(
    py: Python<'py>,
    status_code: i64,
    sub_status: i64,
    response_headers: Bound<'py, PyDict>,
    body: &[u8],
) -> PyResult<Bound<'py, PyTuple>> {
    let body_py = PyBytes::new_bound(py, body);
    let items: Vec<PyObject> = vec![
        status_code.into_py(py),
        sub_status.into_py(py),
        response_headers.into_any().unbind(),
        body_py.into_any().unbind(),
    ];
    Ok(PyTuple::new_bound(py, &items))
}

fn backend_response_tuple_from_success<'py>(
    py: Python<'py>,
    response: azure_data_cosmos_driver::models::CosmosResponse,
) -> PyResult<Bound<'py, PyTuple>> {
    let status = response.status();
    let status_code = u16::from(status.status_code()) as i64;
    // SubStatusCode wraps a u16; use ``.value()`` to read it.
    let sub_status = status.sub_status().map(|s| s.value() as i64).unwrap_or(0);

    // Copy the driver's typed CosmosResponseHeaders fields into a Python
    // dict keyed by the actual `x-ms-...` wire-header names. This is what
    // the Python parser (`_helpers/_response_parse.py`) reads to populate
    // `client_connection.last_response_headers`, so customer code that
    // does e.g. `last_response_headers["etag"]` keeps working on the
    // Rust path.
    let driver_headers = response.headers();
    let response_headers = PyDict::new_bound(py);
    write_response_headers(&response_headers, driver_headers)?;

    let body_vec = response_body_to_vec(response.into_body());
    backend_response_tuple(py, status_code, sub_status, response_headers, &body_vec)
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
fn response_body_to_vec(body: ResponseBody) -> Vec<u8> {
    match body {
        ResponseBody::NoPayload => Vec::new(),
        ResponseBody::Bytes(b) => b.to_vec(),
        ResponseBody::Items(items) => items.iter().flat_map(|b| b.iter().copied()).collect(),
    }
}

/// Build a `BackendResponse` 4-tuple from a driver `CosmosError` that
/// carries a wire response.
///
/// Returns `Ok(None)` when the error has no wire response (transport
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

    let response_headers = PyDict::new_bound(py);
    write_response_headers(&response_headers, response.headers())?;

    let body_vec = response_body_to_vec(response.body().clone());
    Ok(Some(backend_response_tuple(
        py,
        status_code,
        sub_status,
        response_headers,
        &body_vec,
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


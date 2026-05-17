// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! PyO3 binding crate that exposes `azure_data_cosmos_driver` to Python.
//!
//! Compiled into one cdylib that Maturin renames to
//! `_rust.{pyd,so}` and drops into `azure/cosmos/`. The
//! driver crate is statically linked into the same binary so the
//! wheel ships exactly one Rust file.
//!
//! Two Python-callable entry points:
//!
//!   * `init_client(endpoint, master_key) -> handle`
//!         Lazily stands up a per-process Tokio runtime + driver
//!         runtime, builds a `CosmosDriver` for the given endpoint,
//!         and returns a string handle the Python side keeps and
//!         passes back on every operation.
//!
//!   * `create_item(handle, prepared) -> (status, sub_status,
//!                                         headers, body)`
//!         Resolves the container, builds a typed
//!         `CosmosOperation::create_item`, runs it on the Tokio
//!         runtime with the GIL released, and converts the
//!         `CosmosResponse` into a 4-tuple matching the Python
//!         `BackendResponse` dataclass.
//!
//! `x-ms-activity-id` and `x-ms-session-token` are forwarded to the
//! driver's typed operation fields. `responsePayloadOnWriteDisabled`
//! is lifted to the typed `OperationOptions::content_response_on_write`
//! field. Every other per-request header (intended-collection-rid,
//! indexing directive, pre/post triggers, priority, throughput bucket,
//! plus any already-`x-ms-...`-named entry) is pushed through the
//! driver's `OperationOptions::with_custom_headers` escape hatch so
//! it lands on the wire.

use std::collections::HashMap;
use std::sync::{Arc, OnceLock, RwLock};
use std::time::Duration;

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyTuple};

use azure_core::http::headers::{HeaderName, HeaderValue};
use azure_data_cosmos_driver::{
    driver::{CosmosDriver, CosmosDriverRuntime},
    models::{
        AccountReference, ActivityId, CosmosOperation, ItemReference, PartitionKey,
        PartitionKeyValue, SessionToken,
    },
    options::{ContentResponseOnWrite, EndToEndOperationLatencyPolicy, ExcludedRegions, OperationOptionsBuilder},
};
use tokio::runtime::Runtime as TokioRuntime;
use url::Url;

// ---------------------------------------------------------------------------
// Per-process singletons
// ---------------------------------------------------------------------------
//
// One Tokio runtime, one CosmosDriverRuntime, and a per-endpoint cache of
// CosmosDrivers. All three are lazily initialised on the first init_client
// call and live for the lifetime of the Python process.

static TOKIO_RUNTIME: OnceLock<TokioRuntime> = OnceLock::new();
// `Arc<...>` because the external driver's `get_or_create_driver` takes
// `self: &Arc<Self>`, and `CosmosDriverRuntimeBuilder::build()` returns an
// `Arc<CosmosDriverRuntime>` directly.
static DRIVER_RUNTIME: OnceLock<Arc<CosmosDriverRuntime>> = OnceLock::new();
static DRIVERS: OnceLock<RwLock<HashMap<String, Arc<CosmosDriver>>>> = OnceLock::new();

fn drivers() -> &'static RwLock<HashMap<String, Arc<CosmosDriver>>> {
    DRIVERS.get_or_init(|| RwLock::new(HashMap::new()))
}

// ---------------------------------------------------------------------------
// Module entry point
// ---------------------------------------------------------------------------

#[pymodule]
fn _rust(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(init_client, m)?)?;
    m.add_function(wrap_pyfunction!(create_item, m)?)?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}

// ---------------------------------------------------------------------------
// init_client
// ---------------------------------------------------------------------------
//
// Idempotent: subsequent calls with the same endpoint return the same
// handle without rebuilding the driver. Subsequent calls with a different
// endpoint construct a new driver against the shared runtime.

#[pyfunction]
fn init_client(py: Python<'_>, endpoint: &str, master_key: &str) -> PyResult<String> {
    let endpoint_url = Url::parse(endpoint)
        .map_err(|e| PyValueError::new_err(format!("invalid endpoint URL: {e}")))?;
    // Promote the borrowed master_key to an owned String so the
    // AccountReference (which keeps a Cow<'static, str>) can hold it.
    let master_key_owned: String = master_key.to_string();

    // First call only: stand up Tokio + the driver runtime. Both are async to
    // build, so we block_on on a temporary handle. After both OnceLocks fill,
    // every later call skips this whole block.
    if TOKIO_RUNTIME.get().is_none() {
        let tokio_rt = TokioRuntime::new().map_err(|e| {
            PyRuntimeError::new_err(format!("failed to start tokio runtime: {e}"))
        })?;
        let built_driver_runtime = tokio_rt
            .block_on(async { CosmosDriverRuntime::builder().build().await })
            .map_err(|e| PyRuntimeError::new_err(format!("driver runtime build failed: {e}")))?;
        // OnceLock::set returns Err if another thread won the race; in that
        // case our local values are dropped and the winner's values stay.
        let _ = TOKIO_RUNTIME.set(tokio_rt);
        let _ = DRIVER_RUNTIME.set(built_driver_runtime);
    }

    let tokio_rt = TOKIO_RUNTIME
        .get()
        .expect("TOKIO_RUNTIME populated above");
    let driver_runtime = DRIVER_RUNTIME
        .get()
        .expect("DRIVER_RUNTIME populated above");

    let handle = endpoint.to_string();

    // Fast path: read lock; if the driver is already cached we are done.
    if drivers().read().unwrap().contains_key(&handle) {
        return Ok(handle);
    }

    // Slow path: build the driver. Held without any of our locks because
    // get_or_create_driver is async and may take seconds.
    let account = AccountReference::with_master_key(endpoint_url, master_key_owned);
    let driver = py
        .allow_threads(|| tokio_rt.block_on(driver_runtime.get_or_create_driver(account, None)))
        .map_err(|e| PyRuntimeError::new_err(format!("driver init failed: {e}")))?;

    // Insert under write lock. If two threads raced we keep whichever
    // landed first; both end up with the same logical driver because the
    // runtime itself caches by endpoint internally.
    drivers()
        .write()
        .unwrap()
        .entry(handle.clone())
        .or_insert(driver);

    Ok(handle)
}

// ---------------------------------------------------------------------------
// create_item
// ---------------------------------------------------------------------------
//
// Inputs:
//   handle    : the string returned by init_client.
//   prepared  : a Python PreparedRequest dataclass instance with fields
//               container_link        : str, e.g. "dbs/<db>/colls/<coll>"
//               body_bytes            : bytes (already JSON-serialised)
//               partition_key_header  : str, e.g. '["customerA"]'
//               headers               : dict[str, str]
//
// Output: 4-tuple (status_code, sub_status, headers_dict, body_bytes)
// matching the Python BackendResponse dataclass.

#[pyfunction]
fn create_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let container_link: String = prepared.getattr("container_link")?.extract()?;
    let body_bytes: Vec<u8> = prepared.getattr("body_bytes")?.extract()?;
    let partition_key_header: String =
        prepared.getattr("partition_key_header")?.extract()?;
    let headers_obj = prepared.getattr("headers")?;
    let headers_dict: &Bound<'py, PyDict> = headers_obj.downcast::<PyDict>()?;

    let mut activity_header: Option<String> = None;
    let mut session_header: Option<String> = None;
    // The Python helper writes the *internal option-key name*
    // ``responsePayloadOnWriteDisabled`` into PreparedRequest.headers
    // when the customer passed ``no_response=True``. The driver's
    // ``OperationOptions::content_response_on_write`` defaults to
    // ``Disabled`` ("suppresses the body to reduce bandwidth"); to
    // make a successful create return the created item the binding
    // must explicitly map ``no_response`` → ``Enabled`` / ``Disabled``
    // here. ``None`` (kwarg never set) is treated as the customer
    // wanting the body, so we default to Enabled.
    let mut content_response_on_write: ContentResponseOnWrite =
        ContentResponseOnWrite::Enabled;
    // ``excluded_locations`` (Python kwarg) → driver
    // ``OperationOptions::excluded_regions``. The Python helper writes
    // the kwarg into ``PreparedRequest.headers`` under the internal
    // option-key name ``excludedLocations`` (see
    // ``_helpers/_options.COMMON_OPTIONS``) with the *raw value* — a
    // ``Sequence[str]`` of region display names like
    // ``["East US", "West US 2"]``. The driver models this as a typed
    // field (``ExcludedRegions(Vec<Region>)``) and ``Region`` is
    // case/whitespace-normalising via its ``From<String>`` impl, so we
    // hand the strings straight in. ``None`` here means "kwarg never
    // set" and the driver inherits from a lower-priority layer
    // (account/runtime/env) per the layered-options model.
    let mut excluded_regions_value: Option<ExcludedRegions> = None;
    // ``timeout`` (Python kwarg, seconds) → driver
    // ``OperationOptions::end_to_end_latency_policy``. The Python
    // helper writes the value under the sentinel header name
    // ``__overall_timeout_seconds`` (see
    // ``_constants._Constants.OVERALL_TIMEOUT_SECONDS``). The legacy
    // core-Python path consumes ``timeout`` via the azure-core
    // pipeline; the rust path bypasses that pipeline entirely, so the
    // binding lifts the value into the driver's typed end-to-end
    // latency policy here. Sub-second values are clamped by the
    // driver to its 1-second minimum (see
    // ``EndToEndOperationLatencyPolicy::new``); ``None`` means
    // "kwarg never set" and the driver inherits from a lower layer.
    let mut end_to_end_timeout: Option<EndToEndOperationLatencyPolicy> = None;
    // Custom headers the binding pushes through the driver's
    // ``OperationOptions::with_custom_headers`` escape hatch. Used for
    // every per-request header that the driver does not yet model as
    // a typed field of its own (intended-collection-rid, indexing
    // directive, pre/post triggers, priority, throughput bucket).
    let mut custom_headers: HashMap<HeaderName, HeaderValue> = HashMap::new();
    for (key, value) in headers_dict.iter() {
        let key_str: String = key.extract()?;
        let lower = key_str.to_ascii_lowercase();
        // Headers the driver already exposes as typed fields on the
        // operation itself — handled out of band, not via custom_headers.
        if lower == "x-ms-activity-id" {
            activity_header = Some(value.extract()?);
            continue;
        }
        // Accept both the wire-name (`x-ms-session-token`) and the Python
        // helper's camelCase option-key (`sessionToken`, produced by
        // `_options.COMMON_OPTIONS` when the customer passes
        // `session_token=`). The legacy core-Python path translates the
        // option-key to the wire header via `_base.GetHeaders`; the Rust
        // path does the same translation here so the kwarg is not
        // silently lost on the way to the driver.
        if lower == "x-ms-session-token" || lower == "sessiontoken" {
            session_header = Some(value.extract()?);
            continue;
        }
        // ``no_response`` lifted to the typed options field (see above).
        if lower == "responsepayloadonwritedisabled" {
            // Truthy → caller asked for "no body"; falsy → caller
            // explicitly asked for the body (today indistinguishable
            // from omission). ``bool`` lift via PyAny.is_truthy().
            content_response_on_write = if value.is_truthy().unwrap_or(false) {
                ContentResponseOnWrite::Disabled
            } else {
                ContentResponseOnWrite::Enabled
            };
            continue;
        }
        // ``excludedLocations`` (option-key form of the ``excluded_locations``
        // kwarg) → typed ``ExcludedRegions`` on the driver. We accept any
        // Python iterable of strings (the Python type is
        // ``Sequence[str]``); each element is fed through ``Region::from``
        // (case- and whitespace-normalising). Stripped from custom-headers
        // because the driver does not want it on the wire as a header.
        if lower == "excludedlocations" {
            let regions: Vec<String> = value.extract().map_err(|e| {
                PyValueError::new_err(format!(
                    "excluded_locations must be a sequence of region name strings: {e}"
                ))
            })?;
            excluded_regions_value =
                Some(regions.into_iter().collect::<ExcludedRegions>());
            continue;
        }
        // Sentinel header carrying the customer's ``timeout`` kwarg
        // (overall operation timeout, seconds). Accepts int or float;
        // negative / zero / non-finite values are ignored (treated
        // as "kwarg never set") rather than surfaced as an error
        // because the legacy path silently ignores them too.
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
        // Everything else: translate the Python helper's option-key
        // name (or accept an already-wire-name string) to the
        // ``x-ms-...`` header the service expects, then push onto the
        // custom-headers map. Unknown keys are skipped silently — the
        // legacy ``_base.GetHeaders`` mapping table also drops keys
        // it does not recognise, so the rust path matches that
        // behaviour rather than 500ing on a stray option.
        let wire_name: Option<&'static str> = match lower.as_str() {
            "pretriggerinclude" => Some("x-ms-documentdb-pre-trigger-include"),
            "posttriggerinclude" => Some("x-ms-documentdb-post-trigger-include"),
            "indexingdirective" => Some("x-ms-indexing-directive"),
            "prioritylevel" => Some("x-ms-cosmos-priority-level"),
            "throughputbucket" => Some("x-ms-cosmos-throughput-bucket"),
            "containerrid" => Some("x-ms-cosmos-intended-collection-rid"),
            // Already a wire-name header (e.g. caller-supplied
            // initial_headers, or a future site that writes the
            // x-ms-... name directly). Forward as-is. We exclude the
            // two typed-field names handled above.
            other if other.starts_with("x-ms-") || other == "prefer" => None,
            _ => continue,
        };
        // Stringify the value. Python may have written a non-str
        // (e.g. an int for indexing_directive); we coerce via str()
        // to match what the legacy path emits on the wire.
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

    let driver = drivers()
        .read()
        .unwrap()
        .get(handle)
        .cloned()
        .ok_or_else(|| {
            PyRuntimeError::new_err(format!(
                "no driver registered for handle {handle:?}; call init_client first"
            ))
        })?;

    let (database_name, container_name) = parse_container_link(&container_link)?;
    let partition_key = parse_partition_key_header(&partition_key_header)?;
    let item_id = extract_item_id(&body_bytes)?;

    let tokio_rt = TOKIO_RUNTIME.get().ok_or_else(|| {
        PyRuntimeError::new_err("init_client must be called before create_item")
    })?;

    let response_result: azure_core::Result<_> = py.allow_threads(|| {
        tokio_rt.block_on(async {
            let container = driver
                .resolve_container(&database_name, &container_name)
                .await?;
            let item_ref =
                ItemReference::from_name(&container, partition_key, item_id);
            let mut op = CosmosOperation::create_item(item_ref).with_body(body_bytes);

            if let Some(activity) = activity_header {
                if let Ok(uuid) = activity.parse::<uuid::Uuid>() {
                    op = op.with_activity_id(ActivityId::from(uuid.to_string()));
                }
            }
            if let Some(session) = session_header {
                op = op.with_session_token(SessionToken::from(session));
            }

            // Build OperationOptions with the field(s) the binding maps
            // from the Python side:
            //   * ``content_response_on_write`` — from ``no_response``.
            //   * ``custom_headers`` — every per-request header the
            //     driver does not yet model as a typed field of its own
            //     (intended-collection-rid, indexing directive,
            //     pre/post triggers, priority, throughput bucket; plus
            //     any caller-supplied ``x-ms-...`` / ``prefer`` key
            //     that flowed through PreparedRequest.headers).
            // Other fields stay ``None`` and the driver fills them
            // from account / runtime / env defaults (the layered-
            // options model — see ``OperationOptions`` doc).
            let mut builder = OperationOptionsBuilder::new()
                .with_content_response_on_write(content_response_on_write);
            if let Some(regions) = excluded_regions_value {
                builder = builder.with_excluded_regions(regions);
            }
            if let Some(policy) = end_to_end_timeout {
                builder = builder.with_end_to_end_latency_policy(policy);
            }
            if !custom_headers.is_empty() {
                builder = builder.with_custom_headers(custom_headers);
            }
            let options = builder.build();

            driver.execute_operation(op, options).await
        })
    });

    let response = response_result.map_err(|e| {
        PyRuntimeError::new_err(format!("driver execute_operation failed: {e}"))
    })?;

    let status = response.status();
    let status_code = u16::from(status.status_code()) as i64;
    let sub_status = status.sub_status().map(u32::from).unwrap_or(0) as i64;

    // Copy the driver's typed CosmosResponseHeaders fields into a Python
    // dict keyed by the actual `x-ms-...` wire-header names. This is what
    // the Python parser (`_helpers/_response_parse.py`) reads to populate
    // `client_connection.last_response_headers`, so customer code that
    // does e.g. `last_response_headers["etag"]` keeps working on the
    // Rust path.
    let driver_headers = response.headers();
    let response_headers = PyDict::new_bound(py);
    write_response_headers(&response_headers, driver_headers)?;

    let body_vec = response.into_body();
    let body_py = PyBytes::new_bound(py, &body_vec);

    let items: Vec<PyObject> = vec![
        status_code.into_py(py),
        sub_status.into_py(py),
        response_headers.into_any().unbind(),
        body_py.into_any().unbind(),
    ];
    Ok(PyTuple::new_bound(py, &items))
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
        out.set_item("etag", v.as_str())?;
    }
    if let Some(v) = h.continuation.as_ref() {
        out.set_item("x-ms-continuation", v.as_str())?;
    }
    if let Some(v) = h.item_count {
        out.set_item("x-ms-item-count", v)?;
    }
    if let Some(v) = h.substatus {
        out.set_item("x-ms-substatus", u32::from(v))?;
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
    // Additional modeled fields the driver populates that the legacy
    // core-Python path also surfaces in ``last_response_headers``.
    // Customer-visible categories:
    //   * routing diagnostics: partition-key-range id, internal
    //     partition id;
    //   * capacity dashboards: resource-quota, resource-usage;
    //   * service-version reporting: gatewayversion, serviceversion;
    //   * script + write semantics: log-results,
    //     allow-tentative-writes;
    //   * indexing progress: collection-index-transformation-progress,
    //     collection-lazy-indexing-progress.
    // Two more fields (``x-ms-alt-content-path``, ``x-ms-content-path``)
    // are still ``pub(crate)`` on the driver's ``CosmosResponseHeaders``
    // (``owner_full_name``, ``owner_id``) and surface here once the
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
fn parse_container_link(link: &str) -> PyResult<(String, String)> {
    let parts: Vec<&str> = link.split('/').collect();
    if parts.len() == 4 && parts[0] == "dbs" && parts[2] == "colls" {
        Ok((parts[1].to_string(), parts[3].to_string()))
    } else {
        Err(PyValueError::new_err(format!(
            "container_link must be 'dbs/<db>/colls/<coll>', got {link:?}"
        )))
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
        // JSON null -> typed Null. Goes through the `From<Option<T>>` impl
        // which maps None -> InnerPartitionKeyValue::Null.
        serde_json::Value::Null => Ok(PartitionKeyValue::from(None::<String>)),
        serde_json::Value::Bool(b) => Ok(PartitionKeyValue::from(b)),
        serde_json::Value::Number(n) => match n.as_f64() {
            Some(f) => Ok(PartitionKeyValue::from(f)),
            None => Err(PyValueError::new_err(format!(
                "non-finite number in partition key header: {n}"
            ))),
        },
        serde_json::Value::String(s) => Ok(PartitionKeyValue::from(s)),
        // Empty JSON object `{}` is the wire shape for "PK path missing on
        // this document" (Python's `_Undefined`). The driver has a dedicated
        // representation for this.
        serde_json::Value::Object(obj) if obj.is_empty() => Ok(PartitionKeyValue::undefined()),
        // Anything else is not a valid partition-key component on the wire.
        other => Err(PyValueError::new_err(format!(
            "unsupported partition key value: {other}"
        ))),
    }
}

/// Read the document `id` out of a JSON body. The Python helper layer
/// guarantees it is present; we fail loudly if it is not, rather than
/// silently minting one here.
fn extract_item_id(body: &[u8]) -> PyResult<String> {
    let value: serde_json::Value = serde_json::from_slice(body)
        .map_err(|e| PyValueError::new_err(format!("body is not valid JSON: {e}")))?;
    value
        .get("id")
        .and_then(|v| v.as_str())
        .map(|s| s.to_string())
        .ok_or_else(|| PyValueError::new_err("body has no string `id` field"))
}


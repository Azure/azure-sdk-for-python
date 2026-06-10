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
//!   * `upsert_item(handle, prepared) -> (status, sub_status,
//!                                         headers, body)`
//!         Same input/output shape as `create_item` (write-with-body:
//!         the document id rides inside `body_bytes`). The only
//!         difference is the operation kind —
//!         `CosmosOperation::upsert_item` — which makes the driver
//!         pipeline stamp `x-ms-documentdb-is-upsert: true` and POST to
//!         the collection feed, so an existing `(partition_key, id)` is
//!         replaced (HTTP 200) rather than rejected with 409; a new id
//!         inserts (HTTP 201). `If-Match` / `If-None-Match` (built by
//!         the Python helper from `etag` + `match_condition`:
//!         insert-only or version-guarded replace) flow through
//!         `custom_headers`.
//!
//!   * `delete_item(handle, prepared) -> (status, sub_status,
//!                                         headers, body)`
//!         Same shape as `create_item` but builds a
//!         `CosmosOperation::delete_item` with no body. The document
//!         id rides on `PreparedRequest.item_id` because there is no
//!         body to extract it from. On success the driver returns
//!         HTTP 204 with an empty body.
//!
//!   * `read_item(handle, prepared) -> (status, sub_status,
//!                                       headers, body)`
//!         Same input shape as `delete_item` (bodiless GET, document
//!         id on `PreparedRequest.item_id`). On success returns HTTP
//!         200 with the document JSON. Conditional reads
//!         (`If-None-Match` driven by Python's `etag` +
//!         `MatchConditions.IfModified`) surface as **HTTP 304** with
//!         an empty body when the customer's cached etag still
//!         matches the server version — the Python parser treats 304
//!         as a non-error and returns an empty `CosmosDict`.
//!         `x-ms-dedicatedgateway-max-age` (driven by
//!         `max_integrated_cache_staleness_in_ms`) is forwarded
//!         through `custom_headers` like any other per-request header.
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
    error::CosmosError,
    models::{
        AccountReference, ActivityId, CosmosOperation, CosmosResponse, ItemReference,
        PartitionKey, PartitionKeyValue, ResponseBody, SessionToken,
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
    m.add_function(wrap_pyfunction!(upsert_item, m)?)?;
    m.add_function(wrap_pyfunction!(delete_item, m)?)?;
    m.add_function(wrap_pyfunction!(read_item, m)?)?;
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

    let modifiers = extract_op_modifiers(headers_dict)?;

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

    let response_result: Result<CosmosResponse, CosmosError> = py.allow_threads(|| {
        tokio_rt.block_on(async {
            let container = driver
                .resolve_container(&database_name, &container_name)
                .await?;
            let item_ref =
                ItemReference::from_name(&container, partition_key, item_id);
            let mut op = CosmosOperation::create_item(item_ref).with_body(body_bytes);

            if let Some(activity) = modifiers.activity_header.as_ref() {
                if let Ok(uuid) = activity.parse::<uuid::Uuid>() {
                    op = op.with_activity_id(ActivityId::from(uuid.to_string()));
                }
            }
            if let Some(session) = modifiers.session_header.as_ref() {
                op = op.with_session_token(SessionToken::from(session.clone()));
            }

            // Build OperationOptions from the typed fields the
            // binding lifted off the headers dict. Anything left as
            // ``None`` falls back to the driver's default.
            let options = build_operation_options(
                Some(modifiers.content_response_on_write),
                modifiers.excluded_regions_value,
                modifiers.end_to_end_timeout,
                modifiers.custom_headers,
            );

            driver.execute_singleton_operation(op, options).await
        })
    });

    match response_result {
        // Body may legitimately be empty when ``no_response=True``;
        // response_body_to_vec maps NoPayload to an empty Vec for the
        // Python parser.
        Ok(response) => backend_response_tuple_from_success(py, response),
        Err(cosmos_error) => {
            // The driver carries the wire response on its typed
            // CosmosError; extract status, headers, and body directly.
            // Synthetic errors (transport failures, client validation)
            // have no wire response and fall through to a generic
            // RuntimeError.
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
// upsert_item
// ---------------------------------------------------------------------------
//
// Same input/output shape as create_item (write-with-body: the document id
// rides inside body_bytes, the partition key is parsed from the header). The
// only difference is the operation kind: CosmosOperation::upsert_item instead
// of create_item. The driver pipeline owns the upsert semantics from there --
// it stamps `x-ms-documentdb-is-upsert: true` and POSTs to the collection
// feed -- so an existing (partition_key, id) is replaced (HTTP 200) rather
// than rejected with 409, and a new id inserts (HTTP 201). Like create,
// upsert returns the saved document unless `no_response=True`, so
// content_response_on_write is honoured. `If-Match` / `If-None-Match` (built
// by the Python helper from etag + match_condition: insert-only or
// version-guarded replace) flow through custom_headers like any other
// per-request header.

#[pyfunction]
fn upsert_item<'py>(
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

    let modifiers = extract_op_modifiers(headers_dict)?;

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
        PyRuntimeError::new_err("init_client must be called before upsert_item")
    })?;

    let response_result: Result<CosmosResponse, CosmosError> = py.allow_threads(|| {
        tokio_rt.block_on(async {
            let container = driver
                .resolve_container(&database_name, &container_name)
                .await?;
            let item_ref =
                ItemReference::from_name(&container, partition_key, item_id);
            // The single difference from create_item: upsert_item makes
            // the driver stamp is-upsert and POST to the collection feed.
            let mut op = CosmosOperation::upsert_item(item_ref).with_body(body_bytes);

            if let Some(activity) = modifiers.activity_header.as_ref() {
                if let Ok(uuid) = activity.parse::<uuid::Uuid>() {
                    op = op.with_activity_id(ActivityId::from(uuid.to_string()));
                }
            }
            if let Some(session) = modifiers.session_header.as_ref() {
                op = op.with_session_token(SessionToken::from(session.clone()));
            }

            // Upsert returns the saved document unless no_response=True,
            // exactly like create, so honour content_response_on_write.
            let options = build_operation_options(
                Some(modifiers.content_response_on_write),
                modifiers.excluded_regions_value,
                modifiers.end_to_end_timeout,
                modifiers.custom_headers,
            );

            driver.execute_singleton_operation(op, options).await
        })
    });

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
// delete_item
// ---------------------------------------------------------------------------
//
// Same input/output shape as create_item, but:
//   * no request body (the wire DELETE is bodiless);
//   * the document id comes from PreparedRequest.item_id, not the body;
//   * content_response_on_write is left at the driver default — DELETE
//     has no body to suppress, and the driver auto-injects
//     `Prefer: return=minimal` for non-read ops anyway;
//   * If-Match / If-None-Match conditional headers (built by the Python
//     helper from etag + match_condition) flow through custom_headers.

#[pyfunction]
fn delete_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let container_link: String = prepared.getattr("container_link")?.extract()?;
    let partition_key_header: String =
        prepared.getattr("partition_key_header")?.extract()?;
    let item_id: String = prepared
        .getattr("item_id")?
        .extract::<Option<String>>()?
        .ok_or_else(|| {
            PyValueError::new_err(
                "delete_item: PreparedRequest.item_id is required for delete operations",
            )
        })?;
    let headers_obj = prepared.getattr("headers")?;
    let headers_dict: &Bound<'py, PyDict> = headers_obj.downcast::<PyDict>()?;

    let modifiers = extract_op_modifiers(headers_dict)?;

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

    let tokio_rt = TOKIO_RUNTIME.get().ok_or_else(|| {
        PyRuntimeError::new_err("init_client must be called before delete_item")
    })?;

    let response_result: Result<CosmosResponse, CosmosError> = py.allow_threads(|| {
        tokio_rt.block_on(async {
            let container = driver
                .resolve_container(&database_name, &container_name)
                .await?;
            let item_ref =
                ItemReference::from_name(&container, partition_key, item_id);
            let mut op = CosmosOperation::delete_item(item_ref);

            if let Some(activity) = modifiers.activity_header.as_ref() {
                if let Ok(uuid) = activity.parse::<uuid::Uuid>() {
                    op = op.with_activity_id(ActivityId::from(uuid.to_string()));
                }
            }
            if let Some(session) = modifiers.session_header.as_ref() {
                op = op.with_session_token(SessionToken::from(session.clone()));
            }

            // No content_response_on_write override for delete: pass
            // None and let the driver default stand. custom_headers
            // carries If-Match / If-None-Match plus any caller-supplied
            // x-ms-* entries.
            let options = build_operation_options(
                None,
                modifiers.excluded_regions_value,
                modifiers.end_to_end_timeout,
                modifiers.custom_headers,
            );

            driver.execute_singleton_operation(op, options).await
        })
    });

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
// read_item
// ---------------------------------------------------------------------------
//
// Same input/output shape as delete_item:
//   * no request body (GET is bodiless);
//   * the document id comes from PreparedRequest.item_id;
//   * content_response_on_write is left at the driver default — reads
//     have no write-body to suppress (the kwarg is not even on
//     ``Container.read_item``);
//   * If-Match / If-None-Match conditional headers (built by the
//     Python helper from etag + match_condition) flow through
//     custom_headers; the dominant case on read is `If-None-Match`
//     (cache validation), which surfaces as HTTP 304 with an empty
//     body when the customer's cached etag still matches. The Python
//     parser treats 304 as a non-error and returns an empty
//     `CosmosDict`. ``x-ms-dedicatedgateway-max-age`` (driven by
//     Python's ``max_integrated_cache_staleness_in_ms`` kwarg) also
//     rides through custom_headers — see the wire-name match in
//     extract_op_modifiers.

#[pyfunction]
fn read_item<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let container_link: String = prepared.getattr("container_link")?.extract()?;
    let partition_key_header: String =
        prepared.getattr("partition_key_header")?.extract()?;
    let item_id: String = prepared
        .getattr("item_id")?
        .extract::<Option<String>>()?
        .ok_or_else(|| {
            PyValueError::new_err(
                "read_item: PreparedRequest.item_id is required for read operations",
            )
        })?;
    let headers_obj = prepared.getattr("headers")?;
    let headers_dict: &Bound<'py, PyDict> = headers_obj.downcast::<PyDict>()?;

    let modifiers = extract_op_modifiers(headers_dict)?;

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

    let tokio_rt = TOKIO_RUNTIME.get().ok_or_else(|| {
        PyRuntimeError::new_err("init_client must be called before read_item")
    })?;

    let response_result: Result<CosmosResponse, CosmosError> = py.allow_threads(|| {
        tokio_rt.block_on(async {
            let container = driver
                .resolve_container(&database_name, &container_name)
                .await?;
            let item_ref =
                ItemReference::from_name(&container, partition_key, item_id);
            let mut op = CosmosOperation::read_item(item_ref);

            if let Some(activity) = modifiers.activity_header.as_ref() {
                if let Ok(uuid) = activity.parse::<uuid::Uuid>() {
                    op = op.with_activity_id(ActivityId::from(uuid.to_string()));
                }
            }
            if let Some(session) = modifiers.session_header.as_ref() {
                op = op.with_session_token(SessionToken::from(session.clone()));
            }

            // No content_response_on_write override for read: the
            // driver default is correct (reads always return a body
            // when one exists, and 304 returns no body whether the
            // option is set or not). custom_headers carries
            // If-Match / If-None-Match plus the
            // x-ms-dedicatedgateway-max-age header.
            let options = build_operation_options(
                None,
                modifiers.excluded_regions_value,
                modifiers.end_to_end_timeout,
                modifiers.custom_headers,
            );

            driver.execute_singleton_operation(op, options).await
        })
    });

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
// Shared header → modifier translation
// ---------------------------------------------------------------------------
//
// Both create_item and delete_item walk PreparedRequest.headers and pick
// out the entries the driver models as typed fields (activity-id,
// session token, no_response, excluded_regions, end-to-end timeout).
// Everything else goes through the driver's custom_headers escape hatch.

struct OpModifiers {
    activity_header: Option<String>,
    session_header: Option<String>,
    // ``no_response=True`` -> Disabled, otherwise Enabled. Only
    // create_item consumes this; delete_item leaves the driver default
    // in place because it has no body to suppress.
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
    // body on create when the caller did not opt out.
    let mut content_response_on_write: ContentResponseOnWrite =
        ContentResponseOnWrite::Enabled;
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
    // through the driver's custom-headers escape hatch.
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
            excluded_regions_value =
                Some(regions.into_iter().collect::<ExcludedRegions>());
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
/// lifted out of the headers dict. ``content_response`` is ``Some(_)``
/// only for write ops where the kwarg is meaningful (today: create_item);
/// ``None`` leaves the driver default in place (used by delete_item).
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
        out.set_item("etag", v.as_str())?;
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


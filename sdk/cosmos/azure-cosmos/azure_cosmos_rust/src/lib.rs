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
//! Only `x-ms-activity-id` and `x-ms-session-token` are forwarded
//! from the request headers dict, because the driver's typed
//! `CosmosRequestHeaders` struct only accepts those two today.

use std::collections::HashMap;
use std::sync::{Arc, OnceLock, RwLock};

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyTuple};

use azure_data_cosmos_driver::{
    driver::{CosmosDriver, CosmosDriverRuntime},
    models::{
        AccountReference, ActivityId, CosmosOperation, ItemReference, PartitionKey,
        SessionToken,
    },
    options::OperationOptions,
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
static DRIVER_RUNTIME: OnceLock<CosmosDriverRuntime> = OnceLock::new();
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
    for (key, value) in headers_dict.iter() {
        let key_str: String = key.extract()?;
        let lower = key_str.to_ascii_lowercase();
        if lower == "x-ms-activity-id" {
            activity_header = Some(value.extract()?);
        } else if lower == "x-ms-session-token" {
            session_header = Some(value.extract()?);
        }
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

            driver.execute_operation(op, OperationOptions::new()).await
        })
    });

    let response = response_result.map_err(|e| {
        PyRuntimeError::new_err(format!("driver execute_operation failed: {e}"))
    })?;

    let status = response.status();
    let status_code = u16::from(status.status_code()) as i64;
    let sub_status = status.sub_status().map(u32::from).unwrap_or(0) as i64;

    // The driver's CosmosResponseHeaders only exposes typed accessors today
    // and does not surface the raw header map, so this dict is empty for
    // now. The Python parser falls back to body fields where it can.
    let response_headers = PyDict::new_bound(py);

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

/// Parse the JSON-array partition-key header into a typed PartitionKey.
/// Supports the four scalar variants (string, number, bool, null) for a
/// single-value partition key. Hierarchical partition keys (lists with
/// 2 or 3 elements) and the `[{}]` / `[]` shapes are rejected here
/// because the driver's public API does not expose `PartitionKeyValue`,
/// so we cannot construct a multi-component PartitionKey from outside
/// the driver crate today.
fn parse_partition_key_header(header: &str) -> PyResult<PartitionKey> {
    let parsed: Vec<serde_json::Value> = serde_json::from_str(header).map_err(|e| {
        PyValueError::new_err(format!("invalid partition_key_header {header:?}: {e}"))
    })?;

    if parsed.len() != 1 {
        return Err(PyValueError::new_err(format!(
            "rust backend currently only supports single-value partition keys; \
             got {} components in {header:?}",
            parsed.len()
        )));
    }
    let value = parsed.into_iter().next().unwrap();
    let pk: PartitionKey = match value {
        serde_json::Value::Null => PartitionKey::from(None::<String>),
        serde_json::Value::Bool(b) => PartitionKey::from(b),
        serde_json::Value::Number(n) => match n.as_f64() {
            Some(f) => PartitionKey::from(f),
            None => {
                return Err(PyValueError::new_err(format!(
                    "non-finite number in partition key header: {n}"
                )))
            }
        },
        serde_json::Value::String(s) => PartitionKey::from(s),
        other => {
            return Err(PyValueError::new_err(format!(
                "unsupported partition key value: {other}"
            )))
        }
    };
    Ok(pk)
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


// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Per-process runtime, the driver cache, and the client lifecycle entry points
//! (`acquire_driver_handle` / `release_driver_handle`).
//!
//! This file initializes the binding's driver runtimes, converts client settings
//! into driver options, and caches drivers using endpoint, credential, and config
//! fingerprints. Each successful acquisition adds a reference to the cache entry.
//!
//! Three "runtime"-ish things live here; keep them distinct:
//!   * shared Tokio runtime (`RuntimeContext.tokio_rt`) -- the binding-owned
//!     executor shared by driver work and the `pyo3-async-runtimes` bridge,
//!     distinct from Python's event loop.
//!   * driver runtime (`CosmosDriverRuntime`) -- the *factory* that builds rust
//!     drivers and carries the process-wide connection-pool config. Also one per
//!     process. It is built *on* the Tokio runtime.
//!   * rust driver (`CosmosDriver`) -- the per-account *driver* that signs,
//!     routes, and retries. This is the one thing here that is NOT process-wide:
//!     the cache retains one per handle, produced by
//!     `driver_runtime.create_driver(...)`, and its async work runs on the shared
//!     Tokio runtime.
//!
//! So the relationship is: one shared Tokio runtime and one driver runtime per
//! process (bundled together in `RuntimeContext`, behind one `OnceLock`); the
//! driver runtime is a factory that makes rust drivers, which this file caches
//! and reference-counts. Concurrent cache misses can build surplus drivers before
//! one is selected for the cache. Runtime initialization errors are cached too.
//!
//! `acquire_driver_handle` returns an opaque SHA-256 cache key. Identity uses the
//! parsed endpoint, process-salted credentials, and typed configuration values.
//! A balanced final release evicts the entry, but active operations can retain
//! their own `Arc` references to the driver after eviction.
//!
//! Terminology (consistent with `factory.py`, `rust.py`, `credential.rs`,
//! `ffi/`): client = the `CosmosClient`; binding = this compiled `_rust`
//! extension; rust driver / driver runtime / shared Tokio runtime as above;
//! driver handle = the cache key string; credential = how the customer proves who
//! they are.

use std::collections::HashMap;
use std::sync::{Arc, OnceLock};
use std::time::Duration;

use parking_lot::RwLock;
use pyo3::exceptions::{PyAttributeError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use sha2::{Digest, Sha256};

use azure_data_cosmos_driver::{
    driver::{CosmosDriver, CosmosDriverRuntime},
    fault_injection::{
        CustomResponseBuilder, FaultInjectionConditionBuilder, FaultInjectionResultBuilder,
        FaultInjectionRule, FaultInjectionRuleBuilder, FaultOperationType,
    },
    models::AccountReference,
    options::{
        AvailabilityStrategy, ConnectionPoolOptions, DriverOptions, ExcludedRegions,
        HedgeThreshold, HedgingStrategy, OperationOptions, OperationOptionsBuilder,
        ReadConsistencyStrategy, Region, ThrottlingRetryOptionsBuilder, UserAgentSuffix,
    },
};
use tokio::runtime::Runtime as TokioRuntime;
use url::Url;

use crate::credential::PyTokenCredential;

// ---------------------------------------------------------------------------
// Per-process singletons
// ---------------------------------------------------------------------------

/// Bundles the process-wide Tokio runtime, driver factory, and the runtime
/// settings that later clients must match. Built once by `runtime_context`.
pub(crate) struct RuntimeContext {
    pub(crate) tokio_rt: &'static TokioRuntime,
    pub(crate) driver_runtime: Arc<CosmosDriverRuntime>,
    settings: RuntimeSettings,
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
struct RuntimeSettings {
    proxy_allowed: Option<bool>,
    max_connect_timeout: Option<Duration>,
    max_dataplane_request_timeout: Option<Duration>,
    max_metadata_request_timeout: Option<Duration>,
}

/// One cached driver, its fault rules, and the number of outstanding acquisitions.
///
/// The key includes endpoint, credential, and config fingerprints because drivers
/// retain authentication and settings. Keying only by endpoint would incorrectly
/// share those values between differently configured clients.
///
/// Acquisition adds one reference; release removes one and evicts at zero.
/// Callers must balance these calls. This count does not include operation-held
/// `Arc`s, which can keep the driver alive independently of the cache.
pub(crate) struct DriverEntry {
    pub(crate) driver: Arc<CosmosDriver>,
    fault_rules: HashMap<String, Arc<FaultInjectionRule>>,
    refcount: usize,
}

/// Compute a `DriverEntry`'s next refcount and whether to evict it. Split out of
/// `release_driver_handle` so the drop-one / evict-at-zero rule can be tested without a real
/// `CosmosDriver`. Saturation prevents underflow, not duplicate-release errors:
/// an extra close on a shared handle still removes another acquisition's count.
fn apply_close(refcount: usize) -> (usize, bool) {
    let next = refcount.saturating_sub(1);
    (next, next == 0)
}

// ---------------------------------------------------------------------------
// Cache key: (endpoint, credential, config)
// ---------------------------------------------------------------------------
//
// * Master keys use process-salted SHA-256. Handles remain private identifiers,
//   not authorization tokens or a reason to log credential-derived values.
// * A token credential is keyed by its Python object identity. The cache holds a
//   reference to it, so its address can't be reused by another live credential while
//   cached. The token value is never read.
// * Config identity includes the typed fields consumed here, never Python repr().
static IDENTITY_SALT: OnceLock<Result<[u8; 32], String>> = OnceLock::new();

fn fingerprint(parts: &[&[u8]]) -> String {
    let mut hash = Sha256::new();
    for part in parts {
        hash.update((part.len() as u64).to_be_bytes());
        hash.update(part);
    }
    format!("{:x}", hash.finalize())
}

fn master_key_fingerprint(master_key: &str) -> PyResult<String> {
    let salt = IDENTITY_SALT
        .get_or_init(|| {
            let mut bytes = [0; 32];
            getrandom::fill(&mut bytes)
                .map_err(|error| format!("driver identity entropy failed: {error}"))?;
            Ok(bytes)
        })
        .as_ref()
        .map_err(|error| PyRuntimeError::new_err(error.clone()))?;
    Ok(format!(
        "mk:{}",
        fingerprint(&[salt, master_key.as_bytes()])
    ))
}

/// Fingerprint a token credential by its Python object identity, tagged `tc:`. The
/// tag distinguishes it from a master-key fingerprint.
fn token_credential_fingerprint(object_id: usize) -> String {
    format!("tc:{object_id:x}")
}

fn config_fingerprint_from_value(value: &serde_json::Value) -> String {
    format!("cfg:{}", fingerprint(&[value.to_string().as_bytes()]))
}

/// Explicit fields keep identity independent of object representation and field order.
fn config_fingerprint(config: Option<&Bound<'_, PyAny>>) -> PyResult<String> {
    macro_rules! field {
        ($name:literal, $kind:ty) => {
            match config {
                Some(config) => get_config_opt::<$kind>(config, $name)?,
                None => None,
            }
        };
    }
    let finite = |value: Option<f64>, name: &str| -> PyResult<Option<f64>> {
        if value.is_some_and(|value| !value.is_finite()) {
            return Err(PyValueError::new_err(format!("{name} must be finite")));
        }
        Ok(value.map(|value| if value == 0.0 { 0.0 } else { value }))
    };
    let mut rules = Vec::new();
    if let Some((config, items)) = config.zip(field!("fault_injection_rules", Vec<PyObject>)) {
        let py = config.py();
        for item in items {
            let item = item.bind(py);
            let probability: f32 = item.getattr("probability")?.extract()?;
            if !probability.is_finite() {
                return Err(PyValueError::new_err("fault probability must be finite"));
            }
            rules.push(serde_json::json!({
                "id": item.getattr("id")?.extract::<String>()?,
                "operation_type": item.getattr("operation_type")?.extract::<String>()?,
                "status_code": item.getattr("status_code")?.extract::<u16>()?,
                "sub_status": item.getattr("sub_status")?.extract::<u16>()?,
                "container_id": item.getattr("container_id")?.extract::<Option<String>>()?,
                "region": item.getattr("region")?.extract::<Option<String>>()?,
                "delay_ms": item.getattr("delay_ms")?.extract::<u64>()?,
                "probability": probability,
                "hit_limit": item.getattr("hit_limit")?.extract::<Option<u32>>()?,
                "enabled": item.getattr("enabled")?.extract::<bool>()?,
            }));
        }
    }
    let value = serde_json::json!({
        "preferred_locations": field!("preferred_locations", Vec<String>).unwrap_or_default(),
        "excluded_locations": field!("excluded_locations", Vec<String>).unwrap_or_default(),
        "throttling_max_retry_count": field!("throttling_max_retry_count", u32),
        "throttling_max_retry_wait_time_seconds": finite(field!("throttling_max_retry_wait_time_seconds", f64), "throttling_max_retry_wait_time_seconds")?,
        "hedging_threshold_ms": field!("hedging_threshold_ms", u64),
        "user_agent_suffix": field!("user_agent_suffix", String).filter(|value| !value.is_empty()),
        "consistency_level": field!("consistency_level", String),
        "proxy_allowed": field!("proxy_allowed", bool),
        "connection_timeout_seconds": finite(field!("connection_timeout_seconds", f64), "connection_timeout_seconds")?,
        "read_timeout_seconds": finite(field!("read_timeout_seconds", f64), "read_timeout_seconds")?,
        "fault_injection_rules": rules,
    });
    Ok(config_fingerprint_from_value(&value))
}

/// Length-prefix each part and expose only the final opaque digest.
fn compose_cache_key(endpoint: &str, credential_fp: &str, config_fp: &str) -> String {
    format!(
        "driver:{}",
        fingerprint(&[
            endpoint.as_bytes(),
            credential_fp.as_bytes(),
            config_fp.as_bytes()
        ])
    )
}

/// Compute the same identity used by acquisition, without starting the runtime,
/// acquiring a driver reference, or calling a credential.
fn driver_identity(
    endpoint: &str,
    master_key: Option<&str>,
    config: Option<&Bound<'_, PyAny>>,
    credential: Option<&Bound<'_, PyAny>>,
) -> PyResult<String> {
    validate_auth_inputs(master_key, credential)?;
    let endpoint = Url::parse(endpoint)
        .map_err(|error| PyValueError::new_err(format!("invalid endpoint URL: {error}")))?;
    let credential_fp = match credential {
        Some(token_credential) => token_credential_fingerprint(token_credential.as_ptr() as usize),
        None => master_key_fingerprint(
            master_key.ok_or_else(|| PyValueError::new_err(AUTH_REQUIRED_ERROR))?,
        )?,
    };
    Ok(compose_cache_key(
        endpoint.as_str(),
        &credential_fp,
        &config_fingerprint(config)?,
    ))
}

/// The driver runtime and its connection pool are process-global, so a later
/// explicit runtime setting that differs from the initialized value is a conflict.
///
/// The winner is whichever client wins the `OnceLock` `get_or_init` race -- NOT
/// "the first client in source order". Under concurrent client construction with
/// differing settings, which values initialize the process runtime are
/// nondeterministic and the loser gets a hard error. The contract is therefore
/// "use the same process-wide settings on every Rust client", not "set them on
/// the first client".
fn runtime_settings_conflict(initialized: RuntimeSettings, requested: RuntimeSettings) -> bool {
    setting_conflicts(initialized.proxy_allowed, requested.proxy_allowed)
        || setting_conflicts(
            initialized.max_connect_timeout,
            requested.max_connect_timeout,
        )
        || setting_conflicts(
            initialized.max_dataplane_request_timeout,
            requested.max_dataplane_request_timeout,
        )
        || setting_conflicts(
            initialized.max_metadata_request_timeout,
            requested.max_metadata_request_timeout,
        )
}

fn setting_conflicts<T: PartialEq>(initialized: Option<T>, requested: Option<T>) -> bool {
    requested.is_some() && initialized != requested
}

const AUTH_REQUIRED_ERROR: &str =
    "acquire_driver_handle requires either a master_key or a token credential";
const AUTH_EXCLUSIVE_ERROR: &str =
    "acquire_driver_handle received both master_key and token credential; exactly one must be set";

/// Require exactly one auth input -- a master key or a token credential -- at the
/// API boundary. Rejects "both" (ambiguous: which one signs requests?) and
/// "neither" (nothing to authenticate with) with a clear message. Without this
/// check, "neither" would fail deeper down in a less obvious place and "both"
/// could be resolved silently one way, hiding a real misconfiguration.
fn validate_auth_inputs(
    master_key: Option<&str>,
    credential: Option<&Bound<'_, PyAny>>,
) -> PyResult<()> {
    match (master_key, credential) {
        (Some(_), Some(_)) => Err(PyValueError::new_err(AUTH_EXCLUSIVE_ERROR)),
        (None, None) => Err(PyValueError::new_err(AUTH_REQUIRED_ERROR)),
        _ => Ok(()),
    }
}

// Keep init errors too, so every later caller sees the same failure reason.
static RUNTIME_CONTEXT: OnceLock<Result<RuntimeContext, String>> = OnceLock::new();
static DRIVERS: OnceLock<RwLock<HashMap<String, DriverEntry>>> = OnceLock::new();

/// Accessor for the one process-wide driver cache: the map from driver handle
/// (`(endpoint, credential, config)` key) to the reference-counted rust driver
/// for that key. The map is process-wide and created once; the rust drivers it
/// holds are per-key. Without a single accessor there would be no one shared
/// cache, so clients could not find each other's drivers to share them.
pub(crate) fn drivers() -> &'static RwLock<HashMap<String, DriverEntry>> {
    DRIVERS.get_or_init(|| RwLock::new(HashMap::new()))
}

/// Build (once) or fetch the two process-wide runtimes -- the shared Tokio
/// runtime and the driver runtime -- and return the shared `RuntimeContext`.
///
/// The first client to reach here initializes both together inside the
/// `RUNTIME_CONTEXT` `OnceLock`, with the GIL released (`py.allow_threads`), and
/// records its connection-pool settings. Every later client fetches the same
/// context and is checked against those recorded values. Because these runtimes
/// are process-wide (not per client), a later client asking for a different proxy
/// or transport timeout is a hard error rather than a silent mismatch.
fn runtime_context(
    py: Python<'_>,
    requested_settings: RuntimeSettings,
) -> PyResult<&'static RuntimeContext> {
    // Waiting for another initializer must also release the GIL; otherwise that
    // initializer cannot reacquire it to finish while this thread waits on OnceLock.
    let ctx_or_error = py.allow_threads(|| {
        RUNTIME_CONTEXT.get_or_init(|| {
            let tokio_rt = pyo3_async_runtimes::tokio::get_runtime();
            let mut runtime_builder = CosmosDriverRuntime::builder();
            if let Some(connection_pool) = connection_pool_from_settings(requested_settings)? {
                runtime_builder = runtime_builder.with_connection_pool(connection_pool);
            }
            let driver_runtime = tokio_rt
                .block_on(async { runtime_builder.build().await })
                .map_err(|e| format!("driver runtime build failed: {e}"))?;
            Ok(RuntimeContext {
                tokio_rt,
                driver_runtime,
                settings: requested_settings,
            })
        })
    });
    validate_runtime_context(ctx_or_error, requested_settings)
}

fn validate_runtime_context(
    context: &Result<RuntimeContext, String>,
    requested_settings: RuntimeSettings,
) -> PyResult<&RuntimeContext> {
    match context {
        Ok(ctx) => {
            if runtime_settings_conflict(ctx.settings, requested_settings) {
                return Err(PyValueError::new_err(format!(
                    "Rust transport configuration is process-global and was already initialized with {:?}; cannot honor {:?} for this client. Set proxy_allowed, connection_timeout, and read_timeout consistently on every Rust CosmosClient in the process.",
                    ctx.settings, requested_settings
                )));
            }
            Ok(ctx)
        }
        Err(message) => Err(PyRuntimeError::new_err(message.clone())),
    }
}

/// Check settings against an initialized runtime without creating one.
///
/// A successful check is not a reservation: another caller can initialize the
/// runtime afterwards. Acquisition repeats this check using the same rules.
#[pyfunction(name = "_validate_runtime_configuration")]
#[pyo3(signature = (config=None))]
pub(crate) fn validate_runtime_configuration(config: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
    let requested_settings = runtime_settings_from_config(config)?;
    if let Some(context) = RUNTIME_CONTEXT.get() {
        validate_runtime_context(context, requested_settings)?;
    }
    Ok(())
}

fn connection_pool_from_settings(
    settings: RuntimeSettings,
) -> Result<Option<ConnectionPoolOptions>, String> {
    if settings == RuntimeSettings::default() {
        return Ok(None);
    }
    let mut builder = ConnectionPoolOptions::builder();
    if let Some(proxy_allowed) = settings.proxy_allowed {
        builder = builder.with_proxy_allowed(proxy_allowed);
    }
    if let Some(timeout) = settings.max_connect_timeout {
        builder = builder.with_max_connect_timeout(timeout);
    }
    if let Some(timeout) = settings.max_dataplane_request_timeout {
        builder = builder.with_max_dataplane_request_timeout(timeout);
    }
    if let Some(timeout) = settings.max_metadata_request_timeout {
        builder = builder.with_max_metadata_request_timeout(timeout);
    }
    builder
        .build()
        .map(Some)
        .map_err(|e| format!("invalid connection pool options: {e}"))
}

/// Read-only fetch of the process-wide `RuntimeContext` for the per-operation
/// path (`wire/`), which needs the shared Tokio runtime to run a request but
/// must not (re)build it. Raises a clear "acquire_driver_handle must be called before
/// {op_name}" if no client has initialized the runtimes yet. Without it, an
/// operation issued before `acquire_driver_handle` would fail deep down with an obscure
/// error instead of a plain one naming the missing step.
pub(crate) fn require_runtime_context(op_name: &str) -> PyResult<&'static RuntimeContext> {
    match RUNTIME_CONTEXT.get() {
        Some(Ok(ctx)) => Ok(ctx),
        Some(Err(message)) => Err(PyRuntimeError::new_err(message.clone())),
        None => Err(PyRuntimeError::new_err(format!(
            "acquire_driver_handle must be called before {op_name}"
        ))),
    }
}

// ---------------------------------------------------------------------------
// acquire_driver_handle
// ---------------------------------------------------------------------------
//
#[pyfunction(name = "_runtime_configuration")]
pub(crate) fn runtime_configuration() -> Option<(Option<bool>, Option<f64>, Option<f64>)> {
    match RUNTIME_CONTEXT.get() {
        Some(Ok(ctx)) => Some((
            ctx.settings.proxy_allowed,
            ctx.settings
                .max_connect_timeout
                .map(|value| value.as_secs_f64()),
            ctx.settings
                .max_dataplane_request_timeout
                .map(|value| value.as_secs_f64()),
        )),
        _ => None,
    }
}

/// Acquire one reference to a cached driver and return its handle.
/// The Python backend calls this during lazy initialization, which can be retried
/// after a driver-build failure. This function does not enforce one call per client.
///
/// A cache hit increments its count. On a miss, build outside the cache lock,
/// then insert the driver or use the entry another caller inserted in the meantime.
/// Runtime settings are initialized process-wide; preferred regions and operation
/// defaults are configured on each newly built driver.
///
/// Validate that exactly one of `master_key` and the synchronous Python
/// `credential` is present. Token credentials are adapted by `PyTokenCredential`.

#[pyfunction]
#[pyo3(signature = (endpoint, master_key=None, config=None, credential=None))]
pub(crate) fn acquire_driver_handle(
    py: Python<'_>,
    endpoint: &str,
    master_key: Option<&str>,
    config: Option<&Bound<'_, PyAny>>,
    credential: Option<&Bound<'_, PyAny>>,
) -> PyResult<String> {
    validate_auth_inputs(master_key, credential)?;

    let endpoint_url = Url::parse(endpoint)
        .map_err(|e| PyValueError::new_err(format!("invalid endpoint URL: {e}")))?;

    let requested_settings = runtime_settings_from_config(config)?;
    let runtime_ctx = runtime_context(py, requested_settings)?;

    let driver_handle = driver_identity(endpoint, master_key, config, credential)?;

    // Fast path: reuse the matching cache entry and add one acquisition.
    // This changes the count, so it requires a write lock.
    {
        let mut cache = drivers().write();
        if let Some(entry) = cache.get_mut(&driver_handle) {
            entry.refcount += 1;
            return Ok(driver_handle);
        }
    }

    // Python clients default to no hedging, even when no config was prepared.
    let operation_options = operation_options_from_config(config)?;
    let (preferred_regions, user_agent_suffix, fault_rules) = match config {
        Some(client_config) => (
            preferred_regions_from_config(client_config)?,
            user_agent_suffix_from_config(client_config)?,
            fault_rules_from_config(client_config)?,
        ),
        None => (Vec::new(), None, Vec::new()),
    };

    // Slow path: build the driver. Held without any of our locks because
    // create_driver is async and may take seconds. The account carries
    // whichever auth the caller supplied: a token credential (wrapped so the
    // driver can call back into Python for tokens), otherwise the master key.
    // This binding enforces exactly one input at the API boundary.
    let account = match credential {
        Some(token_credential) => {
            let py_credential: Py<PyAny> = token_credential.clone().unbind();
            AccountReference::with_credential(
                endpoint_url,
                Arc::new(PyTokenCredential::new(py_credential)),
            )
        }
        None => {
            let key = master_key.ok_or_else(|| PyValueError::new_err(AUTH_REQUIRED_ERROR))?;
            AccountReference::with_master_key(endpoint_url, key.to_string())
        }
    };

    // `create_driver` takes a single required `DriverOptions` that carries the
    // account itself and the Python client's operation defaults.
    let driver_options = {
        let mut builder = DriverOptions::builder(account).with_operation_options(operation_options);
        if !preferred_regions.is_empty() {
            builder = builder.with_preferred_regions(preferred_regions);
        }
        if let Some(user_agent_suffix) = user_agent_suffix {
            builder = builder.with_user_agent_suffix(user_agent_suffix);
        }
        if !fault_rules.is_empty() {
            builder = builder
                .with_fault_injection_rules(fault_rules.clone())
                .map_err(|e| PyValueError::new_err(format!("invalid fault rules: {e}")))?;
        }
        builder.build()
    };

    // Build the driver on the shared runtime as a spawned task, then wait on its
    // handle with the GIL released. Concurrent acquisitions can submit separate
    // build tasks. Join failures are mapped to Python errors below.
    let driver_runtime = Arc::clone(&runtime_ctx.driver_runtime);
    let build_task = runtime_ctx
        .tokio_rt
        .spawn(async move { driver_runtime.create_driver(driver_options).await });
    let driver = py
        .allow_threads(|| runtime_ctx.tokio_rt.block_on(build_task))
        .map_err(|join_error| {
            PyRuntimeError::new_err(format!("driver init task failed: {join_error}"))
        })?
        .map_err(|e| PyRuntimeError::new_err(format!("driver init failed: {e}")))?;

    // Insert under the write lock as the first reference. If two threads raced to
    // build the same key, the first to take the lock wins; the loser's driver is
    // dropped after the lock is released, not inside it -- dropping a CosmosDriver
    // runs teardown that could block other threads or panic, and that must not happen
    // while the cache lock is held.
    let mut surplus_driver: Option<Arc<CosmosDriver>> = None;
    {
        let mut cache = drivers().write();
        match cache.get_mut(&driver_handle) {
            Some(entry) => {
                entry.refcount += 1;
                surplus_driver = Some(driver);
            }
            None => {
                cache.insert(
                    driver_handle.clone(),
                    DriverEntry {
                        driver,
                        fault_rules: fault_rules
                            .into_iter()
                            .map(|rule| (rule.id().to_string(), rule))
                            .collect(),
                        refcount: 1,
                    },
                );
            }
        }
    }
    // Drop the race-loser driver (if any) now that the lock is released.
    drop(surplus_driver);

    Ok(driver_handle)
}

/// Read the process-wide connection-pool settings from the prepared config.
fn runtime_settings_from_config(config: Option<&Bound<'_, PyAny>>) -> PyResult<RuntimeSettings> {
    let Some(client_config) = config else {
        return Ok(RuntimeSettings::default());
    };
    // Compatibility mapping: the driver exposes complete HTTP-attempt caps,
    // not the customer's socket-read inactivity timer (driver parity gap 17).
    let http_attempt_cap = timeout_from_config(client_config, "read_timeout_seconds")?;
    Ok(RuntimeSettings {
        proxy_allowed: get_config_opt::<bool>(client_config, "proxy_allowed")?,
        max_connect_timeout: timeout_from_config(client_config, "connection_timeout_seconds")?,
        max_dataplane_request_timeout: http_attempt_cap,
        max_metadata_request_timeout: http_attempt_cap,
    })
}

fn timeout_from_config(config: &Bound<'_, PyAny>, field_name: &str) -> PyResult<Option<Duration>> {
    let Some(seconds) = get_config_opt::<f64>(config, field_name)? else {
        return Ok(None);
    };
    Duration::try_from_secs_f64(seconds).map(Some).map_err(|_| {
        PyValueError::new_err(format!(
            "{field_name} must be a finite, non-negative number of seconds"
        ))
    })
}

/// Read the optional `preferred_locations` off the prepared client config and
/// turn each region name into a driver `Region` for preferred-region routing.
///
/// Matches how `extract_settings` reads `excluded_locations`: it accepts any
/// Python sequence of strings (the `PreparedClientConfig` stores a tuple) and
/// lets the driver normalize each name ("West US" -> "westus"). A config object
/// without the attribute, or a Python `None`, yields no regions rather than an
/// error, so the binding stays compatible with config shapes that predate or
/// postdate this field; the driver then keeps its default endpoint ordering.
fn preferred_regions_from_config(config: &Bound<'_, PyAny>) -> PyResult<Vec<Region>> {
    let value = match config.getattr("preferred_locations") {
        Ok(value) => value,
        Err(err) if err.is_instance_of::<PyAttributeError>(config.py()) => return Ok(Vec::new()),
        Err(err) => return Err(err),
    };
    if value.is_none() {
        return Ok(Vec::new());
    }
    let region_names: Vec<String> = value.extract().map_err(|e| {
        PyValueError::new_err(format!(
            "preferred_locations must be a sequence of region-name strings: {e}"
        ))
    })?;
    validate_region_names(&region_names)?;
    Ok(region_names.into_iter().map(Region::from).collect())
}

fn validate_region_names(names: &[String]) -> PyResult<()> {
    if names.iter().any(|name| name.trim().is_empty()) {
        return Err(PyValueError::new_err(
            "region names must be non-empty strings",
        ));
    }
    Ok(())
}

/// Read the optional `user_agent_suffix` and turn it into the driver's
/// `UserAgentSuffix` for driver construction. A missing
/// attribute, a Python `None`, or an empty string yields `None`, leaving the driver's
/// default SDK User-Agent in place. (`build_client_config` normalizes an empty suffix
/// to `None`, so an empty string only reaches here from a hand-built config.)
///
/// The driver's `UserAgentSuffix` allows at most `UserAgentSuffix::MAX_LENGTH` (25)
/// header-safe characters (alphanumeric, `-`, `_`, `.`, `~`). A present value that
/// fails that check is a hard error rather than a silent drop. `try_new` (not `new`)
/// is used so an invalid value returns a `ValueError` instead of panicking across the
/// FFI boundary.
fn user_agent_suffix_from_config(config: &Bound<'_, PyAny>) -> PyResult<Option<UserAgentSuffix>> {
    let suffix = match get_config_opt::<String>(config, "user_agent_suffix")? {
        Some(suffix) => suffix,
        None => return Ok(None),
    };
    if suffix.is_empty() {
        return Ok(None);
    }
    match UserAgentSuffix::try_new(suffix.as_str()) {
        Some(value) => Ok(Some(value)),
        None => Err(PyValueError::new_err(format!(
            "user_agent_suffix {suffix:?} is not valid for the Rust backend: it \
             must be at most {} characters and contain only alphanumeric, '-', \
             '_', '.', or '~' characters.",
            UserAgentSuffix::MAX_LENGTH
        ))),
    }
}

fn fault_rules_from_config(config: &Bound<'_, PyAny>) -> PyResult<Vec<Arc<FaultInjectionRule>>> {
    let value = match config.getattr("fault_injection_rules") {
        Ok(value) => value,
        Err(err) => {
            if err.is_instance_of::<PyAttributeError>(config.py()) {
                return Ok(Vec::new());
            }
            return Err(err);
        }
    };
    if value.is_none() {
        return Ok(Vec::new());
    }

    let mut rules = Vec::new();
    for item in value.iter()? {
        let item = item?;
        let id: String = item.getattr("id")?.extract()?;
        let operation_name: String = item.getattr("operation_type")?.extract()?;
        let operation_type = operation_name.parse::<FaultOperationType>().map_err(|e| {
            PyValueError::new_err(format!(
                "fault rule {id:?} has invalid operation_type {operation_name:?}: {e}"
            ))
        })?;

        let mut condition =
            FaultInjectionConditionBuilder::new().with_operation_type(operation_type);
        if let Some(container_id) = item.getattr("container_id")?.extract::<Option<String>>()? {
            condition = condition.with_container_id(container_id);
        }
        if let Some(region) = item.getattr("region")?.extract::<Option<String>>()? {
            condition = condition.with_region(Region::from(region));
        }

        let status_code: u16 = item.getattr("status_code")?.extract()?;
        let sub_status: u16 = item.getattr("sub_status")?.extract()?;
        let mut response =
            CustomResponseBuilder::new(azure_core::http::StatusCode::from(status_code));
        if sub_status != 0 {
            response = response.with_sub_status(sub_status);
        }

        let delay_ms: u64 = item.getattr("delay_ms")?.extract()?;
        let probability: f32 = item.getattr("probability")?.extract()?;
        let mut result = FaultInjectionResultBuilder::new()
            .with_custom_response(response.build())
            .with_probability(probability);
        if delay_ms != 0 {
            result = result.with_delay(Duration::from_millis(delay_ms));
        }

        let mut rule_builder =
            FaultInjectionRuleBuilder::new(id, result.build()).with_condition(condition.build());
        if let Some(hit_limit) = item.getattr("hit_limit")?.extract::<Option<u32>>()? {
            rule_builder = rule_builder.with_hit_limit(hit_limit);
        }
        let rule = Arc::new(rule_builder.build());
        if !item.getattr("enabled")?.extract::<bool>()? {
            rule.disable();
        }
        rules.push(rule);
    }
    Ok(rules)
}

/// Build a driver-level `OperationOptions` from the prepared client config's
/// defaults -- excluded regions, throttle-retry caps, the hedging threshold,
/// and the chosen read consistency level. Individual operations can also supply
/// options; this function does not establish their final merged values.
///
/// Missing config or threshold means Python's default: hedging disabled.
/// Other absent fields keep the driver's defaults. An enabled per-operation
/// strategy can still override this client-level strategy.
fn operation_options_from_config(config: Option<&Bound<'_, PyAny>>) -> PyResult<OperationOptions> {
    let mut builder =
        OperationOptionsBuilder::new().with_availability_strategy(AvailabilityStrategy::Disabled);
    let Some(config) = config else {
        return Ok(builder.build());
    };

    // excluded_locations -> ExcludedRegions. Same collection shape the
    // per-operation `excludedLocations` option already uses; the driver
    // normalizes each region name.
    if let Some(region_names) = get_config_opt::<Vec<String>>(config, "excluded_locations")? {
        validate_region_names(&region_names)?;
        if !region_names.is_empty() {
            builder = builder
                .with_excluded_regions(region_names.into_iter().collect::<ExcludedRegions>());
        }
    }

    // throttling_max_retry_count / _wait_time_seconds -> ThrottlingRetryOptions.
    // Set only when at least one field was supplied; otherwise leave this option
    // to the driver defaults.
    for name in [
        "throttling_max_retry_count",
        "throttling_max_retry_wait_time_seconds",
    ] {
        if let Some(value) = get_config_opt::<PyObject>(config, name)? {
            if value
                .bind(config.py())
                .is_instance_of::<pyo3::types::PyBool>()
            {
                return Err(PyValueError::new_err(format!(
                    "{name} must be numeric, not bool"
                )));
            }
        }
    }
    let max_retry_count = get_config_opt::<u32>(config, "throttling_max_retry_count")?;
    let max_retry_wait_seconds =
        get_config_opt::<f64>(config, "throttling_max_retry_wait_time_seconds")?;
    if max_retry_count.is_some() || max_retry_wait_seconds.is_some() {
        let mut throttle = ThrottlingRetryOptionsBuilder::new();
        if let Some(count) = max_retry_count {
            throttle = throttle.with_max_retry_count(count);
        }
        if let Some(seconds) = max_retry_wait_seconds {
            let duration = Duration::try_from_secs_f64(seconds).map_err(|_| {
                PyValueError::new_err(
                    "throttling retry wait must be finite nonnegative seconds within range",
                )
            })?;
            throttle = throttle.with_max_retry_wait_time(duration);
        }
        builder = builder.with_throttling_retry_options(throttle.build());
    }

    // hedging threshold -> AvailabilityStrategy::Hedging. Present only when the
    // customer enabled hedging (availability_strategy True / dict). The Python
    // side validates threshold_ms > 0; reject an invalid hand-built config too.
    if let Some(threshold_ms) = get_config_opt::<u64>(config, "hedging_threshold_ms")? {
        let threshold = HedgeThreshold::new(Duration::from_millis(threshold_ms))
            .ok_or_else(|| PyValueError::new_err("hedging_threshold_ms must be positive"))?;
        builder = builder.with_availability_strategy(AvailabilityStrategy::Hedging(
            HedgingStrategy::new(threshold),
        ));
    }

    // consistency_level -> ReadConsistencyStrategy. Set only when the customer
    // supplied a non-empty value. This binding accepts Eventual, Session, and
    // Strong; reject other non-empty values even if Python preparation was bypassed.
    if let Some(level) = get_config_opt::<String>(config, "consistency_level")? {
        if !level.is_empty() {
            match read_consistency_from_str(&level) {
                Some(strategy) => {
                    builder = builder.with_read_consistency_strategy(strategy);
                }
                None => {
                    return Err(PyValueError::new_err(format!(
                        "consistency_level {level:?} is not supported on the Rust \
                         backend; supported levels are Eventual, Session, and Strong."
                    )));
                }
            }
        }
    }

    Ok(builder.build())
}

/// Map a Python consistency-level string to the driver's `ReadConsistencyStrategy`.
///
/// This binding maps `"Eventual"` and `"Session"` directly, and `"Strong"` to
/// `GlobalStrong`. Any other string returns `None` for the caller to reject.
fn read_consistency_from_str(level: &str) -> Option<ReadConsistencyStrategy> {
    match level {
        "Eventual" => Some(ReadConsistencyStrategy::Eventual),
        "Session" => Some(ReadConsistencyStrategy::Session),
        "Strong" => Some(ReadConsistencyStrategy::GlobalStrong),
        _ => None,
    }
}

/// Read an optional attribute off the prepared client config, tolerating a
/// missing attribute or a Python `None` (both yield `Ok(None)`). A present but
/// wrong-typed value is a hard error so a real misconfiguration is loud rather
/// than silently dropped.
fn get_config_opt<'py, T>(config: &Bound<'py, PyAny>, attr: &str) -> PyResult<Option<T>>
where
    T: FromPyObject<'py>,
{
    match config.getattr(attr) {
        Ok(value) => value
            .extract::<Option<T>>()
            .map_err(|e| PyValueError::new_err(format!("client config field {attr:?}: {e}"))),
        Err(err) => {
            if err.is_instance_of::<PyAttributeError>(config.py()) {
                Ok(None)
            } else {
                Err(err)
            }
        }
    }
}

/// Release one acquisition for this exact cache handle and evict at zero.
/// Unknown handles are no-ops, but repeated releases of a still-shared handle
/// decrement other holders' count. The Python backend must release at most once
/// per acquisition. Operation-held Arcs can outlive cache eviction.
#[pyfunction]
pub(crate) fn release_driver_handle(driver_handle: &str) -> PyResult<()> {
    // Remove the entry under the lock, then drop its Arc outside the lock.
    // This drop need not be the driver's final reference.
    let evicted: Option<DriverEntry> = {
        let mut cache = drivers().write();
        let evict = match cache.get_mut(driver_handle) {
            Some(entry) => {
                let (next, evict) = apply_close(entry.refcount);
                entry.refcount = next;
                evict
            }
            None => false,
        };
        if evict {
            cache.remove(driver_handle)
        } else {
            None
        }
    };
    drop(evicted);
    Ok(())
}

#[pyfunction]
pub(crate) fn _debug_fault_injection_rule_hit_count(driver_handle: &str, rule_id: &str) -> PyResult<u32> {
    let cache = drivers().read();
    let entry = cache
        .get(driver_handle)
        .ok_or_else(|| PyValueError::new_err("unknown or closed Rust client handle"))?;
    let rule = entry.fault_rules.get(rule_id).ok_or_else(|| {
        PyValueError::new_err(format!("unknown fault injection rule id: {rule_id:?}"))
    })?;
    Ok(rule.hit_count())
}

#[cfg(test)]
mod tests {
    use super::{
        apply_close, compose_cache_key, config_fingerprint_from_value,
        connection_pool_from_settings, get_config_opt, master_key_fingerprint,
        operation_options_from_config, read_consistency_from_str, runtime_settings_conflict,
        runtime_settings_from_config, token_credential_fingerprint, validate_auth_inputs,
        validate_runtime_context, RuntimeContext, RuntimeSettings, AUTH_EXCLUSIVE_ERROR,
        AUTH_REQUIRED_ERROR,
    };
    use azure_data_cosmos_driver::options::{
        AvailabilityStrategy, HedgeThreshold, HedgingStrategy, OperationOptionsBuilder,
        OperationOptionsView, ReadConsistencyStrategy,
    };
    use pyo3::exceptions::{PyRuntimeError, PyValueError};
    use pyo3::prelude::*;
    use pyo3::types::{PyModule, PyString};
    use std::time::Duration;

    #[test]
    fn client_config_rejects_invalid_retries_and_regions() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let config = PyModule::import_bound(py, "types")
                .unwrap()
                .getattr("SimpleNamespace")
                .unwrap()
                .call0()
                .unwrap();
            for count in [-1_i64, 4294967296] {
                config.setattr("throttling_max_retry_count", count).unwrap();
                assert!(operation_options_from_config(Some(&config)).is_err());
            }
            config.setattr("throttling_max_retry_count", true).unwrap();
            assert!(operation_options_from_config(Some(&config)).is_err());
            config.setattr("throttling_max_retry_count", 0).unwrap();
            for wait in [-1.0, f64::NAN, f64::INFINITY, 2_f64.powi(64)] {
                config
                    .setattr("throttling_max_retry_wait_time_seconds", wait)
                    .unwrap();
                assert!(operation_options_from_config(Some(&config)).is_err());
            }
            config
                .setattr("throttling_max_retry_wait_time_seconds", true)
                .unwrap();
            assert!(operation_options_from_config(Some(&config)).is_err());
            config
                .setattr("throttling_max_retry_wait_time_seconds", 0)
                .unwrap();
            assert!(operation_options_from_config(Some(&config)).is_ok());
            config.setattr("preferred_locations", vec![123]).unwrap();
            assert!(super::preferred_regions_from_config(&config).is_err());
            config.setattr("preferred_locations", vec![" "]).unwrap();
            assert!(super::preferred_regions_from_config(&config).is_err());
            config.setattr("excluded_locations", vec![123]).unwrap();
            assert!(operation_options_from_config(Some(&config)).is_err());
            config.setattr("excluded_locations", vec![" "]).unwrap();
            assert!(operation_options_from_config(Some(&config)).is_err());
        });
    }

    #[test]
    fn client_hedging_defaults_to_disabled_with_or_without_config() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let options = operation_options_from_config(None).unwrap();
            assert_eq!(
                options.availability_strategy,
                Some(AvailabilityStrategy::Disabled)
            );
            let module = PyModule::from_code_bound(
                py,
                r#"
class Empty:
    pass
class Missing:
    preferred_locations = ("West US",)
class ExplicitNone:
    hedging_threshold_ms = None
    consistency_level = "Session"
"#,
                "hedging_config_test.py",
                "hedging_config_test",
            )
            .unwrap();
            for name in ["Empty", "Missing", "ExplicitNone"] {
                let config = module.getattr(name).unwrap().call0().unwrap();
                let options = operation_options_from_config(Some(&config)).unwrap();
                assert_eq!(
                    options.availability_strategy,
                    Some(AvailabilityStrategy::Disabled)
                );
                if name == "ExplicitNone" {
                    assert_eq!(
                        options.read_consistency_strategy,
                        Some(ReadConsistencyStrategy::Session)
                    );
                }
            }
        });
    }

    #[test]
    fn client_hedging_enabled_preserves_default_and_custom_thresholds() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let types = PyModule::import_bound(py, "types").unwrap();
            for threshold_ms in [500_u64, 25] {
                let config = types.getattr("SimpleNamespace").unwrap().call0().unwrap();
                config
                    .setattr("hedging_threshold_ms", threshold_ms)
                    .unwrap();
                let options = operation_options_from_config(Some(&config)).unwrap();
                let expected = AvailabilityStrategy::Hedging(HedgingStrategy::new(
                    HedgeThreshold::new(Duration::from_millis(threshold_ms)).unwrap(),
                ));
                assert_eq!(options.availability_strategy, Some(expected));
            }
        });
    }

    #[test]
    fn client_hedging_rejects_invalid_threshold_instead_of_disabling_silently() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let config = PyModule::import_bound(py, "types")
                .unwrap()
                .getattr("SimpleNamespace")
                .unwrap()
                .call0()
                .unwrap();
            config.setattr("hedging_threshold_ms", 0).unwrap();
            let error = operation_options_from_config(Some(&config)).unwrap_err();
            assert!(error.is_instance_of::<pyo3::exceptions::PyValueError>(py));
            assert!(error
                .to_string()
                .contains("hedging_threshold_ms must be positive"));
            config.setattr("hedging_threshold_ms", "invalid").unwrap();
            assert!(operation_options_from_config(Some(&config)).is_err());
        });
    }

    #[test]
    fn client_hedging_default_allows_explicit_request_override() {
        let account = std::sync::Arc::new(operation_options_from_config(None).unwrap());
        let enabled = AvailabilityStrategy::Hedging(HedgingStrategy::new(
            HedgeThreshold::new(Duration::from_millis(50)).unwrap(),
        ));
        let operation = OperationOptionsBuilder::new()
            .with_availability_strategy(enabled)
            .build();
        let view = OperationOptionsView::new(None, None, Some(account.clone()), Some(&operation));
        assert_eq!(view.availability_strategy(), Some(&enabled));
        let view = OperationOptionsView::new(None, None, Some(account), None);
        assert_eq!(
            view.availability_strategy(),
            Some(&AvailabilityStrategy::Disabled)
        );
    }

    // Test the count/eviction decision in isolation, not a live cache or driver
    // destructor. The count belongs to one exact handle, not an entire endpoint.
    #[test]
    fn apply_close_drops_one_reference_and_evicts_only_at_zero() {
        // One release from a count of two leaves one acquisition.
        assert_eq!(apply_close(2), (1, false));
        // Releasing the final count requests eviction.
        assert_eq!(apply_close(1), (0, true));
    }

    #[test]
    fn apply_close_on_zero_is_a_saturating_no_op_evict() {
        // Saturation at zero prevents underflow. It does not make duplicate
        // releases safe while another acquisition still contributes to the count.
        assert_eq!(apply_close(0), (0, true));
    }

    // Check the binding's string-to-strategy mapping, not request transmission
    // or customer-visible consistency guarantees.
    #[test]
    fn read_consistency_maps_supported_levels() {
        assert_eq!(
            read_consistency_from_str("Eventual"),
            Some(ReadConsistencyStrategy::Eventual)
        );
        assert_eq!(
            read_consistency_from_str("Session"),
            Some(ReadConsistencyStrategy::Session)
        );
        // Strong maps to the driver's GlobalStrong -- there is no plain Strong.
        assert_eq!(
            read_consistency_from_str("Strong"),
            Some(ReadConsistencyStrategy::GlobalStrong)
        );
    }

    #[test]
    fn read_consistency_rejects_unsupported_and_unknown() {
        // This binding mapping does not accept these two Python names.
        assert_eq!(read_consistency_from_str("BoundedStaleness"), None);
        assert_eq!(read_consistency_from_str("ConsistentPrefix"), None);
        // An outright-unknown string is rejected, not dropped.
        assert_eq!(read_consistency_from_str("Nonsense"), None);
        // The mapping is exact: the driver's own wire spelling is not a Python
        // consistency-level name, so it does not sneak through here.
        assert_eq!(read_consistency_from_str("GlobalStrong"), None);
        assert_eq!(read_consistency_from_str(""), None);
    }

    #[test]
    fn runtime_settings_conflict_only_when_later_explicit_value_differs() {
        let initialized = RuntimeSettings {
            proxy_allowed: Some(true),
            max_connect_timeout: Some(Duration::from_secs(5)),
            max_dataplane_request_timeout: Some(Duration::from_secs(65)),
            max_metadata_request_timeout: Some(Duration::from_secs(65)),
        };
        assert!(!runtime_settings_conflict(
            initialized,
            RuntimeSettings::default()
        ));
        assert!(!runtime_settings_conflict(initialized, initialized));
        assert!(runtime_settings_conflict(
            initialized,
            RuntimeSettings {
                max_connect_timeout: Some(Duration::from_secs(4)),
                ..initialized
            }
        ));
        assert!(runtime_settings_conflict(
            RuntimeSettings::default(),
            RuntimeSettings {
                proxy_allowed: Some(true),
                ..RuntimeSettings::default()
            }
        ));
    }

    #[test]
    fn runtime_settings_read_transport_timeouts_from_python_config() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = PyModule::from_code_bound(
                py,
                r#"
class Config:
    proxy_allowed = False
    connection_timeout_seconds = 1.25
    read_timeout_seconds = 42.5
"#,
                "runtime_settings_test.py",
                "runtime_settings_test",
            )
            .expect("module must compile");
            let config = module
                .getattr("Config")
                .and_then(|cls| cls.call0())
                .expect("Config() should construct");

            let settings =
                runtime_settings_from_config(Some(&config)).expect("settings should parse");
            assert_eq!(settings.proxy_allowed, Some(false));
            assert_eq!(
                settings.max_connect_timeout,
                Some(Duration::from_millis(1_250))
            );
            assert_eq!(
                settings.max_dataplane_request_timeout,
                Some(Duration::from_millis(42_500))
            );
            assert_eq!(
                settings.max_metadata_request_timeout,
                Some(Duration::from_millis(42_500))
            );
        });
    }

    #[test]
    fn runtime_validation_propagates_cached_initialization_failure() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let context = Err("driver runtime build failed: test failure".to_owned());
            let error = validate_runtime_context(&context, RuntimeSettings::default())
                .err()
                .expect("cached initialization failure must propagate");
            assert!(error.is_instance_of::<PyRuntimeError>(py));
            assert!(error.to_string().contains("test failure"));
        });
    }

    #[test]
    fn acquisition_identity_covers_config_and_credential_without_starting_driver() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = PyModule::from_code_bound(
                py,
                r#"
from types import SimpleNamespace
class Config(SimpleNamespace):
    def __repr__(self):
        raise AssertionError("identity must not use repr")
class Credential:
    def get_token(self, *args, **kwargs):
        raise AssertionError("identity must not request a token")
credential = Credential()
baseline = Config()
variants = [
    Config(preferred_locations=("East US",)),
    Config(excluded_locations=("Central US",)),
    Config(throttling_max_retry_count=7),
    Config(throttling_max_retry_wait_time_seconds=12.5),
    Config(hedging_threshold_ms=250),
    Config(user_agent_suffix="checkout-west"),
    Config(consistency_level="Eventual"),
    Config(proxy_allowed=True),
    Config(connection_timeout_seconds=1.5),
    Config(read_timeout_seconds=30.0),
    Config(fault_injection_rules=(SimpleNamespace(
        id="rule", operation_type="CreateItem", status_code=502, sub_status=0,
        container_id=None, region=None, delay_ms=0, probability=1.0,
        hit_limit=None, enabled=True),)),
]
"#,
                "identity_test.py",
                "identity_test",
            ).unwrap();
            let url = "https://identity.invalid";
            let baseline = module.getattr("baseline").unwrap();
            let identity = super::driver_identity(url, Some("key"), Some(&baseline), None).unwrap();
            assert_eq!(identity, super::driver_identity(url, Some("key"), None, None).unwrap());
            for config in module.getattr("variants").unwrap().iter().unwrap() {
                let config = config.unwrap();
                assert_ne!(identity, super::driver_identity(url, Some("key"), Some(&config), None).unwrap());
            }
            assert_ne!(identity, super::driver_identity(url, Some("different-key"), None, None).unwrap());
            let credential = module.getattr("credential").unwrap();
            let token_identity = super::driver_identity(url, None, None, Some(&credential)).unwrap();
            assert_ne!(identity, token_identity);
            assert_eq!(token_identity, super::driver_identity(url, None, None, Some(&credential)).unwrap());
        });
    }

    #[test]
    fn runtime_validation_checks_successfully_initialized_settings() {
        pyo3::prepare_freethreaded_python();
        let tokio_rt = pyo3_async_runtimes::tokio::get_runtime();
        let driver_runtime = tokio_rt
            .block_on(azure_data_cosmos_driver::driver::CosmosDriverRuntime::builder().build())
            .expect("local driver runtime should build without an account");
        let settings = RuntimeSettings {
            proxy_allowed: Some(true),
            max_connect_timeout: Some(Duration::from_secs(2)),
            ..RuntimeSettings::default()
        };
        let context = Ok(RuntimeContext {
            tokio_rt,
            driver_runtime,
            settings,
        });
        Python::with_gil(|py| {
            assert!(validate_runtime_context(&context, RuntimeSettings::default()).is_ok());
            assert!(validate_runtime_context(&context, settings).is_ok());
            let error = validate_runtime_context(
                &context,
                RuntimeSettings {
                    max_connect_timeout: Some(Duration::from_secs(5)),
                    ..settings
                },
            )
            .err()
            .expect("different initialized timeout must fail");
            assert!(error.is_instance_of::<PyValueError>(py));
            assert!(error.to_string().contains("process-global"));
        });
    }

    #[test]
    fn runtime_settings_compare_timeouts_at_native_nanosecond_precision() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = PyModule::from_code_bound(
                py,
                r#"
class Config:
    proxy_allowed = None
    connection_timeout_seconds = 2.123456789
    read_timeout_seconds = 25.123456789
"#,
                "runtime_precision_test.py",
                "runtime_precision_test",
            )
            .expect("module must compile");
            let config = module.getattr("Config").unwrap().call0().unwrap();
            let initialized = runtime_settings_from_config(Some(&config)).unwrap();
            config
                .setattr("connection_timeout_seconds", 2.1234567891)
                .unwrap();
            config
                .setattr("read_timeout_seconds", 25.1234567891)
                .unwrap();
            let equivalent = runtime_settings_from_config(Some(&config)).unwrap();
            assert!(!runtime_settings_conflict(initialized, equivalent));
            config
                .setattr("connection_timeout_seconds", 2.1234567896)
                .unwrap();
            let different = runtime_settings_from_config(Some(&config)).unwrap();
            assert!(runtime_settings_conflict(initialized, different));
        });
    }

    #[test]
    fn runtime_settings_build_connection_pool_timeout_caps() {
        let settings = RuntimeSettings {
            proxy_allowed: Some(false),
            max_connect_timeout: Some(Duration::from_millis(1_250)),
            max_dataplane_request_timeout: Some(Duration::from_millis(42_500)),
            max_metadata_request_timeout: Some(Duration::from_millis(42_500)),
        };
        let pool = connection_pool_from_settings(settings)
            .expect("connection pool settings should be valid")
            .expect("non-default settings should build a pool");
        assert!(!pool.proxy_allowed());
        assert_eq!(pool.max_connect_timeout(), Duration::from_millis(1_250));
        assert_eq!(
            pool.max_dataplane_request_timeout(),
            Duration::from_millis(42_500)
        );
        assert_eq!(
            pool.max_metadata_request_timeout(),
            Duration::from_millis(42_500)
        );
    }

    #[test]
    fn validate_auth_inputs_rejects_missing_and_ambiguous_inputs() {
        let missing = validate_auth_inputs(None, None).expect_err("missing auth should fail");
        assert!(
            missing.to_string().contains(AUTH_REQUIRED_ERROR),
            "unexpected error: {missing}"
        );

        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let cred = PyString::new_bound(py, "token-credential").into_any();
            let both = validate_auth_inputs(Some("master-key"), Some(&cred))
                .expect_err("both auth inputs should fail");
            assert!(
                both.to_string().contains(AUTH_EXCLUSIVE_ERROR),
                "unexpected error: {both}"
            );
        });
    }

    #[test]
    fn get_config_opt_ignores_only_missing_attribute() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = PyModule::from_code_bound(
                py,
                r#"
class Config:
    @property
    def exploding(self):
        raise RuntimeError("boom")
"#,
                "runtime_config_test.py",
                "runtime_config_test",
            )
            .expect("module must compile");
            let config = module
                .getattr("Config")
                .and_then(|cls| cls.call0())
                .expect("Config() should construct");

            let missing = get_config_opt::<String>(&config, "missing_attr")
                .expect("missing attribute should map to None");
            assert_eq!(missing, None);

            let err = get_config_opt::<String>(&config, "exploding")
                .expect_err("non-attribute getattr failure must be reported");
            assert!(err.to_string().contains("boom"), "unexpected error: {err}");
        });
    }

    // ---- Cache-key / credential-fingerprint isolation -------------------------
    //
    // Exercise the endpoint/credential/config key helpers on selected inputs.
    // Different sample digests are not proof of collision impossibility.
    // These tests do not construct drivers or verify service authentication.

    #[test]
    fn master_key_fingerprint_is_stable_for_equal_keys() {
        // Equal key strings produce the same fingerprint within this process.
        assert_eq!(
            master_key_fingerprint("secret-key").unwrap(),
            master_key_fingerprint("secret-key").unwrap()
        );
    }

    #[test]
    fn master_key_fingerprint_differs_for_different_keys() {
        // These two sample keys produce different fingerprints.
        assert_ne!(
            master_key_fingerprint("key-a").unwrap(),
            master_key_fingerprint("key-b").unwrap()
        );
    }

    #[test]
    fn master_key_fingerprint_does_not_leak_the_key() {
        // The sample key is not embedded verbatim. This is not a guarantee that
        // a credential-derived handle is safe to log.
        let key = "super-secret-master-key";
        let fp = master_key_fingerprint(key).unwrap();
        assert!(fp.starts_with("mk:"));
        assert_eq!(fp.len(), 3 + 64);
        assert!(!fp.contains(key));
    }

    #[test]
    fn master_key_and_token_fingerprints_never_collide() {
        // Distinct namespaces (mk: vs tc:) guarantee a master key and a token
        // credential can never produce the same fingerprint, even by chance.
        let master = master_key_fingerprint("anything").unwrap();
        let token = token_credential_fingerprint(0xDEAD_BEEF);
        assert!(master.starts_with("mk:"));
        assert!(token.starts_with("tc:"));
        assert_ne!(master, token);
    }

    #[test]
    fn token_credential_fingerprint_tracks_object_identity() {
        // Compare synthetic object addresses; no live Python credentials or
        // driver lifetimes are exercised.
        assert_eq!(
            token_credential_fingerprint(0x1000),
            token_credential_fingerprint(0x1000)
        );
        assert_ne!(
            token_credential_fingerprint(0x1000),
            token_credential_fingerprint(0x2000)
        );
    }

    #[test]
    fn config_fingerprint_is_stable_and_distinguishes() {
        let a = serde_json::json!({"preferred_locations": ["West US"]});
        let b = serde_json::json!({"preferred_locations": ["East US"]});
        assert_eq!(
            config_fingerprint_from_value(&a),
            config_fingerprint_from_value(&a)
        );
        assert_ne!(
            config_fingerprint_from_value(&a),
            config_fingerprint_from_value(&b)
        );
    }

    #[test]
    fn config_and_credential_fingerprints_never_collide() {
        // The cfg: namespace keeps a config fingerprint from ever matching a
        // credential one, so the three key parts stay independent.
        let cfg = config_fingerprint_from_value(&serde_json::json!({}));
        assert!(cfg.starts_with("cfg:"));
        assert!(!cfg.starts_with("mk:"));
        assert!(!cfg.starts_with("tc:"));
    }

    #[test]
    fn cache_key_separates_endpoint_credential_and_config() {
        let endpoint = "https://acct.documents.azure.com";
        let cred_a = master_key_fingerprint("key-a").unwrap();
        let cred_b = master_key_fingerprint("key-b").unwrap();
        let cfg_a = config_fingerprint_from_value(&serde_json::json!({"value": "a"}));
        let cfg_b = config_fingerprint_from_value(&serde_json::json!({"value": "b"}));

        // Equal endpoint and fingerprint strings produce an equal cache key.
        assert_eq!(
            compose_cache_key(endpoint, &cred_a, &cfg_a),
            compose_cache_key(endpoint, &cred_a, &cfg_a)
        );
        // Changing this sample credential fingerprint changes the key.
        assert_ne!(
            compose_cache_key(endpoint, &cred_a, &cfg_a),
            compose_cache_key(endpoint, &cred_b, &cfg_a)
        );
        // Changing this sample config fingerprint changes the key.
        assert_ne!(
            compose_cache_key(endpoint, &cred_a, &cfg_a),
            compose_cache_key(endpoint, &cred_a, &cfg_b)
        );
        // A different endpoint -> different key.
        assert_ne!(
            compose_cache_key(endpoint, &cred_a, &cfg_a),
            compose_cache_key("https://other.documents.azure.com", &cred_a, &cfg_a)
        );
    }

    #[test]
    fn cache_key_length_prefix_prevents_component_aliasing() {
        assert_ne!(
            compose_cache_key("ab", "c", "d"),
            compose_cache_key("a", "bc", "d")
        );
        assert_ne!(
            compose_cache_key("a", "b", "cd"),
            compose_cache_key("a", "bc", "d")
        );
        assert_ne!(
            compose_cache_key("a\u{1f}b", "c", "d"),
            compose_cache_key("a", "b\u{1f}c", "d")
        );
    }

    #[test]
    fn driver_identity_canonicalizes_endpoint_without_erasing_path_or_query() {
        let base = super::driver_identity("https://acct.example", Some("key"), None, None).unwrap();
        assert_eq!(base.len(), "driver:".len() + 64);
        assert!(!base.contains("acct") && !base.contains("key"));
        for endpoint in ["https://acct.example/", "https://ACCT.example:443"] {
            assert_eq!(
                base,
                super::driver_identity(endpoint, Some("key"), None, None).unwrap()
            );
        }
        for endpoint in [
            "https://acct.example/path",
            "https://acct.example?route=other",
        ] {
            assert_ne!(
                base,
                super::driver_identity(endpoint, Some("key"), None, None).unwrap()
            );
        }
    }

    #[test]
    fn concurrent_runtime_initializers_release_the_python_lock_while_waiting() {
        pyo3::prepare_freethreaded_python();
        let barrier = std::sync::Arc::new(std::sync::Barrier::new(4));
        let (sender, receiver) = std::sync::mpsc::channel();
        let mut workers = Vec::new();
        for _ in 0..4 {
            let barrier = barrier.clone();
            let sender = sender.clone();
            workers.push(std::thread::spawn(move || {
                barrier.wait();
                let address = Python::with_gil(|py| {
                    super::runtime_context(py, RuntimeSettings::default())
                        .unwrap()
                        .tokio_rt as *const tokio::runtime::Runtime as usize
                });
                sender.send(address).unwrap();
            }));
        }
        let first = receiver.recv_timeout(Duration::from_secs(5)).unwrap();
        for _ in 1..4 {
            assert_eq!(
                first,
                receiver.recv_timeout(Duration::from_secs(5)).unwrap()
            );
        }
        for worker in workers {
            worker.join().unwrap();
        }
    }

    #[test]
    fn driver_work_uses_the_async_bridge_executor() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let context = super::runtime_context(py, RuntimeSettings::default()).unwrap();
            assert!(std::ptr::eq(
                context.tokio_rt,
                pyo3_async_runtimes::tokio::get_runtime()
            ));
        });
    }
}

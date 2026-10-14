// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Acquire and release CosmosDriver objects for the Python wrapper.
//!
//! A customer app reading database "sales" needs that read to use its account
//! address, credential, and applicable client settings. The Python wrapper
//! retains those inputs and passes them to this binding module.
//!
//! A CosmosDriver is an object supplied by the separately owned Rust driver
//! library, configured for an account and used to perform operations. When a
//! new object is needed, the binding prepares the library's configuration from
//! the supplied inputs and asks the library to create it.
//!
//! The configuration combines:
//!   - account address: which Cosmos DB account to access
//!   - credential: authentication information for that account
//!   - applicable client settings: for example, a preferred region
//!
//! Preferred region is an optional client setting, not a separate required
//! input category. Database, container, and item identifiers belong to
//! individual operation calls; the object is not specific to database "sales"
//! or container "orders".
//!
//! Two matching clients can reuse a CosmosDriver object rather than build one
//! each. The binding computes a driver identity from the endpoint, credential,
//! and PreparedClientConfig fields, then adds the selected runtime identity.
//! It returns that cache key to Python in its role as a driver handle.
//! Each acquisition adds to the entry's count; a balanced final release removes
//! the entry. An active operation can still retain the CosmosDriver afterward.
//!
//! Reading database "sales" requires communication with the service backend.
//! The account address, credential, and client settings describe the account
//! access; they are not the connections used to perform it.
//!
//! The binding selects the client's explicit CosmosDriverRuntime or the default
//! singleton from driver_runtime.rs. Connection settings belong to that runtime,
//! not to the client acquiring a driver. Runtime identity participates in driver
//! reuse: separately created runtimes never receive each other's cached drivers.
//!
//! RuntimeContext retains only the shared Tokio executor. Creating a custom
//! driver runtime does not create another executor. Each CosmosDriver retains
//! its selected driver runtime independently of the Python runtime object.
//!
//! Preferred regions and driver operation defaults are prepared separately for
//! DriverOptions. See docs/V5/VOCABULARY.md for the object names and
//! docs/V5/use-cases/01-cosmos-client-creation.md for the ownership walkthrough.

use std::collections::{BTreeMap, HashMap};
use std::sync::{Arc, OnceLock};
use std::time::Duration;

use azure_core::http::headers::{HeaderName, HeaderValue};
use parking_lot::RwLock;
use pyo3::exceptions::{PyAttributeError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use sha2::{Digest, Sha256};

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    fault_injection::{
        CustomResponseBuilder, FaultInjectionConditionBuilder, FaultInjectionErrorType,
        FaultInjectionResultBuilder, FaultInjectionRule, FaultInjectionRuleBuilder, FaultOperationType,
    },
    models::AccountReference,
    options::{
        AvailabilityStrategy, DriverOptions, EndToEndOperationLatencyPolicy, ExcludedRegions,
        HedgeThreshold, HedgingStrategy, OperationOptions, OperationOptionsBuilder,
        PartitionFailoverOptions, PartitionFailoverOptionsBuilder, PartitionTopologyCacheMode,
        ReadConsistencyStrategy, Region, ThrottlingRetryOptionsBuilder, UserAgentSuffix,
    },
};
use tokio::runtime::Runtime as TokioRuntime;
use url::Url;

use crate::credential::PyTokenCredential;
use crate::driver_runtime::{default_runtime, RuntimeHandle};

// ---------------------------------------------------------------------------
// Per-process singletons
// ---------------------------------------------------------------------------

/// Retain the shared executor, independently of the selected driver runtime.
pub(crate) struct RuntimeContext {
    pub(crate) tokio_rt: &'static TokioRuntime,
}

/// One cached CosmosDriver, its fault rules, and its outstanding acquisition count.
///
/// The key includes runtime identity, endpoint, credential, and config fingerprints because drivers
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
// Cache key: (endpoint, credential, config, runtime identity)
// ---------------------------------------------------------------------------
//
// * Account keys use process-salted SHA-256. Handles remain private identifiers,
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
/// tag distinguishes it from an account-key fingerprint.
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
                "status_code": item.getattr("status_code")?.extract::<Option<u16>>()?,
                "error_type": get_config_opt::<String>(item, "error_type")?,
                "response_body": get_config_opt::<Vec<u8>>(item, "response_body")?.unwrap_or_default(),
                "response_headers": fault_response_headers_from_config(item)?,
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
        "operation_timeout_seconds": finite(field!("operation_timeout_seconds", f64), "operation_timeout_seconds")?,
        "fault_injection_rules": rules,
        "headers": client_headers_from_config(config)?,
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

/// Compute the driver identity without initializing RuntimeContext,
/// acquiring a CosmosDriver reference, or asking the credential for a token.
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

const AUTH_REQUIRED_ERROR: &str =
    "acquire_driver_handle requires either a master_key or a token credential";
const AUTH_EXCLUSIVE_ERROR: &str =
    "acquire_driver_handle received both master_key and token credential; exactly one must be set";

/// Require exactly one credential input: account key or Python token credential.
/// Reject both or neither rather than silently choosing an authentication path.
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

static RUNTIME_CONTEXT: OnceLock<RuntimeContext> = OnceLock::new();
static DRIVERS: OnceLock<RwLock<HashMap<String, DriverEntry>>> = OnceLock::new();

/// Return the driver cache, creating the empty table if needed.
/// Each driver identity maps to a CosmosDriver object and its acquisition count.
/// Creating this table alone does not create CosmosDriverRuntime or a driver.
pub(crate) fn drivers() -> &'static RwLock<HashMap<String, DriverEntry>> {
    DRIVERS.get_or_init(|| RwLock::new(HashMap::new()))
}

pub(crate) fn runtime_context() -> &'static RuntimeContext {
    RUNTIME_CONTEXT.get_or_init(|| RuntimeContext {
        tokio_rt: pyo3_async_runtimes::tokio::get_runtime(),
    })
}

/// Reject retired client-level network configuration without initializing a runtime.
#[pyfunction(name = "_validate_runtime_configuration")]
#[pyo3(signature = (config=None))]
pub(crate) fn validate_runtime_configuration(config: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
    if let Some(config) = config {
        for name in ["connection_timeout_seconds", "read_timeout_seconds", "proxy_allowed"] {
            match config.getattr(name) {
                Ok(value) if !value.is_none() => {
                    return Err(PyValueError::new_err(format!(
                        "{name} is not a client setting; use CosmosRuntime with ConnectionPoolOptions. \
                         Read-inactivity timeouts are not supported."
                    )));
                }
                Ok(_) => {}
                Err(error) if error.is_instance_of::<PyAttributeError>(config.py()) => {}
                Err(error) => return Err(error),
            }
        }
    }
    Ok(())
}

/// Return an initialized RuntimeContext without creating it.
/// Operation helpers use its Tokio runtime. Missing initialization raises an
/// error naming the required acquisition step.
pub(crate) fn require_runtime_context(op_name: &str) -> PyResult<&'static RuntimeContext> {
    match RUNTIME_CONTEXT.get() {
        Some(ctx) => Ok(ctx),
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
pub(crate) fn runtime_configuration() -> Option<(f64, f64, f64)> {
    crate::driver_runtime::default_configuration()
}

/// Acquire a CosmosDriver object and return a driver handle for later binding calls.
/// The Python adapter requests this on first use. This function does not enforce
/// one acquisition per Python client.
///
/// A cache hit increments its count. On a miss, build outside the cache lock,
/// then cache the CosmosDriver or use the entry another caller inserted meanwhile.
/// CosmosDriverRuntime is selected explicitly or from the default singleton;
/// preferred regions and driver operation defaults belong in DriverOptions.
///
/// Exactly one of `master_key` and Python `credential` must be present.
/// PyTokenCredential handles a synchronous credential or AsyncTokenCredentialBridge.

#[pyfunction]
#[pyo3(signature = (endpoint, master_key=None, config=None, credential=None, runtime=None))]
pub(crate) fn acquire_driver_handle(
    py: Python<'_>,
    endpoint: &str,
    master_key: Option<&str>,
    config: Option<&Bound<'_, PyAny>>,
    credential: Option<&Bound<'_, PyAny>>,
    runtime: Option<PyRef<'_, RuntimeHandle>>,
) -> PyResult<String> {
    validate_auth_inputs(master_key, credential)?;

    let endpoint_url = Url::parse(endpoint)
        .map_err(|e| PyValueError::new_err(format!("invalid endpoint URL: {e}")))?;

    validate_runtime_configuration(config)?;
    let runtime_ctx = runtime_context();
    let selected_runtime = match runtime {
        Some(runtime) => runtime.clone(),
        None => py.allow_threads(|| runtime_ctx.tokio_rt.block_on(default_runtime()))?,
    };

    let driver_handle = format!(
        "{}:runtime-{}",
        driver_identity(endpoint, master_key, config, credential)?,
        selected_runtime.id
    );

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

    // No matching CosmosDriver was cached. Prepare the account without holding the
    // cache lock; token authentication uses PyTokenCredential to call Python.
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
            AccountReference::with_account_key(endpoint_url, key.to_string())
        }
    };

    // Combine the account address, credential, and applicable client settings
    // into the options used to create a CosmosDriver. Preferred regions are
    // one example of those settings; connection settings are applied separately
    // to CosmosDriverRuntime.
    let driver_options = {
        let mut builder = DriverOptions::builder(account)
            .with_operation_options(operation_options)
            .with_partition_failover_options(partition_failover_options()?);
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

    // Build the CosmosDriver on the Tokio runtime, then wait on the task's
    // handle with the GIL released. Concurrent acquisitions can submit separate
    // build tasks. Join failures are mapped to Python errors below.
    let driver_runtime = Arc::clone(&selected_runtime.driver_runtime);
    let build_task = runtime_ctx
        .tokio_rt
        .spawn(async move { driver_runtime.create_driver(driver_options).await });
    let driver = py
        .allow_threads(|| runtime_ctx.tokio_rt.block_on(build_task))
        .map_err(|join_error| {
            PyRuntimeError::new_err(format!("driver init task failed: {join_error}"))
        })?
        .map_err(|e| PyRuntimeError::new_err(format!("driver init failed: {e}")))?;

    // If another acquisition already cached a matching CosmosDriver, reuse it.
    // Drop our surplus object after releasing the lock so its cleanup cannot
    // run while the driver cache is locked.
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
    // Drop any surplus CosmosDriver after releasing the cache lock.
    drop(surplus_driver);

    Ok(driver_handle)
}

pub(crate) fn partition_failover_options() -> PyResult<PartitionFailoverOptions> {
    // Preserve container resolution without eagerly fetching the physical map.
    PartitionFailoverOptionsBuilder::new()
        .with_partition_topology_cache_mode(PartitionTopologyCacheMode::Lazy)
        .build()
        .map_err(|error| PyValueError::new_err(format!("invalid partition failover settings: {error}")))
}


/// Convert PreparedClientConfig.preferred_locations into Rust driver Region values.
/// For example, the tuple ("West US",) supplies one Region::from("West US").
/// Reject blank names; a missing attribute or None yields an empty list.
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

/// Convert an optional prepared suffix to the Rust driver's UserAgentSuffix.
/// Missing, None, or empty means no suffix. Use try_new so a value rejected by
/// the Rust driver's length or character rules raises ValueError rather than
/// panicking across the binding call.
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

fn fault_response_headers_from_config(rule: &Bound<'_, PyAny>) -> PyResult<BTreeMap<String, String>> {
    let mut headers = BTreeMap::new();
    if let Some(value) = get_config_opt::<PyObject>(rule, "response_headers")? {
        for pair in value.bind(rule.py()).call_method0("items")?.iter()? {
            let (name, value) = pair?.extract::<(String, String)>()?;
            if name.is_empty()
                || !name.bytes().all(|c| c.is_ascii_alphanumeric() || b"!#$%&'*+-.^_`|~".contains(&c))
                || value.chars().any(|c| (c < ' ' && c != '\t') || c == '\u{7f}')
            {
                return Err(PyValueError::new_err("fault rule response_headers contains an invalid header"));
            }
            let name = name.to_ascii_lowercase();
            if name == "x-ms-substatus" {
                return Err(PyValueError::new_err("fault rule response_headers must use sub_status instead of x-ms-substatus"));
            }
            if headers.insert(name, value).is_some() {
                return Err(PyValueError::new_err("fault rule response_headers contains duplicate case-insensitive names"));
            }
        }
    }
    Ok(headers)
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

        let status_code: Option<u16> = item.getattr("status_code")?.extract()?;
        let sub_status: u16 = item.getattr("sub_status")?.extract()?;
        let error_type = get_config_opt::<String>(&item, "error_type")?;
        let response_body = get_config_opt::<Vec<u8>>(&item, "response_body")?.unwrap_or_default();
        let response_headers = fault_response_headers_from_config(&item)?;
        if error_type.is_some() && !response_body.is_empty() {
            return Err(PyValueError::new_err(
                "fault rule response_body requires status_code, not error_type",
            ));
        }
        if error_type.is_some() && !response_headers.is_empty() {
            return Err(PyValueError::new_err(
                "fault rule response_headers requires status_code, not error_type",
            ));
        }
        let delay_ms: u64 = item.getattr("delay_ms")?.extract()?;
        let probability: f32 = item.getattr("probability")?.extract()?;
        let mut result = FaultInjectionResultBuilder::new().with_probability(probability);
        result = match (status_code, error_type.as_deref()) {
            (Some(status), None) if (100..=599).contains(&status) => {
                let mut response =
                    CustomResponseBuilder::new(azure_core::http::StatusCode::from(status));
                if sub_status != 0 {
                    response = response.with_sub_status(sub_status);
                }
                for (name, value) in response_headers {
                    response = response.with_header(name, value);
                }
                result.with_custom_response(response.with_body(response_body).build())
            }
            (None, Some("ConnectionError")) if sub_status == 0 => {
                result.with_error(FaultInjectionErrorType::ConnectionError)
            }
            (None, Some("ResponseTimeout")) if sub_status == 0 => {
                result.with_error(FaultInjectionErrorType::ResponseTimeout)
            }
            _ => return Err(PyValueError::new_err(
                "fault rule requires status_code 100..599 or error_type ConnectionError/ResponseTimeout, not both; transport errors cannot have sub_status",
            )),
        };
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

/// Build Rust driver OperationOptions from PreparedClientConfig's operation
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
    if let Some(value) = get_config_opt::<PyObject>(config, "operation_timeout_seconds")? {
        if value.bind(config.py()).is_instance_of::<pyo3::types::PyBool>() {
            return Err(PyValueError::new_err("timeout must be numeric, not bool"));
        }
        let seconds: f64 = value.bind(config.py()).extract()?;
        let timeout = Duration::try_from_secs_f64(seconds)
            .map_err(|_| PyValueError::new_err("timeout must be finite seconds within range"))?;
        if timeout < Duration::from_secs(1) {
            return Err(PyValueError::new_err("timeout must be at least one second"));
        }
        builder = builder.with_end_to_end_latency_policy(EndToEndOperationLatencyPolicy::new(timeout));
    }
    let headers = client_headers_from_config(Some(config))?;
    if !headers.is_empty() {
        builder = builder.with_custom_headers(
            headers
                .into_iter()
                .map(|(name, value)| (HeaderName::from(name), HeaderValue::from(value)))
                .collect(),
        );
    }

    // Convert excluded_locations to the same ExcludedRegions type used by
    // per-operation settings.
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
    // customer app enabled hedging (availability_strategy True / dict). The
    // Python wrapper validates threshold_ms > 0; reject an invalid hand-built config too.
    if let Some(threshold_ms) = get_config_opt::<u64>(config, "hedging_threshold_ms")? {
        let threshold = HedgeThreshold::new(Duration::from_millis(threshold_ms))
            .ok_or_else(|| PyValueError::new_err("hedging_threshold_ms must be positive"))?;
        builder = builder.with_availability_strategy(AvailabilityStrategy::Hedging(
            HedgingStrategy::new(threshold),
        ));
    }

    // consistency_level -> ReadConsistencyStrategy. Set only when the customer app
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

fn client_headers_from_config(config: Option<&Bound<'_, PyAny>>) -> PyResult<BTreeMap<String, String>> {
    let mut headers = BTreeMap::new();
    if let Some(config) = config {
        if let Some(value) = get_config_opt::<PyObject>(config, "headers")? {
            for pair in value.bind(config.py()).call_method0("items")?.iter()? {
                let (name, value) = pair?.extract::<(String, String)>()?;
                crate::wire::settings::reject_trigger_header(&name)?;
                headers.insert(name.to_ascii_lowercase(), value);
            }
        }
    }
    Ok(headers)
}

/// Map a Python consistency-level string to the driver's `ReadConsistencyStrategy`.
///
/// This binding maps `"Eventual"` and `"Session"` directly, and `"Strong"` to
/// `GlobalStrong`. Any other string returns `None` for the caller to reject.
pub(crate) fn read_consistency_from_str(level: &str) -> Option<ReadConsistencyStrategy> {
    match level {
        "Eventual" => Some(ReadConsistencyStrategy::Eventual),
        "Session" => Some(ReadConsistencyStrategy::Session),
        "Strong" => Some(ReadConsistencyStrategy::GlobalStrong),
        _ => None,
    }
}

/// Read an optional PreparedClientConfig attribute.
/// Missing or None yields Ok(None); a wrongly typed value raises ValueError.
pub(crate) fn get_config_opt<'py, T>(config: &Bound<'py, PyAny>, attr: &str) -> PyResult<Option<T>>
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

/// Toggle only an explicitly configured rule; callers must use isolated rule IDs.
// PyO3 generates the identity PyErr conversion in the Python-call wrapper.
#[allow(clippy::useless_conversion)]
#[pyfunction]
pub(crate) fn _debug_set_fault_injection_rule_enabled(
    driver_handle: &str,
    rule_id: &str,
    enabled: bool,
) -> PyResult<()> {
    let cache = drivers().read();
    let entry = cache
        .get(driver_handle)
        .ok_or_else(|| PyValueError::new_err("unknown or closed Rust client handle"))?;
    let rule = entry.fault_rules.get(rule_id).ok_or_else(|| {
        PyValueError::new_err(format!("unknown fault injection rule id: {rule_id:?}"))
    })?;
    if enabled {
        rule.enable();
    } else {
        rule.disable();
    }
    Ok(())
}

/// Inspect already-cached regions without causing a metadata request.
#[pyfunction]
pub(crate) fn _debug_cached_account_regions(
    py: Python<'_>,
    driver_handle: &str,
) -> PyResult<Option<(Vec<String>, Vec<String>)>> {
    let driver = drivers()
        .read()
        .get(driver_handle)
        .map(|entry| Arc::clone(&entry.driver))
        .ok_or_else(|| PyValueError::new_err("unknown or closed Rust client handle"))?;
    let runtime = require_runtime_context("inspect cached account regions")?;
    Ok(py.allow_threads(|| {
        runtime.tokio_rt.block_on(async {
            driver.cached_account_regions_for_testing().await.map(|(writes, reads)| {
                (
                    writes.iter().map(|region| region.as_str().to_owned()).collect(),
                    reads.iter().map(|region| region.as_str().to_owned()).collect(),
                )
            })
        })
    }))
}

#[cfg(test)]
mod tests {
    use super::{
        apply_close, compose_cache_key, config_fingerprint_from_value,
        get_config_opt, master_key_fingerprint,
        operation_options_from_config, read_consistency_from_str,
        token_credential_fingerprint, validate_auth_inputs,
        AUTH_EXCLUSIVE_ERROR,
        AUTH_REQUIRED_ERROR,
    };

    #[test]
    fn fault_wait_budget_config_preserves_fractional_seconds() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let config = PyModule::import_bound(py, "types").unwrap()
                .getattr("SimpleNamespace").unwrap().call0().unwrap();
            config.setattr("throttling_max_retry_count", 5).unwrap();
            for (seconds, milliseconds) in [(2.5, 2500), (10.0, 10000)] {
                config.setattr("throttling_max_retry_wait_time_seconds", seconds).unwrap();
                let options = operation_options_from_config(Some(&config)).unwrap();
                let throttle = options.throttling_retry_options.unwrap();
                assert_eq!(throttle.max_retry_count, Some(5));
                assert_eq!(throttle.max_retry_wait_time, Some(Duration::from_millis(milliseconds)));
            }
        });
    }

    #[test]
    fn fault_response_headers_are_forwarded_and_isolate_cached_drivers() {
        use super::{config_fingerprint, fault_rules_from_config};
        use azure_core::http::headers::HeaderName;

        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = PyModule::from_code_bound(
                py,
                r#"
from types import MappingProxyType, SimpleNamespace
headers = {"X-MS-Retry-After-MS": "1000", "x-test": "value"}
rule = SimpleNamespace(
    id="wait", operation_type="ReadItem", status_code=429, sub_status=17,
    container_id="orders", region=None, delay_ms=0, probability=1.0,
    hit_limit=None, enabled=True, response_headers=MappingProxyType(headers))
config = SimpleNamespace(fault_injection_rules=(rule,))
equivalent = {"x-test": "value", "x-ms-retry-after-ms": "1000"}
invalid = [
    {"": "value"}, {"bad name": "value"}, {"bad:header": "value"},
    {"x-test": "bad\r\nvalue"}, {"x-test": "\x00"}, {"x-test": "\x7f"},
    {"x-test": "1", "X-Test": "2"}, {"X-MS-Substatus": "1"},
]
"#,
                "fault_headers.py",
                "fault_headers",
            ).unwrap();
            let config = module.getattr("config").unwrap();
            let rule = module.getattr("rule").unwrap();
            let first = config_fingerprint(Some(&config)).unwrap();
            let rules = fault_rules_from_config(&config).unwrap();
            let response = rules[0].result().custom_response().unwrap();
            assert_eq!(u16::from(response.status_code()), 429);
            assert_eq!(response.headers().get_optional_str(&HeaderName::from_static("x-ms-retry-after-ms")), Some("1000"));
            assert_eq!(response.headers().get_optional_str(&HeaderName::from_static("x-ms-substatus")), Some("17"));
            assert!(rules[0].result().delay().is_none());
            rule.setattr("response_headers", module.getattr("equivalent").unwrap()).unwrap();
            assert_eq!(first, config_fingerprint(Some(&config)).unwrap());
            let headers = rule.getattr("response_headers").unwrap();
            headers.set_item("x-ms-retry-after-ms", "2000").unwrap();
            assert_ne!(first, config_fingerprint(Some(&config)).unwrap());
            let changed = fault_rules_from_config(&config).unwrap();
            assert_eq!(
                changed[0].result().custom_response().unwrap().headers()
                    .get_optional_str(&HeaderName::from_static("x-ms-retry-after-ms")),
                Some("2000"),
            );
            for invalid in module.getattr("invalid").unwrap().iter().unwrap() {
                rule.setattr("response_headers", invalid.unwrap()).unwrap();
                assert!(fault_rules_from_config(&config).is_err());
                assert!(config_fingerprint(Some(&config)).is_err());
            }
            rule.setattr("response_headers", headers).unwrap();
            rule.setattr("status_code", py.None()).unwrap();
            rule.setattr("sub_status", 0).unwrap();
            for error_type in ["ConnectionError", "ResponseTimeout"] {
                rule.setattr("error_type", error_type).unwrap();
                assert!(fault_rules_from_config(&config).unwrap_err().to_string().contains("response_headers"));
            }
        });
    }

    #[test]
    fn fault_response_body_is_preserved_and_changes_driver_identity() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = PyModule::from_code_bound(py, r#"
from types import SimpleNamespace
rule = SimpleNamespace(
    id="topology", operation_type="MetadataReadDatabaseAccount",
    status_code=200, sub_status=0, container_id=None, region=None,
    delay_ms=0, probability=1.0, hit_limit=None, enabled=True,
    response_body=b'{"id":"first"}')
config = SimpleNamespace(fault_injection_rules=(rule,))
"#, "fault_body.py", "fault_body").unwrap();
            let config = module.getattr("config").unwrap();
            let rule = module.getattr("rule").unwrap();
            let before = super::config_fingerprint(Some(&config)).unwrap();
            let rules = super::fault_rules_from_config(&config).unwrap();
            assert_eq!(
                rules[0].result().custom_response().unwrap().body(),
                br#"{"id":"first"}"#
            );
            rule.setattr("response_body", pyo3::types::PyBytes::new_bound(py, br#"{"id":"second"}"#)).unwrap();
            assert_ne!(before, super::config_fingerprint(Some(&config)).unwrap());
            rule.setattr("status_code", py.None()).unwrap();
            rule.setattr("error_type", "ConnectionError").unwrap();
            assert!(super::fault_rules_from_config(&config).is_err());
        });
    }
    use azure_data_cosmos_driver::options::{
        AvailabilityStrategy, HedgeThreshold, HedgingStrategy, OperationOptionsBuilder,
        OperationOptionsView, ReadConsistencyStrategy,
    };
    use pyo3::exceptions::PyValueError;
    use pyo3::prelude::*;
    use pyo3::types::{PyModule, PyString};
    use std::time::Duration;

    #[test]
    fn client_headers_configure_driver_and_isolate_cached_clients() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let config = py.import_bound("types").unwrap()
                .getattr("SimpleNamespace").unwrap().call0().unwrap();
            let headers = pyo3::types::PyDict::new_bound(py);
            headers.set_item("X-Application", "first").unwrap();
            config.setattr("headers", &headers).unwrap();
            let first = super::config_fingerprint(Some(&config)).unwrap();
            let options = operation_options_from_config(Some(&config)).unwrap();
            assert_eq!(options.custom_headers.unwrap()[
                &azure_core::http::headers::HeaderName::from_static("x-application")
            ].as_str(), "first");
            headers.clear();
            headers.set_item("x-application", "first").unwrap();
            assert_eq!(first, super::config_fingerprint(Some(&config)).unwrap());
            headers.set_item("x-application", "second").unwrap();
            assert_ne!(first, super::config_fingerprint(Some(&config)).unwrap());
            for name in [
                "X-MS-DOCUMENTDB-PRE-TRIGGER-INCLUDE",
                "x-ms-documentdb-post-trigger-include",
            ] {
                headers.clear();
                headers.set_item(name, "validateOrder").unwrap();
                assert!(super::config_fingerprint(Some(&config)).is_err());
                assert!(operation_options_from_config(Some(&config)).is_err());
            }
        });
    }

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

    #[tokio::test]
    async fn fault_rule_toggle_is_scoped_and_rejects_unknown_or_closed_handles() {
        use azure_data_cosmos_driver::{
            fault_injection::{
                FaultInjectionErrorType, FaultInjectionResultBuilder, FaultInjectionRuleBuilder,
            },
            in_memory_emulator::{InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion},
            models::AccountReference,
            options::DriverOptions,
        };
        use std::{collections::HashMap, sync::Arc};
        use url::Url;

        pyo3::prepare_freethreaded_python();
        let endpoint = Url::parse("https://toggle.emulator.local").unwrap();
        let config =
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", endpoint.clone())])
                .unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(config));
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_account_key(
                    endpoint,
                    "ZW11bGF0b3Ita2V5",
                ))
                .build(),
            )
            .await
            .unwrap();
        let rules: Vec<_> = ["selected", "other"]
            .into_iter()
            .map(|id| {
                let rule = Arc::new(
                    FaultInjectionRuleBuilder::new(
                        id,
                        FaultInjectionResultBuilder::new()
                            .with_error(FaultInjectionErrorType::Timeout)
                            .build(),
                    )
                    .build(),
                );
                rule.disable();
                rule
            })
            .collect();
        let handle = "fault-rule-toggle-scoping-test";
        super::drivers().write().insert(
            handle.into(),
            super::DriverEntry {
                driver,
                fault_rules: rules
                    .iter()
                    .map(|rule| (rule.id().to_owned(), Arc::clone(rule)))
                    .collect::<HashMap<_, _>>(),
                refcount: 1,
            },
        );
        for enabled in [true, true, false, false] {
            super::_debug_set_fault_injection_rule_enabled(handle, "selected", enabled).unwrap();
            assert_eq!(rules[0].is_enabled(), enabled);
            assert!(!rules[1].is_enabled());
            assert_eq!(rules[0].hit_count(), 0);
        }
        assert!(super::_debug_set_fault_injection_rule_enabled(handle, "missing", true).is_err());
        super::release_driver_handle(handle).unwrap();
        assert!(super::_debug_set_fault_injection_rule_enabled(handle, "selected", true).is_err());
        assert!(!rules[0].is_enabled());
    }

    #[tokio::test]
    async fn release_preserves_other_clients_and_operation_references() {
        use azure_data_cosmos_driver::{
            in_memory_emulator::{InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion},
            models::AccountReference,
            options::DriverOptions,
        };
        use std::{collections::HashMap, sync::Arc};
        use url::Url;

        let endpoint = Url::parse("https://close.emulator.local").unwrap();
        let config =
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", endpoint.clone())])
                .unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(config));
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let account = AccountReference::with_account_key(endpoint, "ZW11bGF0b3Ita2V5");
        let driver = runtime
            .create_driver(DriverOptions::builder(account).build())
            .await
            .unwrap();
        let weak_driver = Arc::downgrade(&driver);
        let handle = "close-reference-lifetime-test";
        super::drivers().write().insert(
            handle.to_string(),
            super::DriverEntry {
                driver,
                fault_rules: HashMap::new(),
                refcount: 2,
            },
        );

        super::release_driver_handle(handle).unwrap();
        let operation_driver = {
            let cache = super::drivers().read();
            let entry = cache.get(handle).unwrap();
            assert_eq!(entry.refcount, 1);
            Arc::clone(&entry.driver)
        };
        super::release_driver_handle(handle).unwrap();
        assert!(!super::drivers().read().contains_key(handle));
        assert!(weak_driver.upgrade().is_some());

        super::release_driver_handle(handle).unwrap();
        assert!(weak_driver.upgrade().is_some());
        drop(operation_driver);
        assert!(weak_driver.upgrade().is_none());
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
    fn retired_client_network_settings_are_rejected_without_initialization() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = PyModule::from_code_bound(
                py,
                r#"
class Config:
    proxy_allowed = False
    connection_timeout_seconds = 1.25
"#,
                "runtime_settings_test.py",
                "runtime_settings_test",
            )
            .expect("module must compile");
            let config = module
                .getattr("Config")
                .and_then(|cls| cls.call0())
                .expect("Config() should construct");

            let error = super::validate_runtime_configuration(Some(&config)).unwrap_err();
            assert!(error.is_instance_of::<PyValueError>(py));
            assert!(error.to_string().contains("CosmosRuntime"));
            assert!(super::validate_runtime_configuration(None).is_ok());
        });
    }

    #[test]
    fn fault_transport_errors_preserve_response_rules_and_cache_isolation() {
        use super::{config_fingerprint, fault_rules_from_config, FaultInjectionErrorType};
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = PyModule::from_code_bound(
                py,
                r#"
from types import SimpleNamespace
rule = SimpleNamespace(
    id="rule", operation_type="CreateItem", status_code=502, sub_status=0,
    container_id="orders", region=None, delay_ms=2000, probability=1.0,
    hit_limit=None, enabled=True)
config = SimpleNamespace(fault_injection_rules=(rule,))
"#,
                "fault_config_test.py",
                "fault_config_test",
            )
            .unwrap();
            let config = module.getattr("config").unwrap();
            let rule = module.getattr("rule").unwrap();
            let before = config_fingerprint(Some(&config)).unwrap();
            let rules = fault_rules_from_config(&config).unwrap();
            assert!(rules[0].result().error_type().is_none());
            assert_eq!(
                u16::from(rules[0].result().custom_response().unwrap().status_code()),
                502
            );
            rule.setattr("error_type", "ConnectionError").unwrap();
            assert!(fault_rules_from_config(&config).is_err());
            rule.setattr("status_code", py.None()).unwrap();
            let rules = fault_rules_from_config(&config).unwrap();
            assert_eq!(
                rules[0].result().error_type(),
                Some(FaultInjectionErrorType::ConnectionError)
            );
            assert!(rules[0].result().custom_response().is_none());
            assert_eq!(rules[0].result().delay(), Some(Duration::from_secs(2)));
            let connection_fingerprint = config_fingerprint(Some(&config)).unwrap();
            assert_ne!(before, connection_fingerprint);
            rule.setattr("error_type", "ResponseTimeout").unwrap();
            let rules = fault_rules_from_config(&config).unwrap();
            assert_eq!(rules[0].result().error_type(), Some(FaultInjectionErrorType::ResponseTimeout));
            assert!(rules[0].result().custom_response().is_none());
            assert_eq!(rules[0].result().delay(), Some(Duration::from_secs(2)));
            let response_fingerprint = config_fingerprint(Some(&config)).unwrap();
            assert_ne!(before, response_fingerprint);
            assert_ne!(connection_fingerprint, response_fingerprint);
            rule.setattr("status_code", 503).unwrap();
            assert!(fault_rules_from_config(&config).is_err());
            rule.setattr("status_code", py.None()).unwrap();
            rule.setattr("response_body", pyo3::types::PyBytes::new_bound(py, b"body")).unwrap();
            assert!(fault_rules_from_config(&config).is_err());
            rule.setattr("response_body", pyo3::types::PyBytes::new_bound(py, b"")).unwrap();
            rule.setattr("sub_status", 1).unwrap();
            assert!(fault_rules_from_config(&config).is_err());
            rule.setattr("sub_status", 0).unwrap();
            rule.setattr("error_type", "typo").unwrap();
            assert!(fault_rules_from_config(&config).is_err());
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
                let address = Python::with_gil(|_py| {
                    super::runtime_context()
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
        Python::with_gil(|_py| {
            let context = super::runtime_context();
            assert!(std::ptr::eq(
                context.tokio_rt,
                pyo3_async_runtimes::tokio::get_runtime()
            ));
        });
    }

    #[test]
    fn selected_runtime_scopes_driver_reuse_and_survives_python_owner_release() {
        use std::sync::Arc;
        use url::Url;
        use azure_data_cosmos_driver::in_memory_emulator::{
            InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion,
        };
        use crate::driver_runtime::RuntimeHandle;

        pyo3::prepare_freethreaded_python();
        let endpoint = Url::parse("https://runtime-ownership.emulator.local").unwrap();
        let config = VirtualAccountConfig::new(vec![VirtualRegion::new(
            "East US", endpoint.clone(),
        )]).unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(config));
        let executor = super::runtime_context().tokio_rt;
        let first = executor.block_on(emulator.runtime_builder().build()).unwrap();
        let second = executor.block_on(emulator.runtime_builder().build()).unwrap();
        let weak_first = Arc::downgrade(&first);
        Python::with_gil(|py| {
            let first = Py::new(py, RuntimeHandle::new(first)).unwrap();
            let second = Py::new(py, RuntimeHandle::new(second)).unwrap();
            let acquire = |runtime: &Py<RuntimeHandle>| {
                super::acquire_driver_handle(
                    py, endpoint.as_str(), Some("ZW11bGF0b3Ita2V5"), None, None,
                    Some(runtime.borrow(py)),
                ).unwrap()
            };
            let a = acquire(&first);
            let b = acquire(&first);
            let c = acquire(&second);
            assert_eq!(a, b);
            assert_ne!(a, c);
            assert_eq!(super::drivers().read().get(&a).unwrap().refcount, 2);
            drop(first);
            assert!(weak_first.upgrade().is_some());
            let operation_driver = Arc::clone(&super::drivers().read().get(&a).unwrap().driver);
            super::release_driver_handle(&a).unwrap();
            assert!(super::drivers().read().contains_key(&b));
            super::release_driver_handle(&b).unwrap();
            assert!(weak_first.upgrade().is_some());
            drop(operation_driver);
            assert!(weak_first.upgrade().is_none());
            super::release_driver_handle(&c).unwrap();
        });
    }

    #[test]
    fn client_overall_deadline_is_distinct_from_connection_settings() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = PyModule::from_code_bound(py,
                "from types import SimpleNamespace\nconfig = SimpleNamespace(operation_timeout_seconds=30)",
                "timeout_config.py", "timeout_config").unwrap();
            let config = module.getattr("config").unwrap();
            let options = operation_options_from_config(Some(&config)).unwrap();
            assert_eq!(options.end_to_end_latency_policy.as_ref().unwrap().timeout(), Duration::from_secs(30));
            let account = std::sync::Arc::new(options);
            let operation = OperationOptionsBuilder::new()
                .with_end_to_end_latency_policy(super::EndToEndOperationLatencyPolicy::new(Duration::from_secs(2)))
                .build();
            for (request, expected) in [(None, 30), (Some(&operation), 2), (None, 30)] {
                let view = OperationOptionsView::new(None, None, Some(account.clone()), request);
                assert_eq!(view.end_to_end_latency_policy().unwrap().timeout(), Duration::from_secs(expected));
            }
            let first_identity = super::driver_identity(
                "https://timeout.invalid", Some("key"), Some(&config), None).unwrap();
            config.setattr("operation_timeout_seconds", 2).unwrap();
            assert_ne!(first_identity, super::driver_identity(
                "https://timeout.invalid", Some("key"), Some(&config), None).unwrap());
            for invalid in [0.5, f64::NAN, f64::INFINITY] {
                config.setattr("operation_timeout_seconds", invalid).unwrap();
                assert!(operation_options_from_config(Some(&config)).is_err());
            }
        });
    }
}

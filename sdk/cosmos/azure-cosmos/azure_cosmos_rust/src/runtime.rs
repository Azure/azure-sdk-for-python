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
//! Python receives an opaque handle retaining that exact CosmosDriver, not its
//! cache key. Each acquisition adds to the entry's count; a balanced final
//! release removes the entry. Handles already held by operations keep the
//! original driver alive even before those operations enter the binding.
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
//! DriverOptions.

use std::collections::{BTreeMap, HashMap};
use std::sync::{Arc, OnceLock, Weak};
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::Duration;

use azure_core::http::headers::{HeaderName, HeaderValue};
use parking_lot::RwLock;
use pyo3::exceptions::{PyAttributeError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use sha2::{Digest, Sha256};

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    models::AccountReference,
    options::{
        AvailabilityStrategy, DriverOptions, EndToEndOperationLatencyPolicy, ExcludedRegions,
        HedgeThreshold, HedgingStrategy, OperationOptions, OperationOptionsBuilder,
        PartitionFailoverOptions, PartitionFailoverOptionsBuilder, PartitionTopologyCacheMode,
        ReadConsistencyStrategy, Region, ThrottlingRetryOptionsBuilder, UserAgentSuffix,
        Utf8DecodingMode,
    },
};
#[cfg(any(test, feature = "test-probes"))]
use azure_data_cosmos_driver::fault_injection::{
    CustomResponseBuilder, FaultInjectionConditionBuilder, FaultInjectionErrorType,
    FaultInjectionResultBuilder, FaultInjectionRule, FaultInjectionRuleBuilder, FaultOperationType,
};
use tokio::runtime::Runtime as TokioRuntime;
use tokio::sync::Mutex;
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

/// One cached CosmosDriver and its outstanding acquisition count.
///
/// The key includes runtime identity, endpoint, credential, and config fingerprints because drivers
/// retain authentication and settings. Keying only by endpoint would incorrectly
/// share those values between differently configured clients.
///
/// Each acquisition increases the count by one; releasing it decreases the count.
/// At zero, the cache entry is removed. Handles and operations may still keep
/// the driver alive independently of the cache.
pub(crate) struct DriverEntry {
    pub(crate) driver: Arc<CosmosDriver>,
    #[cfg(any(test, feature = "test-probes"))]
    fault_rules: HashMap<String, Arc<FaultInjectionRule>>,
    acquisition_count: usize,
}

/// Tracks one cache acquisition and keeps its driver alive.
/// Releasing the acquisition does not remove driver references already held by calls.
#[pyclass(frozen, module = "azure.cosmos._rust", name = "_DriverHandle")]
pub(crate) struct DriverHandle {
    key: String,
    driver: Arc<CosmosDriver>,
    #[cfg(any(test, feature = "test-probes"))]
    fault_rules: HashMap<String, Arc<FaultInjectionRule>>,
    released: AtomicBool,
}

impl DriverHandle {
    fn from_acquired_entry(key: String, entry: &DriverEntry) -> Self {
        Self {
            key,
            driver: Arc::clone(&entry.driver),
            #[cfg(any(test, feature = "test-probes"))]
            fault_rules: entry.fault_rules.clone(),
            released: AtomicBool::new(false),
        }
    }

    pub(crate) fn driver(&self) -> Arc<CosmosDriver> {
        Arc::clone(&self.driver)
    }

    pub(crate) fn cache_key(&self) -> &str {
        &self.key
    }

    #[cfg(any(test, feature = "test-probes"))]
    fn fault_rule(&self, rule_id: &str) -> PyResult<&Arc<FaultInjectionRule>> {
        if self.released.load(Ordering::Acquire) {
            return Err(PyValueError::new_err("closed Rust client handle"));
        }
        self.fault_rules.get(rule_id).ok_or_else(|| {
            PyValueError::new_err(format!("unknown fault injection rule id: {rule_id:?}"))
        })
    }

    fn release(&self) {
        if !self.released.swap(true, Ordering::AcqRel) {
            release_cached_driver(&self.key, Some(&self.driver));
        }
    }
}

impl Drop for DriverHandle {
    fn drop(&mut self) {
        self.release();
    }
}

/// Calculate the count after one release and whether to remove the cache entry.
/// Zero stays zero. `DriverHandle::release` ensures that each handle
/// decreases the count at most once.
fn apply_close(acquisition_count: usize) -> (usize, bool) {
    let next = acquisition_count.saturating_sub(1);
    (next, next == 0)
}

// ---------------------------------------------------------------------------
// Cache key: (endpoint, credential, config, runtime identity)
// ---------------------------------------------------------------------------
//
// * Account keys use process-salted SHA-256. Cache keys remain private identifiers,
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

/// Own every setting used for driver identity and construction before releasing the GIL.
/// Serializing this same snapshot keeps new settings in the identity automatically.
#[derive(Default, serde::Serialize)]
struct ClientSettings {
    preferred_locations: Vec<String>,
    excluded_locations: Vec<String>,
    throttling_max_retry_count: Option<u32>,
    throttling_max_retry_wait_time_seconds: Option<f64>,
    hedging_threshold_ms: Option<u64>,
    user_agent_suffix: Option<String>,
    consistency_level: Option<String>,
    utf8_decoding_mode: Option<String>,
    aad_scope_override: Option<String>,
    operation_timeout_seconds: Option<f64>,
    #[cfg(any(test, feature = "test-probes"))]
    fault_injection_rules: Vec<FaultRuleSettings>,
    headers: BTreeMap<String, String>,
}

#[derive(serde::Serialize)]
#[cfg(any(test, feature = "test-probes"))]
struct FaultRuleSettings {
    id: String,
    operation_type: String,
    status_code: Option<u16>,
    error_type: Option<String>,
    response_body: Vec<u8>,
    response_headers: BTreeMap<String, String>,
    sub_status: u16,
    container_id: Option<String>,
    region: Option<String>,
    delay_ms: u64,
    probability: f32,
    hit_limit: Option<u32>,
    enabled: bool,
}

impl ClientSettings {
    fn from_python(config: Option<&Bound<'_, PyAny>>) -> PyResult<Self> {
        validate_runtime_configuration(config)?;
        let Some(config) = config else {
            return Ok(Self::default());
        };
        let finite = |value: Option<f64>, name: &str| -> PyResult<Option<f64>> {
            if value.is_some_and(|value| !value.is_finite()) {
                return Err(PyValueError::new_err(format!("{name} must be finite")));
            }
            Ok(value.map(|value| if value == 0.0 { 0.0 } else { value }))
        };
        #[cfg(any(test, feature = "test-probes"))]
        let mut rules = Vec::new();
        #[cfg(any(test, feature = "test-probes"))]
        if let Some(items) = get_config_opt::<Vec<PyObject>>(config, "fault_injection_rules")? {
            for item in items {
                let item = item.bind(config.py());
                let probability: f32 = item.getattr("probability")?.extract()?;
                if !probability.is_finite() {
                    return Err(PyValueError::new_err("fault probability must be finite"));
                }
                rules.push(FaultRuleSettings {
                    id: item.getattr("id")?.extract()?,
                    operation_type: item.getattr("operation_type")?.extract()?,
                    status_code: item.getattr("status_code")?.extract()?,
                    error_type: get_config_opt(item, "error_type")?,
                    response_body: get_config_opt(item, "response_body")?.unwrap_or_default(),
                    response_headers: fault_response_headers_from_config(item)?,
                    sub_status: item.getattr("sub_status")?.extract()?,
                    container_id: item.getattr("container_id")?.extract()?,
                    region: item.getattr("region")?.extract()?,
                    delay_ms: item.getattr("delay_ms")?.extract()?,
                    probability,
                    hit_limit: item.getattr("hit_limit")?.extract()?,
                    enabled: item.getattr("enabled")?.extract()?,
                });
            }
        }
        Ok(Self {
            preferred_locations: get_config_opt(config, "preferred_locations")?.unwrap_or_default(),
            excluded_locations: get_config_opt(config, "excluded_locations")?.unwrap_or_default(),
            throttling_max_retry_count: get_numeric_config_opt(
                config,
                "throttling_max_retry_count",
            )?,
            throttling_max_retry_wait_time_seconds: finite(
                get_numeric_config_opt(config, "throttling_max_retry_wait_time_seconds")?,
                "throttling_max_retry_wait_time_seconds",
            )?,
            hedging_threshold_ms: get_config_opt(config, "hedging_threshold_ms")?,
            user_agent_suffix: get_config_opt::<String>(config, "user_agent_suffix")?
                .filter(|value| !value.is_empty()),
            consistency_level: get_config_opt(config, "consistency_level")?,
            utf8_decoding_mode: get_config_opt(config, "utf8_decoding_mode")?,
            aad_scope_override: get_config_opt::<String>(config, "aad_scope_override")?
                .filter(|value| !value.is_empty()),
            operation_timeout_seconds: finite(
                get_numeric_config_opt(config, "operation_timeout_seconds")?,
                "operation_timeout_seconds",
            )?,
            #[cfg(any(test, feature = "test-probes"))]
            fault_injection_rules: rules,
            headers: client_headers_from_config(Some(config))?,
        })
    }

    fn fingerprint(&self) -> PyResult<String> {
        let value = serde_json::to_value(self).map_err(|error| {
            PyRuntimeError::new_err(format!("invalid client settings identity: {error}"))
        })?;
        Ok(config_fingerprint_from_value(&value))
    }
}

fn get_numeric_config_opt<'py, T>(config: &Bound<'py, PyAny>, name: &str) -> PyResult<Option<T>>
where
    T: FromPyObject<'py>,
{
    let Some(value) = get_config_opt::<PyObject>(config, name)? else {
        return Ok(None);
    };
    let value = value.bind(config.py());
    if value.is_instance_of::<pyo3::types::PyBool>() {
        let name = if name == "operation_timeout_seconds" {
            "timeout"
        } else {
            name
        };
        return Err(PyValueError::new_err(format!(
            "{name} must be numeric, not bool"
        )));
    }
    value
        .extract()
        .map(Some)
        .map_err(|error| PyValueError::new_err(format!("client config field {name:?}: {error}")))
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

fn account_scope(py: Python<'_>, endpoint: &str) -> PyResult<String> {
    py.import_bound("azure.cosmos._base")?
        .getattr("create_scope_from_url")?
        .call1((endpoint,))?
        .extract()
}

/// Compute the driver identity without initializing RuntimeContext,
/// acquiring a CosmosDriver reference, or asking the credential for a token.
fn driver_identity_from_settings(
    endpoint: &str,
    master_key: Option<&str>,
    settings: &ClientSettings,
    credential: Option<&Bound<'_, PyAny>>,
) -> PyResult<String> {
    validate_auth_inputs(master_key, credential)?;
    let endpoint_url = Url::parse(endpoint)
        .map_err(|error| PyValueError::new_err(format!("invalid endpoint URL: {error}")))?;
    let credential_fp = match credential {
        Some(token_credential) => format!(
            "{}:scope:{}",
            token_credential_fingerprint(token_credential.as_ptr() as usize),
            fingerprint(&[account_scope(token_credential.py(), endpoint)?.as_bytes()])
        ),
        None => master_key_fingerprint(
            master_key.ok_or_else(|| PyValueError::new_err(AUTH_REQUIRED_ERROR))?,
        )?,
    };
    Ok(compose_cache_key(
        endpoint_url.as_str(),
        &credential_fp,
        &settings.fingerprint()?,
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
static DRIVER_CREATIONS: OnceLock<RwLock<HashMap<String, Weak<DriverCreation>>>> = OnceLock::new();

/// Return the driver cache, creating the empty table if needed.
/// Each driver identity maps to a CosmosDriver object and its acquisition count.
/// Creating this table alone does not create CosmosDriverRuntime or a driver.
pub(crate) fn drivers() -> &'static RwLock<HashMap<String, DriverEntry>> {
    DRIVERS.get_or_init(|| RwLock::new(HashMap::new()))
}

/// Held by creators and waiting acquisitions, independently of cached-driver ownership.
struct DriverCreation {
    key: String,
    lock: Mutex<()>,
}

fn driver_creations() -> &'static RwLock<HashMap<String, Weak<DriverCreation>>> {
    DRIVER_CREATIONS.get_or_init(|| RwLock::new(HashMap::new()))
}

fn driver_creation(key: &str) -> Arc<DriverCreation> {
    let mut creations = driver_creations().write();
    if let Some(creation) = creations.get(key).and_then(Weak::upgrade) {
        return creation;
    }
    let creation = Arc::new(DriverCreation {
        key: key.to_owned(),
        lock: Mutex::new(()),
    });
    creations.insert(key.to_owned(), Arc::downgrade(&creation));
    creation
}

impl Drop for DriverCreation {
    fn drop(&mut self) {
        let mut creations = driver_creations().write();
        // A new caller can replace our expired weak entry before this destructor runs.
        // Remove only our own entry, never that caller's new coordination object.
        if creations
            .get(&self.key)
            .is_some_and(|entry| std::ptr::eq(entry.as_ptr(), self))
        {
            creations.remove(&self.key);
        }
    }
}

fn acquire_cached_driver(key: &str) -> Option<DriverHandle> {
    let mut cache = drivers().write();
    let entry = cache.get_mut(key)?;
    entry.acquisition_count += 1;
    Some(DriverHandle::from_acquired_entry(key.to_owned(), entry))
}

fn acquire_driver_handle_with(
    py: Python<'_>,
    key: String,
    create: impl FnOnce() -> PyResult<DriverEntry>,
) -> PyResult<DriverHandle> {
    if let Some(handle) = acquire_cached_driver(&key) {
        return Ok(handle);
    }

    let creation = driver_creation(&key);
    // Release the GIL while waiting: the current creator may need Python callbacks.
    // The borrowed guard drops before `creation`, keeping its registry entry alive.
    let _guard = py.allow_threads(|| runtime_context().tokio_rt.block_on(creation.lock.lock()));
    if let Some(handle) = acquire_cached_driver(&key) {
        return Ok(handle);
    }

    // Failure leaves no cache entry or acquisition count. Unlocking lets a waiter retry.
    // Only this key is locked during creation; unrelated keys and releases can proceed.
    let entry = create()?;
    let handle = DriverHandle::from_acquired_entry(key.clone(), &entry);
    drivers().write().insert(key, entry);
    Ok(handle)
}

pub(crate) fn runtime_context() -> &'static RuntimeContext {
    RUNTIME_CONTEXT.get_or_init(|| RuntimeContext {
        tokio_rt: pyo3_async_runtimes::tokio::get_runtime(),
    })
}

/// Reject unsupported client configuration without initializing a runtime.
#[pyfunction(name = "_validate_runtime_configuration")]
#[pyo3(signature = (config=None))]
pub(crate) fn validate_runtime_configuration(config: Option<&Bound<'_, PyAny>>) -> PyResult<()> {
    if let Some(config) = config {
        #[cfg(not(any(test, feature = "test-probes")))]
        if get_config_opt::<Vec<PyObject>>(config, "fault_injection_rules")?
            .is_some_and(|rules| !rules.is_empty())
        {
            return Err(PyValueError::new_err(
                "fault_injection_rules requires a wheel built with --features test-probes.",
            ));
        }
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

#[pyfunction(name = "_runtime_configuration")]
pub(crate) fn runtime_configuration() -> Option<(f64, f64, f64)> {
    crate::driver_runtime::default_configuration()
}

// ---------------------------------------------------------------------------
// acquire_driver_handle
// ---------------------------------------------------------------------------
//
/// Acquire a CosmosDriver object and return a driver handle for later binding calls.
/// The Python adapter requests this during async `__aenter__()` or on the first
/// operation needing a driver handle. This function does not enforce one
/// acquisition per Python client.
///
/// A cache hit increments its count. On a miss, serialize creation for this key,
/// recheck the cache, and build outside the global cache lock only if still absent.
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
) -> PyResult<DriverHandle> {
    validate_auth_inputs(master_key, credential)?;

    let endpoint_url = Url::parse(endpoint)
        .map_err(|e| PyValueError::new_err(format!("invalid endpoint URL: {e}")))?;

    let settings = ClientSettings::from_python(config)?;
    let runtime_ctx = runtime_context();
    let selected_runtime = match runtime {
        Some(runtime) => runtime.clone(),
        None => py.allow_threads(|| runtime_ctx.tokio_rt.block_on(default_runtime()))?,
    };

    let key = format!(
        "{}:runtime-{}",
        driver_identity_from_settings(endpoint, master_key, &settings, credential)?,
        selected_runtime.id
    );

    acquire_driver_handle_with(py, key, || {
        // Python clients default to no hedging, even when no config was prepared.
        let operation_options = operation_options_from_settings(&settings)?;
        let preferred_regions = preferred_regions_from_settings(&settings)?;
        let user_agent_suffix = user_agent_suffix_from_settings(&settings)?;
        #[cfg(any(test, feature = "test-probes"))]
        let fault_rules = fault_rules_from_settings(&settings)?;

        // No matching CosmosDriver was cached. Prepare the account without holding the
        // cache lock; token authentication uses PyTokenCredential to call Python.
        let account = match credential {
            Some(token_credential) => {
                let py_credential: Py<PyAny> = token_credential.clone().unbind();
                let account_scope = account_scope(py, endpoint)?;
                AccountReference::with_credential(
                    endpoint_url,
                    Arc::new(PyTokenCredential::for_account(
                        py_credential,
                        account_scope,
                        settings.aad_scope_override.clone(),
                    )),
                )
            }
            None => {
                let account_key =
                    master_key.ok_or_else(|| PyValueError::new_err(AUTH_REQUIRED_ERROR))?;
                AccountReference::with_account_key(endpoint_url, account_key.to_string())
            }
        };

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
            #[cfg(any(test, feature = "test-probes"))]
            if !fault_rules.is_empty() {
                builder = builder
                    .with_fault_injection_rules(fault_rules.clone())
                    .map_err(|e| PyValueError::new_err(format!("invalid fault rules: {e}")))?;
            }
            builder.build()
        };

        // Build on Tokio with the GIL released. Different keys can build concurrently;
        // matching acquisitions wait for this attempt and then recheck the cache.
        let driver_runtime = Arc::clone(&selected_runtime.driver_runtime);
        let build_task = runtime_ctx
            .tokio_rt
            .spawn(async move { driver_runtime.create_driver(driver_options).await });
        let driver = py
            .allow_threads(|| runtime_ctx.tokio_rt.block_on(build_task))
            .map_err(|join_error| {
                PyRuntimeError::new_err(format!("driver init task failed: {join_error}"))
            })?
            .map_err(|error| crate::wire::driver_setup_error(py, error))?;

        Ok(DriverEntry {
            driver,
            #[cfg(any(test, feature = "test-probes"))]
            fault_rules: fault_rules
                .into_iter()
                .map(|rule| (rule.id().to_string(), rule))
                .collect(),
            acquisition_count: 1,
        })
    })
}

pub(crate) fn partition_failover_options() -> PyResult<PartitionFailoverOptions> {
    // Preserve container resolution without eagerly fetching the physical map.
    PartitionFailoverOptionsBuilder::new()
        .with_partition_topology_cache_mode(PartitionTopologyCacheMode::Lazy)
        .build()
        .map_err(|error| PyValueError::new_err(format!("invalid partition failover settings: {error}")))
}


/// Convert the ClientSettings snapshot's preferred locations into driver Region values.
/// Reject blank names; an empty input yields an empty list.
fn preferred_regions_from_settings(settings: &ClientSettings) -> PyResult<Vec<Region>> {
    validate_region_names(&settings.preferred_locations)?;
    Ok(settings
        .preferred_locations
        .iter()
        .cloned()
        .map(Region::from)
        .collect())
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
fn user_agent_suffix_from_settings(settings: &ClientSettings) -> PyResult<Option<UserAgentSuffix>> {
    let suffix = match &settings.user_agent_suffix {
        Some(suffix) => suffix,
        None => return Ok(None),
    };
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

#[cfg(any(test, feature = "test-probes"))]
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

#[cfg(any(test, feature = "test-probes"))]
fn fault_rules_from_settings(settings: &ClientSettings) -> PyResult<Vec<Arc<FaultInjectionRule>>> {
    let mut rules = Vec::new();
    for item in &settings.fault_injection_rules {
        let id = &item.id;
        let operation_name = &item.operation_type;
        let mut condition = FaultInjectionConditionBuilder::new();
        if operation_name != "All" {
            let operation_type = operation_name.parse::<FaultOperationType>().map_err(|e| {
                PyValueError::new_err(format!(
                    "fault rule {id:?} has invalid operation_type {operation_name:?}: {e}"
                ))
            })?;
            condition = condition.with_operation_type(operation_type);
        }
        if let Some(container_id) = &item.container_id {
            condition = condition.with_container_id(container_id.clone());
        }
        if let Some(region) = &item.region {
            condition = condition.with_region(Region::from(region.clone()));
        }

        let status_code = item.status_code;
        let sub_status = item.sub_status;
        let error_type = &item.error_type;
        let response_body = &item.response_body;
        let response_headers = &item.response_headers;
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
        let delay_ms = item.delay_ms;
        let probability = item.probability;
        let mut result = FaultInjectionResultBuilder::new().with_probability(probability);
        result = match (status_code, error_type.as_deref()) {
            (Some(status), None) if (100..=599).contains(&status) => {
                let mut response =
                    CustomResponseBuilder::new(azure_core::http::StatusCode::from(status));
                if sub_status != 0 {
                    response = response.with_sub_status(sub_status);
                }
                for (name, value) in response_headers {
                    response = response.with_header(name.clone(), value.clone());
                }
                result.with_custom_response(response.with_body(response_body.clone()).build())
            }
            (None, Some("ConnectionError")) if sub_status == 0 => {
                result.with_error(FaultInjectionErrorType::ConnectionError)
            }
            (None, Some("ResponseTimeout")) if sub_status == 0 => {
                result.with_error(FaultInjectionErrorType::ResponseTimeout)
            }
            (None, Some("ResponseTimeoutAfterService")) if sub_status == 0 => {
                result.with_error(FaultInjectionErrorType::ResponseTimeoutAfterService)
            }
            _ => return Err(PyValueError::new_err(
                "fault rule requires status_code 100..599 or error_type ConnectionError/ResponseTimeout/ResponseTimeoutAfterService, not both; transport errors cannot have sub_status",
            )),
        };
        if delay_ms != 0 {
            result = result.with_delay(Duration::from_millis(delay_ms));
        }

        let mut rule_builder = FaultInjectionRuleBuilder::new(id.clone(), result.build())
            .with_condition(condition.build());
        if let Some(hit_limit) = item.hit_limit {
            rule_builder = rule_builder.with_hit_limit(hit_limit);
        }
        let rule = Arc::new(rule_builder.build());
        if !item.enabled {
            rule.disable();
        }
        rules.push(rule);
    }
    Ok(rules)
}

/// Build Rust driver OperationOptions from the ClientSettings snapshot:
/// UTF-8 decoding mode, operation timeout, custom headers, excluded regions,
/// throttle-retry caps, hedging, and read consistency. Individual operations can
/// also supply options; this function does not establish their final merged values.
///
/// Missing config or threshold means Python's default: hedging disabled.
/// Other absent fields keep the driver's defaults. An enabled per-operation
/// strategy can still override this client-level strategy.
fn operation_options_from_settings(settings: &ClientSettings) -> PyResult<OperationOptions> {
    let mut builder =
        OperationOptionsBuilder::new().with_availability_strategy(AvailabilityStrategy::Disabled);
    if let Some(mode) = settings.utf8_decoding_mode.as_deref() {
        builder = builder.with_utf8_decoding_mode(utf8_decoding_mode_from_str(mode)?);
    }
    if let Some(seconds) = settings.operation_timeout_seconds {
        let timeout = Duration::try_from_secs_f64(seconds)
            .map_err(|_| PyValueError::new_err("timeout must be finite seconds within range"))?;
        if timeout < Duration::from_secs(1) {
            return Err(PyValueError::new_err("timeout must be at least one second"));
        }
        builder =
            builder.with_end_to_end_latency_policy(EndToEndOperationLatencyPolicy::new(timeout));
    }
    let headers = &settings.headers;
    if !headers.is_empty() {
        builder = builder.with_custom_headers(
            headers
                .iter()
                .map(|(name, value)| {
                    (
                        HeaderName::from(name.clone()),
                        HeaderValue::from(value.clone()),
                    )
                })
                .collect(),
        );
    }

    // Convert excluded_locations to the same ExcludedRegions type used by
    // per-operation settings.
    let region_names = &settings.excluded_locations;
    validate_region_names(region_names)?;
    if !region_names.is_empty() {
        builder = builder
            .with_excluded_regions(region_names.iter().cloned().collect::<ExcludedRegions>());
    }

    // throttling_max_retry_count / _wait_time_seconds -> ThrottlingRetryOptions.
    // Set only when at least one field was supplied; otherwise leave this option
    // to the driver defaults.
    let max_retry_count = settings.throttling_max_retry_count;
    let max_retry_wait_seconds = settings.throttling_max_retry_wait_time_seconds;
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
    if let Some(threshold_ms) = settings.hedging_threshold_ms {
        let threshold = HedgeThreshold::new(Duration::from_millis(threshold_ms))
            .ok_or_else(|| PyValueError::new_err("hedging_threshold_ms must be positive"))?;
        builder = builder.with_availability_strategy(AvailabilityStrategy::Hedging(
            HedgingStrategy::new(threshold),
        ));
    }

    // consistency_level -> ReadConsistencyStrategy. Set only when the customer app
    // supplied a non-empty value. Reject unknown names even if Python
    // preparation was bypassed.
    if let Some(level) = &settings.consistency_level {
        if !level.is_empty() {
            match read_consistency_from_str(level) {
                Some(strategy) => {
                    builder = builder.with_read_consistency_strategy(strategy);
                }
                None => {
                    return Err(PyValueError::new_err(format!(
                        "consistency_level {level:?} is not supported on the Rust \
                         backend; supported levels are Eventual, ConsistentPrefix, \
                         Session, BoundedStaleness, and Strong."
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

/// Parse `Strict` or `Lossy`, returning `PyValueError` for any other name.
pub(crate) fn utf8_decoding_mode_from_str(mode: &str) -> PyResult<Utf8DecodingMode> {
    match mode {
        "Strict" => Ok(Utf8DecodingMode::Strict),
        "Lossy" => Ok(Utf8DecodingMode::Lossy),
        _ => Err(PyValueError::new_err(
            "utf8_decoding_mode must be 'Strict' or 'Lossy'.",
        )),
    }
}

/// Map a Python consistency-level string to the driver's `ReadConsistencyStrategy`.
///
/// These are read overrides, not account-policy changes. `LatestCommitted`
/// selects the latest committed version in the read region; it does not
/// configure account staleness bounds or wait for cross-region replication.
/// Unknown names return `None` for the caller to reject.
pub(crate) fn read_consistency_from_str(level: &str) -> Option<ReadConsistencyStrategy> {
    match level {
        "Eventual" | "ConsistentPrefix" => Some(ReadConsistencyStrategy::Eventual),
        "Session" => Some(ReadConsistencyStrategy::Session),
        "BoundedStaleness" => Some(ReadConsistencyStrategy::LatestCommitted),
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

/// Release this handle's cache acquisition at most once.
/// The handle itself continues to own its driver until its last Python reference drops.
#[pyfunction]
pub(crate) fn release_driver_handle(driver_handle: &DriverHandle) -> PyResult<()> {
    driver_handle.release();
    Ok(())
}

fn release_cached_driver(key: &str, expected: Option<&Arc<CosmosDriver>>) {
    // Remove the cache entry while holding the lock, then release the lock before
    // dropping the entry. Other handles or operations may still keep the driver alive.
    let evicted: Option<DriverEntry> = {
        let mut cache = drivers().write();
        let evict = match cache.get_mut(key) {
            Some(entry) if expected.is_none_or(|driver| Arc::ptr_eq(driver, &entry.driver)) => {
                let (next, evict) = apply_close(entry.acquisition_count);
                entry.acquisition_count = next;
                evict
            }
            _ => false,
        };
        if evict {
            cache.remove(key)
        } else {
            None
        }
    };
    drop(evicted);
}

#[cfg(test)]
fn release_driver_key(key: &str) -> PyResult<()> {
    release_cached_driver(key, None);
    Ok(())
}

#[cfg(any(test, feature = "test-probes"))]
#[pyfunction]
pub(crate) fn _debug_fault_injection_rule_hit_count(driver_handle: &DriverHandle, rule_id: &str) -> PyResult<u32> {
    let rule = driver_handle.fault_rule(rule_id)?;
    Ok(rule.hit_count())
}

/// Toggle only an explicitly configured rule; callers must use isolated rule IDs.
// PyO3 generates the identity PyErr conversion in the Python-call wrapper.
#[allow(clippy::useless_conversion)]
#[cfg(any(test, feature = "test-probes"))]
#[pyfunction]
pub(crate) fn _debug_set_fault_injection_rule_enabled(
    driver_handle: &DriverHandle,
    rule_id: &str,
    enabled: bool,
) -> PyResult<()> {
    let rule = driver_handle.fault_rule(rule_id)?;
    if enabled {
        rule.enable();
    } else {
        rule.disable();
    }
    Ok(())
}

/// Inspect already-cached regions without causing a metadata request.
#[cfg(feature = "test-probes")]
#[pyfunction]
pub(crate) fn _debug_cached_account_regions(
    py: Python<'_>,
    driver_handle: &DriverHandle,
) -> PyResult<Option<(Vec<String>, Vec<String>)>> {
    let driver = driver_handle.driver();
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
fn config_fingerprint(config: Option<&Bound<'_, PyAny>>) -> PyResult<String> {
    ClientSettings::from_python(config)?.fingerprint()
}

#[cfg(test)]
fn operation_options_from_config(config: Option<&Bound<'_, PyAny>>) -> PyResult<OperationOptions> {
    operation_options_from_settings(&ClientSettings::from_python(config)?)
}

#[cfg(test)]
fn preferred_regions_from_config(config: &Bound<'_, PyAny>) -> PyResult<Vec<Region>> {
    preferred_regions_from_settings(&ClientSettings::from_python(Some(config))?)
}

#[cfg(test)]
fn fault_rules_from_config(config: &Bound<'_, PyAny>) -> PyResult<Vec<Arc<FaultInjectionRule>>> {
    fault_rules_from_settings(&ClientSettings::from_python(Some(config))?)
}

#[cfg(test)]
fn driver_identity(
    endpoint: &str,
    master_key: Option<&str>,
    config: Option<&Bound<'_, PyAny>>,
    credential: Option<&Bound<'_, PyAny>>,
) -> PyResult<String> {
    driver_identity_from_settings(
        endpoint,
        master_key,
        &ClientSettings::from_python(config)?,
        credential,
    )
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
    fn driver_acquisition_reads_settings_once_on_cache_miss_and_hit() {
        use crate::driver_runtime::RuntimeHandle;
        use azure_data_cosmos_driver::in_memory_emulator::{
            InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion,
        };
        use std::sync::Arc;
        use url::Url;

        crate::test_support::prepare_python();
        let endpoint = Url::parse("https://settings-snapshot.emulator.local").unwrap();
        let account =
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", endpoint.clone())])
                .unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(account));
        let runtime = super::runtime_context()
            .tokio_rt
            .block_on(emulator.runtime_builder().build())
            .unwrap();
        Python::with_gil(|py| {
            let runtime = Py::new(py, RuntimeHandle::new(runtime)).unwrap();
            let module = PyModule::from_code_bound(
                py,
                r#"
from types import SimpleNamespace
class ReadOnce(SimpleNamespace):
    def __getattribute__(self, name):
        if not name.startswith("_"):
            reads = super().__getattribute__("_reads")
            assert name not in reads, f"{name} read twice"
            reads.add(name)
        return super().__getattribute__(name)
rule = ReadOnce(
    _reads=set(), id="snapshot", operation_type="ReadItem", status_code=429,
    sub_status=0, container_id=None, region=None, delay_ms=0, probability=1.0,
    hit_limit=None, enabled=False, response_headers={"x-test": "snapshot"},
    response_body=b"snapshot")
config = ReadOnce(
    _reads=set(), preferred_locations=("East US",), excluded_locations=(),
    throttling_max_retry_count=3, throttling_max_retry_wait_time_seconds=2.5,
    hedging_threshold_ms=500, user_agent_suffix="snapshot", consistency_level="Session",
    aad_scope_override="https://snapshot.invalid/.default", operation_timeout_seconds=30,
    headers={"x-test": "snapshot"}, fault_injection_rules=(rule,))
"#,
                "settings_snapshot.py",
                "settings_snapshot",
            )
            .unwrap();
            let config = module.getattr("config").unwrap();
            let rule = module.getattr("rule").unwrap();
            let acquire = || {
                super::acquire_driver_handle(
                    py,
                    endpoint.as_str(),
                    Some("ZW11bGF0b3Ita2V5"),
                    Some(&config),
                    None,
                    Some(runtime.borrow(py)),
                )
                .unwrap()
            };
            let first = acquire();
            config
                .getattr("_reads")
                .unwrap()
                .call_method0("clear")
                .unwrap();
            rule.getattr("_reads")
                .unwrap()
                .call_method0("clear")
                .unwrap();
            let second = acquire();
            assert!(Arc::ptr_eq(&first.driver, &second.driver));
            super::release_driver_handle(&first).unwrap();
            super::release_driver_handle(&second).unwrap();
        });
    }

    #[test]
    fn settings_snapshot_keeps_identity_and_driver_options_together_after_python_mutation() {
        crate::test_support::prepare_python();
        Python::with_gil(|py| {
            let module = PyModule::from_code_bound(
                py,
                r#"
from types import SimpleNamespace
rule = SimpleNamespace(
    id="snapshot", operation_type="ReadItem", status_code=429, sub_status=0,
    container_id=None, region=None, delay_ms=0, probability=1.0,
    hit_limit=None, enabled=False, response_headers={"x-test": "original"})
config = SimpleNamespace(
    preferred_locations=["East US"], headers={"x-test": "original"},
    throttling_max_retry_count=3, aad_scope_override="https://original.invalid/.default",
    fault_injection_rules=[rule])
def mutate():
    config.preferred_locations[:] = ["West US"]
    config.headers["x-test"] = "changed"
    config.throttling_max_retry_count = 9
    config.aad_scope_override = "https://changed.invalid/.default"
    rule.response_headers["x-test"] = "changed"
    rule.enabled = True
    config.fault_injection_rules.clear()
"#,
                "settings_mutation.py",
                "settings_mutation",
            )
            .unwrap();
            let config = module.getattr("config").unwrap();
            let settings = super::ClientSettings::from_python(Some(&config)).unwrap();
            let fingerprint = settings.fingerprint().unwrap();
            module.getattr("mutate").unwrap().call0().unwrap();
            assert_eq!(fingerprint, settings.fingerprint().unwrap());
            assert_ne!(
                fingerprint,
                super::config_fingerprint(Some(&config)).unwrap()
            );
            assert_eq!(
                super::preferred_regions_from_settings(&settings).unwrap(),
                vec![super::Region::from("East US")],
            );
            assert_eq!(
                settings.aad_scope_override.as_deref(),
                Some("https://original.invalid/.default")
            );
            let options = super::operation_options_from_settings(&settings).unwrap();
            let header = azure_core::http::headers::HeaderName::from_static("x-test");
            assert_eq!(
                options.custom_headers.unwrap()[&header].as_str(),
                "original"
            );
            assert_eq!(
                options.throttling_retry_options.unwrap().max_retry_count,
                Some(3)
            );
            let rules = super::fault_rules_from_settings(&settings).unwrap();
            assert!(!rules[0].is_enabled());
            assert_eq!(
                rules[0]
                    .result()
                    .custom_response()
                    .unwrap()
                    .headers()
                    .get_optional_str(&header),
                Some("original"),
            );
        });
    }

    #[test]
    fn fault_wait_budget_config_preserves_fractional_seconds() {
        crate::test_support::prepare_python();
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
    fn fault_all_operations_is_explicit_and_preserves_other_filters() {
        crate::test_support::prepare_python();
        Python::with_gil(|py| {
            let module = PyModule::from_code_bound(
                py,
                r#"
from types import SimpleNamespace
rule = SimpleNamespace(
    id="all-operations", operation_type="All", status_code=429, sub_status=0,
    container_id="orders", region=None, delay_ms=5000, probability=1.0,
    hit_limit=None, enabled=False)
config = SimpleNamespace(fault_injection_rules=(rule,))
"#,
                "fault_all.py",
                "fault_all",
            )
            .unwrap();
            let config = module.getattr("config").unwrap();
            let rule = module.getattr("rule").unwrap();
            let fingerprint = super::config_fingerprint(Some(&config)).unwrap();
            let rules = super::fault_rules_from_config(&config).unwrap();
            assert!(rules[0].condition().operation_type().is_none());
            assert_eq!(rules[0].condition().container_id(), Some("orders"));
            assert!(!rules[0].is_enabled());
            assert_eq!(rules[0].result().delay(), Some(Duration::from_secs(5)));
            rule.setattr("operation_type", "ReadItem").unwrap();
            let rules = super::fault_rules_from_config(&config).unwrap();
            assert!(rules[0].condition().operation_type().is_some());
            assert_ne!(
                fingerprint,
                super::config_fingerprint(Some(&config)).unwrap()
            );
            for invalid in ["", "all", "ReadDatabases"] {
                rule.setattr("operation_type", invalid).unwrap();
                assert!(super::fault_rules_from_config(&config).is_err());
            }
            rule.setattr("operation_type", py.None()).unwrap();
            assert!(super::fault_rules_from_config(&config).is_err());
        });
    }

    #[test]
    fn fault_response_headers_are_forwarded_and_isolate_cached_drivers() {
        use super::{config_fingerprint, fault_rules_from_config};
        use azure_core::http::headers::HeaderName;

        crate::test_support::prepare_python();
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
            for error_type in [
                "ConnectionError",
                "ResponseTimeout",
                "ResponseTimeoutAfterService",
            ] {
                rule.setattr("error_type", error_type).unwrap();
                assert!(fault_rules_from_config(&config).unwrap_err().to_string().contains("response_headers"));
            }
        });
    }

    #[test]
    fn fault_response_body_is_preserved_and_changes_driver_identity() {
        crate::test_support::prepare_python();
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
        crate::test_support::prepare_python();
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
        crate::test_support::prepare_python();
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
        crate::test_support::prepare_python();
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
        crate::test_support::prepare_python();
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
        crate::test_support::prepare_python();
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

    // Only test the count and removal decision; no cache entry or driver is dropped.
    #[test]
    fn apply_close_decrements_acquisition_count_and_reports_zero() {
        // One release from a count of two leaves one acquisition.
        assert_eq!(apply_close(2), (1, false));
        // Releasing the last acquisition requests removal.
        assert_eq!(apply_close(1), (0, true));
    }

    #[test]
    fn apply_close_keeps_zero_and_requests_removal() {
        // DriverHandle prevents repeated releases; this test only checks a zero count.
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

        crate::test_support::prepare_python();
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
        let key = "fault-rule-toggle-scoping-test";
        let entry = super::DriverEntry {
            driver,
            fault_rules: rules
                .iter()
                .map(|rule| (rule.id().to_owned(), Arc::clone(rule)))
                .collect::<HashMap<_, _>>(),
            acquisition_count: 1,
        };
        let handle = super::DriverHandle::from_acquired_entry(key.to_owned(), &entry);
        super::drivers().write().insert(key.into(), entry);
        for enabled in [true, true, false, false] {
            super::_debug_set_fault_injection_rule_enabled(&handle, "selected", enabled).unwrap();
            assert_eq!(rules[0].is_enabled(), enabled);
            assert!(!rules[1].is_enabled());
            assert_eq!(rules[0].hit_count(), 0);
        }
        assert!(super::_debug_set_fault_injection_rule_enabled(&handle, "missing", true).is_err());
        super::release_driver_handle(&handle).unwrap();
        assert!(super::_debug_set_fault_injection_rule_enabled(&handle, "selected", true).is_err());
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
        let key = "close-reference-lifetime-test";
        super::drivers().write().insert(
            key.to_string(),
            super::DriverEntry {
                driver,
                fault_rules: HashMap::new(),
                acquisition_count: 2,
            },
        );

        super::release_driver_key(key).unwrap();
        let operation_driver = {
            let cache = super::drivers().read();
            let entry = cache.get(key).unwrap();
            assert_eq!(entry.acquisition_count, 1);
            Arc::clone(&entry.driver)
        };
        super::release_driver_key(key).unwrap();
        assert!(!super::drivers().read().contains_key(key));
        assert!(weak_driver.upgrade().is_some());

        super::release_driver_key(key).unwrap();
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
        assert_eq!(
            read_consistency_from_str("ConsistentPrefix"),
            Some(ReadConsistencyStrategy::Eventual)
        );
        assert_eq!(
            read_consistency_from_str("BoundedStaleness"),
            Some(ReadConsistencyStrategy::LatestCommitted)
        );
        // Strong maps to the driver's GlobalStrong -- there is no plain Strong.
        assert_eq!(
            read_consistency_from_str("Strong"),
            Some(ReadConsistencyStrategy::GlobalStrong)
        );
    }

    #[test]
    fn read_consistency_rejects_unknown_names() {
        // An outright-unknown string is rejected, not dropped.
        assert_eq!(read_consistency_from_str("Nonsense"), None);
        // The mapping is exact: the driver's own wire spelling is not a Python
        // consistency-level name, so it does not sneak through here.
        assert_eq!(read_consistency_from_str("GlobalStrong"), None);
        assert_eq!(read_consistency_from_str("LatestCommitted"), None);
        assert_eq!(read_consistency_from_str("Default"), None);
        assert_eq!(read_consistency_from_str("eventual"), None);
        assert_eq!(read_consistency_from_str(""), None);
    }

    #[test]
    fn client_consistency_config_maps_levels_and_preserves_defaults() {
        crate::test_support::prepare_python();
        Python::with_gil(|py| {
            let config = py
                .import_bound("types")
                .unwrap()
                .getattr("SimpleNamespace")
                .unwrap()
                .call0()
                .unwrap();
            assert_eq!(
                operation_options_from_config(None)
                    .unwrap()
                    .read_consistency_strategy,
                None
            );
            assert_eq!(
                operation_options_from_config(Some(&config))
                    .unwrap()
                    .read_consistency_strategy,
                None
            );
            for (level, expected) in [
                (Some("Eventual"), Some(ReadConsistencyStrategy::Eventual)),
                (
                    Some("ConsistentPrefix"),
                    Some(ReadConsistencyStrategy::Eventual),
                ),
                (Some("Session"), Some(ReadConsistencyStrategy::Session)),
                (
                    Some("BoundedStaleness"),
                    Some(ReadConsistencyStrategy::LatestCommitted),
                ),
                (Some("Strong"), Some(ReadConsistencyStrategy::GlobalStrong)),
                (Some(""), None),
                (None, None),
            ] {
                config.setattr("consistency_level", level).unwrap();
                assert_eq!(
                    operation_options_from_config(Some(&config))
                        .unwrap()
                        .read_consistency_strategy,
                    expected,
                    "{level:?}"
                );
            }
            for level in [
                "Unknown",
                "LatestCommitted",
                "GlobalStrong",
                "Default",
                "eventual",
            ] {
                config.setattr("consistency_level", level).unwrap();
                let error = operation_options_from_config(Some(&config)).unwrap_err();
                assert!(error.is_instance_of::<PyValueError>(py));
            }
        });
    }

    #[test]
    fn retired_client_network_settings_are_rejected_without_initialization() {
        crate::test_support::prepare_python();
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
        crate::test_support::prepare_python();
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
            rule.setattr("error_type", "ResponseTimeoutAfterService").unwrap();
            let rules = fault_rules_from_config(&config).unwrap();
            assert_eq!(
                rules[0].result().error_type(),
                Some(FaultInjectionErrorType::ResponseTimeoutAfterService)
            );
            assert!(rules[0].result().custom_response().is_none());
            assert_eq!(rules[0].result().delay(), Some(Duration::from_secs(2)));
            assert_ne!(response_fingerprint, config_fingerprint(Some(&config)).unwrap());
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
        crate::test_support::prepare_python();
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
            assert_eq!(
                token_identity,
                super::driver_identity(url, None, None, Some(&credential)).unwrap()
            );
            let unicode_endpoint = "https://b\u{fc}cher.invalid";
            let ascii_endpoint = "https://xn--bcher-kva.invalid";
            assert_eq!(
                url::Url::parse(unicode_endpoint).unwrap(),
                url::Url::parse(ascii_endpoint).unwrap()
            );
            assert_ne!(
                super::driver_identity(unicode_endpoint, None, None, Some(&credential)).unwrap(),
                super::driver_identity(ascii_endpoint, None, None, Some(&credential)).unwrap()
            );
            let scope_config = module.getattr("Config").unwrap().call0().unwrap();
            scope_config.setattr("aad_scope_override", "").unwrap();
            assert_eq!(
                token_identity,
                super::driver_identity(url, None, Some(&scope_config), Some(&credential)).unwrap()
            );
            scope_config
                .setattr("aad_scope_override", "https://identity.invalid/.default")
                .unwrap();
            let overridden =
                super::driver_identity(url, None, Some(&scope_config), Some(&credential)).unwrap();
            // Even the same initial scope has a different no-fallback policy.
            assert_ne!(token_identity, overridden);
            assert_eq!(
                overridden,
                super::driver_identity(url, None, Some(&scope_config), Some(&credential)).unwrap()
            );
            scope_config
                .setattr("aad_scope_override", "https://other.invalid/.default")
                .unwrap();
            assert_ne!(
                overridden,
                super::driver_identity(url, None, Some(&scope_config), Some(&credential)).unwrap()
            );
        });
    }

    #[test]
    fn validate_auth_inputs_rejects_missing_and_ambiguous_inputs() {
        let missing = validate_auth_inputs(None, None).expect_err("missing auth should fail");
        assert!(
            missing.to_string().contains(AUTH_REQUIRED_ERROR),
            "unexpected error: {missing}"
        );

        crate::test_support::prepare_python();
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
        crate::test_support::prepare_python();
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
        // a credential-derived fingerprint is safe to log.
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
        crate::test_support::prepare_python();
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
        crate::test_support::prepare_python();
        Python::with_gil(|_py| {
            let context = super::runtime_context();
            assert!(std::ptr::eq(
                context.tokio_rt,
                pyo3_async_runtimes::tokio::get_runtime()
            ));
        });
    }

    mod driver_creation_tests {
        use super::super::{
            acquire_driver_handle_with, driver_creation, driver_creations, drivers,
            runtime_context, DriverCreation, DriverEntry, DriverHandle,
        };
        use azure_data_cosmos_driver::{
            in_memory_emulator::{InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion},
            models::AccountReference,
            options::DriverOptions,
        };
        use pyo3::{exceptions::PyRuntimeError, prelude::*};
        use std::{
            collections::HashMap,
            sync::{
                atomic::{AtomicUsize, Ordering},
                mpsc::{self, Receiver},
                Arc,
            },
            thread::{self, JoinHandle},
            time::{Duration, Instant},
        };
        use tokio::sync::Mutex;
        use url::Url;

        const WAIT: Duration = Duration::from_secs(10);

        fn entry() -> DriverEntry {
            crate::test_support::prepare_python();
            let endpoint = Url::parse("https://driver-creation.emulator.local").unwrap();
            let config =
                VirtualAccountConfig::new(vec![VirtualRegion::new("East US", endpoint.clone())])
                    .unwrap();
            let emulator = Arc::new(InMemoryEmulatorHttpClient::new(config));
            let driver = runtime_context().tokio_rt.block_on(async {
                let runtime = emulator.runtime_builder().build().await.unwrap();
                runtime
                    .create_driver(
                        DriverOptions::builder(AccountReference::with_account_key(
                            endpoint,
                            "ZW11bGF0b3Ita2V5",
                        ))
                        .build(),
                    )
                    .await
                    .unwrap()
            });
            DriverEntry {
                driver,
                fault_rules: HashMap::new(),
                acquisition_count: 1,
            }
        }

        fn spawn_acquisition(
            task: impl FnOnce(Python<'_>) -> PyResult<DriverHandle> + Send + 'static,
        ) -> (JoinHandle<PyResult<DriverHandle>>, Receiver<()>) {
            let (done, finished) = mpsc::channel();
            let worker = thread::spawn(move || {
                let result = Python::with_gil(task);
                done.send(()).unwrap();
                result
            });
            (worker, finished)
        }

        fn finish(
            worker: (JoinHandle<PyResult<DriverHandle>>, Receiver<()>),
        ) -> PyResult<DriverHandle> {
            worker
                .1
                .recv_timeout(WAIT)
                .expect("acquisition did not finish");
            worker.0.join().unwrap()
        }

        fn wait_for_second_miss(key: &str) {
            let deadline = Instant::now() + WAIT;
            loop {
                // Only acquisitions that missed the cache retain this object.
                // Observing two owners proves B missed while A's factory is held.
                if driver_creations()
                    .read()
                    .get(key)
                    .is_some_and(|creation| creation.strong_count() == 2)
                {
                    return;
                }
                assert!(
                    Instant::now() < deadline,
                    "second acquisition did not register"
                );
                thread::yield_now();
            }
        }

        #[derive(Clone, Copy)]
        enum FirstAcquisition {
            Retain,
            Fail,
            Release,
        }

        fn concurrent_acquisitions(first_action: FirstAcquisition) {
            let key = match first_action {
                FirstAcquisition::Retain => "concurrent-driver-reuse",
                FirstAcquisition::Fail => "concurrent-driver-retry",
                FirstAcquisition::Release => "concurrent-driver-late-close",
            };
            // Supply a real driver to the cache, but control and count factory calls
            // rather than depending on the driver's internal initialization requests.
            let first_entry = entry();
            let weak_driver = Arc::downgrade(&first_entry.driver);
            let second_entry = DriverEntry {
                driver: Arc::clone(&first_entry.driver),
                fault_rules: HashMap::new(),
                acquisition_count: 1,
            };
            let calls = Arc::new(AtomicUsize::new(0));
            let first_calls = Arc::clone(&calls);
            let (started, first_started) = mpsc::channel();
            let (resume, first_resume) = mpsc::channel();
            let first = spawn_acquisition(move |py| {
                let result = acquire_driver_handle_with(py, key.to_owned(), || {
                    first_calls.fetch_add(1, Ordering::SeqCst);
                    started.send(()).unwrap();
                    py.allow_threads(move || first_resume.recv_timeout(WAIT))
                        .unwrap();
                    if matches!(first_action, FirstAcquisition::Fail) {
                        return Err(PyRuntimeError::new_err("injected driver init failure"));
                    }
                    Ok(first_entry)
                });
                if matches!(first_action, FirstAcquisition::Release) {
                    // Keep the GIL until release, so B cannot claim the cached entry.
                    // This models an async worker releasing a late handle after close.
                    result.as_ref().unwrap().release();
                }
                result
            });
            first_started.recv_timeout(WAIT).unwrap();
            let second_calls = Arc::clone(&calls);
            let second = spawn_acquisition(move |py| {
                acquire_driver_handle_with(py, key.to_owned(), || {
                    second_calls.fetch_add(1, Ordering::SeqCst);
                    Ok(second_entry)
                })
            });
            wait_for_second_miss(key);
            assert_eq!(calls.load(Ordering::SeqCst), 1);

            if matches!(first_action, FirstAcquisition::Retain) {
                let other_entry = entry();
                let other = spawn_acquisition(move |py| {
                    acquire_driver_handle_with(py, "independent-driver-key".to_owned(), || {
                        Ok(other_entry)
                    })
                });
                let other_handle = finish(other).unwrap();
                other_handle.release();
                assert!(!driver_creations()
                    .read()
                    .contains_key(other_handle.cache_key()));
            }

            resume.send(()).unwrap();
            let first_result = finish(first);
            let second_handle = finish(second).unwrap();
            assert_eq!(second_handle.cache_key(), key);
            let first_handle = if matches!(first_action, FirstAcquisition::Fail) {
                assert_eq!(
                    first_result
                        .err()
                        .expect("first acquisition must fail")
                        .to_string(),
                    "RuntimeError: injected driver init failure"
                );
                None
            } else {
                let handle = first_result.unwrap();
                assert_eq!(handle.cache_key(), key);
                Some(handle)
            };
            let retained_first = matches!(first_action, FirstAcquisition::Retain);
            assert_eq!(
                calls.load(Ordering::SeqCst),
                if retained_first { 1 } else { 2 }
            );
            assert_eq!(
                drivers().read().get(key).unwrap().acquisition_count,
                if retained_first { 2 } else { 1 }
            );
            assert!(!driver_creations().read().contains_key(key));

            Python::with_gil(|py| {
                let reused_handle = acquire_driver_handle_with(py, key.to_owned(), || {
                    panic!("a cache hit must not invoke the factory")
                })
                .unwrap();
                assert_eq!(reused_handle.cache_key(), key);
                assert!(Arc::ptr_eq(&reused_handle.driver, &second_handle.driver));
                reused_handle.release();
            });
            if let Some(handle) = first_handle {
                if retained_first {
                    assert!(Arc::ptr_eq(&handle.driver, &second_handle.driver));
                }
                handle.release();
            }
            let operation_driver = second_handle.driver();
            assert_eq!(drivers().read().get(key).unwrap().acquisition_count, 1);
            second_handle.release();
            assert!(!drivers().read().contains_key(key));
            drop(second_handle);
            assert!(weak_driver.upgrade().is_some());
            drop(operation_driver);
            assert!(weak_driver.upgrade().is_none());
        }

        #[test]
        fn same_key_builds_once_while_different_keys_progress() {
            concurrent_acquisitions(FirstAcquisition::Retain);
        }

        #[test]
        fn failed_creator_leaves_waiter_free_to_retry() {
            concurrent_acquisitions(FirstAcquisition::Fail);
        }

        #[test]
        fn release_before_waiter_claims_handle_allows_recreation() {
            concurrent_acquisitions(FirstAcquisition::Release);
        }

        #[test]
        fn failure_and_unwind_remove_pending_state_and_allow_later_retry() {
            let next_entry = entry();
            let key = "driver-creation-failure-cleanup";
            Python::with_gil(|py| {
                let error = acquire_driver_handle_with(py, key.to_owned(), || {
                    Err(PyRuntimeError::new_err("injected failure"))
                })
                .err()
                .expect("acquisition must fail");
                assert!(error.is_instance_of::<PyRuntimeError>(py));
            });
            assert!(!drivers().read().contains_key(key));
            assert!(!driver_creations().read().contains_key(key));
            let panicked = std::panic::catch_unwind(|| {
                Python::with_gil(|py| {
                    acquire_driver_handle_with(py, key.to_owned(), || panic!("injected panic"))
                })
            });
            assert!(panicked.is_err());
            assert!(!drivers().read().contains_key(key));
            assert!(!driver_creations().read().contains_key(key));
            Python::with_gil(|py| {
                let acquired_handle =
                    acquire_driver_handle_with(py, key.to_owned(), || Ok(next_entry)).unwrap();
                assert_eq!(drivers().read().get(key).unwrap().acquisition_count, 1);
                acquired_handle.release();
            });
            assert!(!drivers().read().contains_key(key));
            assert!(!driver_creations().read().contains_key(key));
        }

        #[test]
        fn last_owner_removes_only_its_own_coordination_entry() {
            let key = "driver-creation-registry-cleanup";
            let first = driver_creation(key);
            let second = driver_creation(key);
            assert!(Arc::ptr_eq(&first, &second));
            drop(second);
            assert!(driver_creations().read().contains_key(key));
            let replacement = Arc::new(DriverCreation {
                key: key.to_owned(),
                lock: Mutex::new(()),
            });
            // Reproduce replacement of an expired weak entry before its destructor
            // obtains the registry lock, without relying on thread scheduling.
            driver_creations()
                .write()
                .insert(key.to_owned(), Arc::downgrade(&replacement));
            drop(first);
            assert!(Arc::ptr_eq(&driver_creation(key), &replacement));
            drop(replacement);
            assert!(!driver_creations().read().contains_key(key));
        }
    }

    #[test]
    fn selected_runtime_scopes_driver_reuse_and_survives_python_owner_release() {
        use std::sync::Arc;
        use url::Url;
        use azure_data_cosmos_driver::in_memory_emulator::{
            InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion,
        };
        use crate::driver_runtime::RuntimeHandle;

        crate::test_support::prepare_python();
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
            assert!(Arc::ptr_eq(&a.driver, &b.driver));
            assert!(!Arc::ptr_eq(&a.driver, &c.driver));
            assert_eq!(
                super::drivers()
                    .read()
                    .get(&a.key)
                    .unwrap()
                    .acquisition_count,
                2
            );
            drop(first);
            assert!(weak_first.upgrade().is_some());
            let operation_driver = a.driver();
            super::release_driver_handle(&a).unwrap();
            assert!(super::drivers().read().contains_key(&b.key));
            super::release_driver_handle(&b).unwrap();
            drop(a);
            drop(b);
            assert!(weak_first.upgrade().is_some());
            drop(operation_driver);
            assert!(weak_first.upgrade().is_none());
            super::release_driver_handle(&c).unwrap();
        });
    }

    fn assert_token_credential_driver_sharing(shared_credential: bool) {
        use crate::driver_runtime::RuntimeHandle;
        use azure_data_cosmos_driver::in_memory_emulator::{
            InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion,
        };
        use std::sync::Arc;
        use url::Url;

        crate::test_support::prepare_python();
        let endpoint = Url::parse(if shared_credential {
            "https://shared-token-credential.emulator.local"
        } else {
            "https://distinct-token-credentials.emulator.local"
        })
        .unwrap();
        let config =
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", endpoint.clone())])
                .unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(config));
        let runtime = super::runtime_context()
            .tokio_rt
            .block_on(emulator.runtime_builder().build())
            .unwrap();

        Python::with_gil(|py| {
            let runtime = Py::new(py, RuntimeHandle::new(runtime)).unwrap();
            let module = PyModule::from_code_bound(
                py,
                r#"
import time
from types import SimpleNamespace
class Credential:
    def get_token(self, *scopes):
        return SimpleNamespace(token="in-memory-test-token", expires_on=int(time.time()) + 3600)
first = Credential()
second = Credential()
"#,
                "driver_sharing_test.py",
                "driver_sharing_test",
            )
            .unwrap();
            let first = module.getattr("first").unwrap();
            let second = if shared_credential {
                first.clone()
            } else {
                module.getattr("second").unwrap()
            };
            let acquire = |credential: &Bound<'_, PyAny>| {
                super::acquire_driver_handle(
                    py,
                    endpoint.as_str(),
                    None,
                    None,
                    Some(credential),
                    Some(runtime.borrow(py)),
                )
                .unwrap()
            };
            // Separate acquisitions are not comparable Python identities. Inspect the
            // actual drivers while both acquisitions and credentials remain alive.
            let a = acquire(&first);
            let b = acquire(&second);
            assert_eq!(Arc::ptr_eq(&a.driver, &b.driver), shared_credential);
            assert_eq!(
                super::drivers()
                    .read()
                    .get(&a.key)
                    .unwrap()
                    .acquisition_count,
                if shared_credential { 2 } else { 1 },
            );

            super::release_driver_handle(&a).unwrap();
            super::release_driver_handle(&a).unwrap();
            {
                let cache = super::drivers().read();
                let entry = cache
                    .get(&b.key)
                    .expect("the second acquisition must remain live");
                assert!(Arc::ptr_eq(&entry.driver, &b.driver));
                assert_eq!(entry.acquisition_count, 1);
                if !shared_credential {
                    assert!(!cache.contains_key(&a.key));
                }
            }
            super::release_driver_handle(&b).unwrap();
            assert!(!super::drivers().read().contains_key(&b.key));
        });
    }

    #[test]
    fn same_token_credential_reuses_native_driver() {
        assert_token_credential_driver_sharing(true);
    }

    #[test]
    fn distinct_token_credentials_isolate_native_drivers() {
        assert_token_credential_driver_sharing(false);
    }

    #[test]
    fn client_overall_deadline_is_distinct_from_connection_settings() {
        crate::test_support::prepare_python();
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

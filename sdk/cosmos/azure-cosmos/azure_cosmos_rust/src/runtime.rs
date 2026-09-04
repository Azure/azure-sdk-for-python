// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Per-process runtime, the driver cache, and the client lifecycle entry points
//! (`init_client` / `close_client`).
//!
//! This file is the rust backend's pooling-and-lifecycle brain. It exists so the
//! whole process shares one set of runtimes, so clients with the same
//! `(endpoint, credential, config)` share one reference-counted rust driver
//! (built and torn down exactly once, at the right times), and so a customer's
//! construction settings and credential are turned into driver options safely at
//! the boundary. Without it, every `CosmosClient` on the rust backend would build
//! its own rust driver -- its own connection pool and routing state -- so N
//! clients to the same account would mean N connection pools; and there would be
//! no safe place to decide when to tear a driver down (closing one client could
//! remove the driver while another client is still using it).
//!
//! Three "runtime"-ish things live here; keep them distinct:
//!   * shared Tokio runtime (`RuntimeContext.tokio_rt`) -- the one process-wide
//!     thread pool that *runs* async work. General-purpose Tokio; knows nothing
//!     about Cosmos.
//!   * driver runtime (`CosmosDriverRuntime`) -- the *factory* that builds rust
//!     drivers and carries the process-wide connection-pool config. Also one per
//!     process. It is built *on* the Tokio runtime.
//!   * rust driver (`CosmosDriver`) -- the per-account *engine* that signs,
//!     routes, and retries. This is the one thing here that is NOT process-wide:
//!     there is one per distinct `(endpoint, credential, config)`, produced by
//!     `driver_runtime.create_driver(...)`, and its async work runs on the shared
//!     Tokio runtime.
//!
//! So the relationship is: one shared Tokio runtime and one driver runtime per
//! process (bundled together in `RuntimeContext`, behind one `OnceLock`); the
//! driver runtime is a factory that makes many rust drivers (one per key), which
//! this file caches and reference-counts.
//!
//! The driver handle `init_client` returns is exactly that
//! `(endpoint, credential, config)` cache key. Clients that match on all three
//! share one rust driver, and it is dropped when the last one closes. A client
//! that differs in credential or config gets its own driver, so one client's auth
//! or settings are never used for another.
//!
//! Terminology (consistent with `factory.py`, `rust.py`, `credential.rs`,
//! `documents/`): client = the `CosmosClient`; binding = this compiled `_rust`
//! extension; rust driver / driver runtime / shared Tokio runtime as above;
//! driver handle = the cache key string; credential = how the customer proves who
//! they are.

use std::collections::hash_map::RandomState;
use std::collections::HashMap;
use std::hash::{BuildHasher, Hash, Hasher};
use std::sync::{Arc, OnceLock};
use std::time::Duration;

use parking_lot::RwLock;
use pyo3::exceptions::{PyAttributeError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyStringMethods;

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
    pub(crate) tokio_rt: TokioRuntime,
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

/// One cached driver plus a count of how many live clients use it.
///
/// The handle `init_client` returns is the `(endpoint, credential, config)` key, so
/// clients that match on all three share one `CosmosDriver` and clients that differ
/// get their own. This map is the only per-account cache, since the driver runtime
/// builds a fresh driver on every `create_driver`.
///
/// All three parts are required -- this is the minimum safe key, not a tuning choice:
///
/// * **credential** -- a driver bakes in the auth it signs requests with, so sharing
///   across credentials would sign one client's requests with another's credential.
/// * **config** -- a driver bakes in its settings (preferred/excluded regions,
///   consistency, throttling, hedging, user-agent suffix) at build time, so a client
///   with different settings would silently inherit another's instead of its own.
/// * **endpoint** -- different accounts always need different drivers.
///
/// A coarser key (endpoint-only, or endpoint+credential) is therefore unsafe: it
/// would misuse a credential or drop config settings. The cost is more drivers -- more
/// connection pools and memory -- when a process deliberately varies credential or
/// config; a normal app (one credential, one config per account) still gets one driver
/// per account. Sharing only happens when all three match.
///
/// The count keeps the shared driver alive until the last user closes: `init_client`
/// adds one, `close_client` drops one, and the driver is evicted at zero. Without it,
/// closing one of two sharers would evict the driver the other still needs.
pub(crate) struct DriverEntry {
    pub(crate) driver: Arc<CosmosDriver>,
    fault_rules: HashMap<String, Arc<FaultInjectionRule>>,
    refcount: usize,
}

/// Compute a `DriverEntry`'s next refcount and whether to evict it. Split out of
/// `close_client` so the drop-one / evict-at-zero rule can be tested without a real
/// `CosmosDriver`. `saturating_sub` keeps a stray extra close from underflowing.
fn apply_close(refcount: usize) -> (usize, bool) {
    let next = refcount.saturating_sub(1);
    (next, next == 0)
}

// ---------------------------------------------------------------------------
// Cache key: (endpoint, credential, config)
// ---------------------------------------------------------------------------
//
// The key carries all three, so two clients share a driver only when they match on
// every one:
//
// * Credential -- a shared driver shares its signed-request auth, so an
//   endpoint-only key could sign one client's requests with another's credential.
// * Config -- a driver bakes in its settings (preferred/excluded regions,
//   consistency, throttling, hedging, user-agent suffix) when built, so a client
//   with different settings needs its own driver to honor them.
//
// This builds more drivers but never uses one client's auth or settings for another.
//
// No secret goes into the key:
//
// * A master key becomes a salted, non-reversible 64-bit hash, so the plaintext
//   secret is never stored in the handle. The handle still identifies a specific
//   endpoint, credential, and config and should not be logged.
// * A token credential is keyed by its Python object identity. The cache holds a
//   reference to it, so its address can't be reused by another live credential while
//   cached. The token value is never read.
// * A config is keyed by the hash of its `PreparedClientConfig` repr: equal configs
//   render equal reprs, different configs differ.
//
// The parts are tagged (`mk:` / `tc:` / `cfg:`) so they can't collide.

// Per-process random salt for the master-key and config-repr hashes. `RandomState`
// seeds from the OS RNG, so the hash is stable within a process and unpredictable
// across processes.
static SALTED_HASHER: OnceLock<RandomState> = OnceLock::new();

/// Salted, non-reversible 64-bit hash of a string. Used for the master key (so the
/// secret never appears) and the config repr (to keep the handle short).
fn salted_hash(value: &str) -> u64 {
    let state = SALTED_HASHER.get_or_init(RandomState::new);
    let mut hasher = state.build_hasher();
    value.hash(&mut hasher);
    hasher.finish()
}

/// Fingerprint a master-key credential as an `mk:`-tagged salted hash so the
/// plaintext key is not stored. The fingerprint is still part of the internal
/// driver identity and should not be logged.
fn master_key_fingerprint(master_key: &str) -> String {
    format!("mk:{:016x}", salted_hash(master_key))
}

/// Fingerprint a token credential by its Python object identity, tagged `tc:`. The
/// `mk:` / `tc:` / `cfg:` tags keep the parts from colliding.
fn token_credential_fingerprint(object_id: usize) -> String {
    format!("tc:{object_id:x}")
}

/// Fingerprint a config from its repr: a `cfg:`-tagged salted hash, or `cfg:none`
/// when no config was given. Equal configs render equal reprs and share a driver.
fn config_fingerprint_from_repr(repr: Option<&str>) -> String {
    match repr {
        Some(repr) => format!("cfg:{:016x}", salted_hash(repr)),
        None => "cfg:none".to_string(),
    }
}

/// Read the config's `repr()` (a Python object, so under the GIL) and hash it into a
/// `cfg:` fingerprint. An absent config yields `cfg:none`.
fn config_fingerprint(config: Option<&Bound<'_, PyAny>>) -> PyResult<String> {
    match config {
        None => Ok(config_fingerprint_from_repr(None)),
        Some(cfg) => {
            // `to_string_lossy` reads the text under abi3 (zero-copy `to_str` is not
            // in the limited API). A Python repr() is valid UTF-8, so nothing is lost.
            let repr = cfg.repr()?;
            let repr_str = repr.to_string_lossy();
            Ok(config_fingerprint_from_repr(Some(repr_str.as_ref())))
        }
    }
}

/// Join the endpoint and the two fingerprints into the cache key / handle. The
/// unit-separator delimiter can't appear in a URL or a fingerprint, so two different
/// triples never produce the same key.
fn compose_cache_key(endpoint: &str, credential_fp: &str, config_fp: &str) -> String {
    format!("{endpoint}\u{1f}{credential_fp}\u{1f}{config_fp}")
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

const AUTH_REQUIRED_ERROR: &str = "init_client requires either a master_key or a token credential";
const AUTH_EXCLUSIVE_ERROR: &str =
    "init_client received both master_key and token credential; exactly one must be set";

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
    let ctx_or_error = RUNTIME_CONTEXT.get_or_init(|| {
        py.allow_threads(|| {
            let tokio_rt =
                TokioRuntime::new().map_err(|e| format!("failed to start tokio runtime: {e}"))?;
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
    match ctx_or_error {
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
/// must not (re)build it. Raises a clear "init_client must be called before
/// {op_name}" if no client has initialized the runtimes yet. Without it, an
/// operation issued before `init_client` would fail deep down with an obscure
/// error instead of a plain one naming the missing step.
pub(crate) fn require_runtime_context(op_name: &str) -> PyResult<&'static RuntimeContext> {
    match RUNTIME_CONTEXT.get() {
        Some(Ok(ctx)) => Ok(ctx),
        Some(Err(message)) => Err(PyRuntimeError::new_err(message.clone())),
        None => Err(PyRuntimeError::new_err(format!(
            "init_client must be called before {op_name}"
        ))),
    }
}

// ---------------------------------------------------------------------------
// init_client
// ---------------------------------------------------------------------------
//
// The entry point, called once on a rust-backed client's first Rust operation.
// It returns the driver handle -- the `(endpoint, credential, config)` cache key
// -- and makes sure a rust driver for that key exists:
//   * Fast path: a driver for this key already exists (another client with the
//     same endpoint, credential, and config), so just add one reference and reuse
//     it. This is what makes same-settings clients share one rust driver.
//   * Slow path: no driver yet, so build one on the shared Tokio runtime (via the
//     process-wide driver runtime) and insert it as the first reference.
// Process-wide vs per-key: the runtimes are shared once for the process; the rust
// driver this builds is per key. The optional `config` is a Python
// `PreparedClientConfig` of construction settings the driver honors --
// preferred_locations, process-wide connection-pool settings, plus account-level
// operation options (excluded locations, throttle-retry caps, hedging threshold,
// consistency level). They apply when the runtime/driver is first built; later
// clients with the same key share the driver.
// Without this entry point there would be no way to get or make a client's rust
// driver, and no reference counting to share and tear it down safely.

#[pyfunction]
#[pyo3(signature = (endpoint, master_key=None, config=None, credential=None))]
pub(crate) fn init_client(
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

    // Fingerprint the credential first so it joins the key: a different credential
    // must not reuse another's driver. Reading a token credential's identity or
    // hashing the master key exposes no secret. Erroring when neither is given stops
    // a credential-less call before it builds a driver.
    let credential_fp = match credential {
        Some(token_credential) => token_credential_fingerprint(token_credential.as_ptr() as usize),
        None => {
            let key = master_key.ok_or_else(|| PyValueError::new_err(AUTH_REQUIRED_ERROR))?;
            master_key_fingerprint(key)
        }
    };
    // Fingerprint the config so it joins the key too. Read here under the GIL, since
    // config is a Python object. An absent config maps to `cfg:none`.
    let config_fp = config_fingerprint(config)?;
    let handle = compose_cache_key(endpoint, &credential_fp, &config_fp);

    // Fast path: a driver for this key already exists, so this is another client with
    // the same endpoint, credential, and config. Add a reference and reuse it. A
    // write lock is taken because we change the count; init_client runs once per
    // client.
    {
        let mut cache = drivers().write();
        if let Some(entry) = cache.get_mut(&handle) {
            entry.refcount += 1;
            return Ok(handle);
        }
    }

    // Read the client-construction settings while the GIL is still held (config
    // is a Python object). An absent config leaves both routing and the
    // per-account operation options unset, so the driver is built with only the
    // account and otherwise keeps its defaults.
    let (preferred_regions, operation_options, user_agent_suffix, fault_rules) = match config {
        Some(client_config) => (
            preferred_regions_from_config(client_config)?,
            operation_options_from_config(client_config)?,
            user_agent_suffix_from_config(client_config)?,
            fault_rules_from_config(client_config)?,
        ),
        None => (Vec::new(), None, None, Vec::new()),
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
    // account itself, so always build one. When the client tuned nothing, the
    // builder gets only the account and the driver keeps its defaults; each
    // present setting is layered on top.
    let driver_options = {
        let mut builder = DriverOptions::builder(account);
        if !preferred_regions.is_empty() {
            builder = builder.with_preferred_regions(preferred_regions);
        }
        if let Some(operation_options) = operation_options {
            builder = builder.with_operation_options(operation_options);
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
    // handle with the GIL released. Spawning -- rather than running the build
    // directly on this thread -- lets several clients build at the same time on the
    // runtime's worker threads instead of competing on the calling threads, which
    // was making the first call on each of many newly built clients slow. A panic
    // during the build comes back as a JoinError we turn into a Python error rather
    // than crashing the process.
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
        match cache.get_mut(&handle) {
            Some(entry) => {
                entry.refcount += 1;
                surplus_driver = Some(driver);
            }
            None => {
                cache.insert(
                    handle.clone(),
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

    Ok(handle)
}

/// Read the process-wide connection-pool settings from the prepared config.
fn runtime_settings_from_config(config: Option<&Bound<'_, PyAny>>) -> PyResult<RuntimeSettings> {
    let Some(client_config) = config else {
        return Ok(RuntimeSettings::default());
    };
    let read_timeout = timeout_from_config(client_config, "read_timeout_seconds")?;
    Ok(RuntimeSettings {
        proxy_allowed: get_config_opt::<bool>(client_config, "proxy_allowed")?,
        max_connect_timeout: timeout_from_config(client_config, "connection_timeout_seconds")?,
        max_dataplane_request_timeout: read_timeout,
        max_metadata_request_timeout: read_timeout,
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
/// Matches how `extract_op_modifiers` reads `excludedlocations`: it accepts any
/// Python sequence of strings (the `PreparedClientConfig` stores a tuple) and
/// lets the driver normalize each name ("West US" -> "westus"). A config object
/// without the attribute, or a Python `None`, yields no regions rather than an
/// error, so the binding stays compatible with config shapes that predate or
/// postdate this field; the driver then keeps its default endpoint ordering.
fn preferred_regions_from_config(config: &Bound<'_, PyAny>) -> PyResult<Vec<Region>> {
    let value = match config.getattr("preferred_locations") {
        Ok(value) => value,
        Err(_) => return Ok(Vec::new()),
    };
    if value.is_none() {
        return Ok(Vec::new());
    }
    let region_names: Vec<String> = value.extract().map_err(|e| {
        PyValueError::new_err(format!(
            "preferred_locations must be a sequence of region-name strings: {e}"
        ))
    })?;
    Ok(region_names.into_iter().map(Region::from).collect())
}

/// Read the optional `user_agent_suffix` and turn it into the driver's
/// `UserAgentSuffix`, which it stamps on every request's User-Agent. A missing
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
/// per-account settings -- excluded regions, throttle-retry caps, the hedging
/// threshold, and the chosen read consistency level. These are carried on the
/// "account" layer the driver applies to every request the client makes.
///
/// Returns `None` when the config carries none of them, so a client that only
/// set (say) `preferred_locations` still passes no operation options and the
/// driver keeps its defaults. Each field is read defensively: a missing
/// attribute or a Python `None` is "unset" rather than an error, so the binding
/// stays compatible with older/newer `PreparedClientConfig` shapes.
fn operation_options_from_config(config: &Bound<'_, PyAny>) -> PyResult<Option<OperationOptions>> {
    let mut builder = OperationOptionsBuilder::new();
    let mut any_set = false;

    // excluded_locations -> ExcludedRegions. Same collection shape the
    // per-operation `excludedLocations` option already uses; the driver
    // normalizes each region name.
    if let Some(region_names) = get_config_opt::<Vec<String>>(config, "excluded_locations")? {
        if !region_names.is_empty() {
            builder = builder
                .with_excluded_regions(region_names.into_iter().collect::<ExcludedRegions>());
            any_set = true;
        }
    }

    // throttling_max_retry_count / _wait_time_seconds -> ThrottlingRetryOptions.
    // Carried only when the customer tuned one of them; an untuned client leaves
    // the driver's defaults (9 retries / 30 s) in place, which match Python-core.
    let max_retry_count = get_config_opt::<u32>(config, "throttling_max_retry_count")?;
    let max_retry_wait_seconds =
        get_config_opt::<f64>(config, "throttling_max_retry_wait_time_seconds")?;
    if max_retry_count.is_some() || max_retry_wait_seconds.is_some() {
        let mut throttle = ThrottlingRetryOptionsBuilder::new();
        if let Some(count) = max_retry_count {
            throttle = throttle.with_max_retry_count(count);
        }
        if let Some(seconds) = max_retry_wait_seconds {
            // Guard against non-finite / negative values, which would panic in
            // Duration::from_secs_f64; treat them as "unset" like the timeout path.
            if seconds.is_finite() && seconds >= 0.0 {
                throttle = throttle.with_max_retry_wait_time(Duration::from_secs_f64(seconds));
            }
        }
        builder = builder.with_throttling_retry_options(throttle.build());
        any_set = true;
    }

    // hedging threshold -> AvailabilityStrategy::Hedging. Present only when the
    // customer enabled hedging (availability_strategy True / dict). The Python
    // side already validated threshold_ms > 0; a 0 here (only reachable from a
    // hand-built config) makes HedgeThreshold::new return None, which we treat as
    // "no hedging" rather than an error.
    if let Some(threshold_ms) = get_config_opt::<u64>(config, "hedging_threshold_ms")? {
        if let Some(threshold) = HedgeThreshold::new(Duration::from_millis(threshold_ms)) {
            builder = builder.with_availability_strategy(AvailabilityStrategy::Hedging(
                HedgingStrategy::new(threshold),
            ));
            any_set = true;
        }
    }

    // consistency_level -> ReadConsistencyStrategy. Set only when the customer
    // chose a level at construction; an untuned client carries nothing, so the
    // driver keeps the account default. The Python layer already rejected the
    // levels the driver can't carry (Bounded Staleness / Consistent Prefix), so a
    // value reaching here is one of the supported three; an unrecognized value is
    // still rejected here rather than dropped.
    if let Some(level) = get_config_opt::<String>(config, "consistency_level")? {
        if !level.is_empty() {
            match read_consistency_from_str(&level) {
                Some(strategy) => {
                    builder = builder.with_read_consistency_strategy(strategy);
                    any_set = true;
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

    Ok(if any_set { Some(builder.build()) } else { None })
}

/// Map a Python consistency-level string to the driver's `ReadConsistencyStrategy`.
///
/// Only the levels the driver supports are accepted: `"Eventual"` and `"Session"`
/// map directly, and `"Strong"` maps to the driver's `GlobalStrong` (the driver
/// has no plain `Strong`). Bounded Staleness and Consistent Prefix have no
/// equivalent and are rejected by the Python layer before they reach here; any
/// other value returns `None` so the caller raises rather than dropping the level.
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

#[pyfunction]
pub(crate) fn close_client(handle: &str) -> PyResult<()> {
    // Drop one client's reference; only the last closer evicts the driver. An unknown
    // handle is a no-op, so close stays idempotent and safe from both close() and
    // __del__. The evicted entry is removed under the lock but dropped after it, so a
    // CosmosDriver's teardown never runs while the cache lock is held.
    let evicted: Option<DriverEntry> = {
        let mut cache = drivers().write();
        let evict = match cache.get_mut(handle) {
            Some(entry) => {
                let (next, evict) = apply_close(entry.refcount);
                entry.refcount = next;
                evict
            }
            None => false,
        };
        if evict {
            cache.remove(handle)
        } else {
            None
        }
    };
    drop(evicted);
    Ok(())
}

#[pyfunction]
pub(crate) fn fault_injection_rule_hit_count(handle: &str, rule_id: &str) -> PyResult<u32> {
    let cache = drivers().read();
    let entry = cache
        .get(handle)
        .ok_or_else(|| PyValueError::new_err("unknown or closed Rust client handle"))?;
    let rule = entry.fault_rules.get(rule_id).ok_or_else(|| {
        PyValueError::new_err(format!("unknown fault injection rule id: {rule_id:?}"))
    })?;
    Ok(rule.hit_count())
}

#[cfg(test)]
mod tests {
    use super::{
        apply_close, compose_cache_key, config_fingerprint_from_repr,
        connection_pool_from_settings, get_config_opt, master_key_fingerprint,
        read_consistency_from_str, runtime_settings_conflict, runtime_settings_from_config,
        token_credential_fingerprint, validate_auth_inputs, RuntimeSettings, AUTH_EXCLUSIVE_ERROR,
        AUTH_REQUIRED_ERROR,
    };
    use azure_data_cosmos_driver::options::ReadConsistencyStrategy;
    use pyo3::prelude::*;
    use pyo3::types::{PyModule, PyString};
    use std::time::Duration;

    // The reference-counted driver cache evicts an endpoint's driver only when
    // its last client closes. apply_close is the decision behind that: it must
    // drop the count by one and report "evict" exactly when the count reaches
    // zero. This is the rule that stops one client's close from removing the
    // driver while another client to the same account is still using it.
    #[test]
    fn apply_close_drops_one_reference_and_evicts_only_at_zero() {
        // Two clients share the driver: closing one leaves it alive (one left).
        assert_eq!(apply_close(2), (1, false));
        // The last client closing takes the count to zero and evicts.
        assert_eq!(apply_close(1), (0, true));
    }

    #[test]
    fn apply_close_on_zero_is_a_saturating_no_op_evict() {
        // A stray extra close on an already-zero entry must not underflow; it
        // stays at zero and is reported evictable (a harmless re-remove).
        assert_eq!(apply_close(0), (0, true));
    }

    // The customer's chosen consistency level must reach the driver. The three
    // supported levels map onto the driver's strategy type (Strong -> GlobalStrong,
    // the driver has no plain Strong), and anything else returns None so the caller
    // raises rather than dropping the level.
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
        // Bounded Staleness / Consistent Prefix have no driver equivalent; the
        // Python layer rejects them first, but the binding is defensive too.
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
    // The cache is keyed by (endpoint, credential). These tests pin the security
    // property that makes that fail-closed: the same credential fingerprints
    // stably (so it shares a driver), different credentials fingerprint
    // differently (so they never share -- no silent auth substitution), and a
    // master key and a token credential can never collide on one fingerprint.

    #[test]
    fn master_key_fingerprint_is_stable_for_equal_keys() {
        // Same key string -> same fingerprint within the process, so two clients
        // with the same master key share one driver.
        assert_eq!(
            master_key_fingerprint("secret-key"),
            master_key_fingerprint("secret-key")
        );
    }

    #[test]
    fn master_key_fingerprint_differs_for_different_keys() {
        // Different keys -> different fingerprints, so a different credential is a
        // cache miss and gets its own driver instead of reusing another's auth.
        assert_ne!(
            master_key_fingerprint("key-a"),
            master_key_fingerprint("key-b")
        );
    }

    #[test]
    fn master_key_fingerprint_does_not_leak_the_key() {
        // The fingerprint must be safe to put in the (logged) handle: it must not
        // contain the secret in cleartext.
        let key = "super-secret-master-key";
        let fp = master_key_fingerprint(key);
        assert!(fp.starts_with("mk:"));
        assert!(!fp.contains(key));
    }

    #[test]
    fn master_key_and_token_fingerprints_never_collide() {
        // Distinct namespaces (mk: vs tc:) guarantee a master key and a token
        // credential can never produce the same fingerprint, even by chance.
        let master = master_key_fingerprint("anything");
        let token = token_credential_fingerprint(0xDEAD_BEEF);
        assert!(master.starts_with("mk:"));
        assert!(token.starts_with("tc:"));
        assert_ne!(master, token);
    }

    #[test]
    fn token_credential_fingerprint_tracks_object_identity() {
        // The same object identity (address) fingerprints equally (shared driver);
        // a different identity fingerprints differently (its own driver).
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
        // Equal config reprs fingerprint equally (shared driver); different reprs
        // fingerprint differently (its own driver); absent config is a fixed value.
        let a = "PreparedClientConfig(preferred_locations=('West US',))";
        let b = "PreparedClientConfig(preferred_locations=('East US',))";
        assert_eq!(
            config_fingerprint_from_repr(Some(a)),
            config_fingerprint_from_repr(Some(a))
        );
        assert_ne!(
            config_fingerprint_from_repr(Some(a)),
            config_fingerprint_from_repr(Some(b))
        );
        assert_eq!(config_fingerprint_from_repr(None), "cfg:none");
        // A present config never collides with the no-config sentinel.
        assert_ne!(
            config_fingerprint_from_repr(Some(a)),
            config_fingerprint_from_repr(None)
        );
    }

    #[test]
    fn config_and_credential_fingerprints_never_collide() {
        // The cfg: namespace keeps a config fingerprint from ever matching a
        // credential one, so the three key parts stay independent.
        let cfg = config_fingerprint_from_repr(Some("PreparedClientConfig()"));
        assert!(cfg.starts_with("cfg:"));
        assert!(!cfg.starts_with("mk:"));
        assert!(!cfg.starts_with("tc:"));
    }

    #[test]
    fn cache_key_separates_endpoint_credential_and_config() {
        let endpoint = "https://acct.documents.azure.com";
        let cred_a = master_key_fingerprint("key-a");
        let cred_b = master_key_fingerprint("key-b");
        let cfg_a = config_fingerprint_from_repr(Some("cfg-a"));
        let cfg_b = config_fingerprint_from_repr(Some("cfg-b"));

        // Same endpoint + credential + config -> same key (one shared driver).
        assert_eq!(
            compose_cache_key(endpoint, &cred_a, &cfg_a),
            compose_cache_key(endpoint, &cred_a, &cfg_a)
        );
        // A different credential -> different key (no sharing).
        assert_ne!(
            compose_cache_key(endpoint, &cred_a, &cfg_a),
            compose_cache_key(endpoint, &cred_b, &cfg_a)
        );
        // A different config -> different key (no sharing, settings honored).
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
    fn cache_key_delimiter_prevents_aliasing() {
        // Without separators, ("ab","c","d") and ("a","bc","d") would both
        // concatenate to "abcd" and alias to one key. The unit-separator delimiter
        // -- which real endpoints and mk:/tc:/cfg: fingerprints never contain --
        // keeps every distinct (endpoint, credential, config) triple mapped to a
        // distinct key.
        assert_ne!(
            compose_cache_key("ab", "c", "d"),
            compose_cache_key("a", "bc", "d")
        );
        assert_ne!(
            compose_cache_key("a", "b", "cd"),
            compose_cache_key("a", "bc", "d")
        );
    }
}

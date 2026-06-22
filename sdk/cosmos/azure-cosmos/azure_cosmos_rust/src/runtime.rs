// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Per-process runtime, the per-endpoint driver cache, and the client lifecycle
//! entry points (`init_client` / `close_client`).
//!
//! One Tokio runtime plus one `CosmosDriverRuntime` are stood up lazily on the
//! first `init_client` and live for the process. Drivers are cached per endpoint
//! and reference-counted so two clients to one account share a single driver and
//! it is evicted only when the last one closes.

use std::collections::HashMap;
use std::sync::{Arc, OnceLock, RwLock};
use std::time::Duration;

use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;

use azure_data_cosmos_driver::{
    driver::{CosmosDriver, CosmosDriverRuntime},
    models::AccountReference,
    options::{
        AvailabilityStrategy, DriverOptions, ExcludedRegions, HedgeThreshold, HedgingStrategy,
        OperationOptions, OperationOptionsBuilder, ReadConsistencyStrategy, Region,
        ThrottlingRetryOptionsBuilder, UserAgentSuffix,
    },
};
use tokio::runtime::Runtime as TokioRuntime;
use url::Url;

use crate::credential::PyTokenCredential;

// ---------------------------------------------------------------------------
// Per-process singletons
// ---------------------------------------------------------------------------
//
// One runtime context (Tokio runtime + CosmosDriverRuntime), and a per-endpoint
// cache of CosmosDrivers. All three are lazily initialised on the first
// init_client call and live for the lifetime of the Python process.

pub(crate) struct RuntimeContext {
    pub(crate) tokio_rt: TokioRuntime,
    pub(crate) driver_runtime: Arc<CosmosDriverRuntime>,
}

/// One cached driver plus a count of how many live Python clients reference it.
///
/// `init_client` returns the endpoint string as the handle, so every
/// `CosmosClient` built against the same account in one process shares a single
/// `CosmosDriver`. The driver runtime no longer caches by endpoint -- its
/// `create_driver` builds a fresh driver on every call -- so this map is the
/// authoritative per-endpoint cache: `init_client` builds a driver only on a
/// miss here and reuses the existing entry on a hit. Because the entry is
/// shared, it must outlive *every* sharer: `init_client` adds a reference and
/// `close_client` drops one, evicting the driver only when the count reaches
/// zero. Without the count, closing one of two clients to the same account would
/// evict the driver the other is still using, and that client's next operation
/// would fail with "no driver registered".
pub(crate) struct DriverEntry {
    pub(crate) driver: Arc<CosmosDriver>,
    refcount: usize,
}

/// Decide a `DriverEntry`'s next refcount and whether it should now be evicted,
/// given its current refcount. Pulled out of `close_client` so the
/// drop-one-reference / evict-at-zero rule can be unit-tested without building a
/// real `CosmosDriver`. `saturating_sub` keeps an already-zero count from
/// wrapping, so a stray extra close is a harmless no-op rather than underflow.
fn apply_close(refcount: usize) -> (usize, bool) {
    let next = refcount.saturating_sub(1);
    (next, next == 0)
}

// Keep init errors too, so every later caller sees the same failure reason.
static RUNTIME_CONTEXT: OnceLock<Result<RuntimeContext, String>> = OnceLock::new();
static DRIVERS: OnceLock<RwLock<HashMap<String, DriverEntry>>> = OnceLock::new();

pub(crate) fn drivers() -> &'static RwLock<HashMap<String, DriverEntry>> {
    DRIVERS.get_or_init(|| RwLock::new(HashMap::new()))
}

fn runtime_context(py: Python<'_>) -> PyResult<&'static RuntimeContext> {
    let ctx_or_error = RUNTIME_CONTEXT.get_or_init(|| {
        py.allow_threads(|| {
            let tokio_rt =
                TokioRuntime::new().map_err(|e| format!("failed to start tokio runtime: {e}"))?;
            let driver_runtime = tokio_rt
                .block_on(async { CosmosDriverRuntime::builder().build().await })
                .map_err(|e| format!("driver runtime build failed: {e}"))?;
            Ok(RuntimeContext {
                tokio_rt,
                driver_runtime,
            })
        })
    });
    match ctx_or_error {
        Ok(ctx) => Ok(ctx),
        Err(message) => Err(PyRuntimeError::new_err(message.clone())),
    }
}

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
// Idempotent in that subsequent calls with the same endpoint return the same
// handle without rebuilding the driver; each such call also adds one reference
// to the cached driver so it survives until every client sharing it has closed
// (see close_client). Subsequent calls with a different endpoint construct a new
// driver against the shared runtime.
//
// The optional `config` is a Python `PreparedClientConfig` carrying the
// client-construction settings the driver can honor: preferred_locations
// (endpoint ordering) plus the per-account operation options -- excluded
// locations, throttle-retry caps, the hedging threshold, and the chosen
// consistency level. They are applied only when an endpoint's driver is first
// built; a second client to the same endpoint reuses the existing driver and
// its original options.

#[pyfunction]
#[pyo3(signature = (endpoint, master_key=None, config=None, credential=None))]
pub(crate) fn init_client(
    py: Python<'_>,
    endpoint: &str,
    master_key: Option<&str>,
    config: Option<&Bound<'_, PyAny>>,
    credential: Option<&Bound<'_, PyAny>>,
) -> PyResult<String> {
    let endpoint_url = Url::parse(endpoint)
        .map_err(|e| PyValueError::new_err(format!("invalid endpoint URL: {e}")))?;

    let runtime_ctx = runtime_context(py)?;

    let handle = endpoint.to_string();

    // Fast path: the driver for this endpoint already exists, so this is a
    // second (or later) client to the same account. Record one more reference
    // and reuse it -- the existing driver and its original options stand; this
    // client's options are intentionally ignored. A write lock (not the old
    // read lock) is taken because we mutate the refcount; init_client runs once
    // per client, so this is not a hot path.
    {
        let mut cache = drivers().write().unwrap();
        if let Some(entry) = cache.get_mut(&handle) {
            entry.refcount += 1;
            return Ok(handle);
        }
    }

    // Read the client-construction settings while the GIL is still held (config
    // is a Python object). An absent config leaves both routing and the
    // per-account operation options unset, so the driver is built with only the
    // account and otherwise keeps its defaults.
    let (preferred_regions, operation_options, user_agent_suffix) = match config {
        Some(client_config) => (
            preferred_regions_from_config(client_config)?,
            operation_options_from_config(client_config)?,
            user_agent_suffix_from_config(client_config)?,
        ),
        None => (Vec::new(), None, None),
    };

    // Slow path: build the driver. Held without any of our locks because
    // create_driver is async and may take seconds. The account carries
    // whichever auth the caller supplied: a token credential (wrapped so the
    // driver can call back into Python for tokens) takes precedence; otherwise
    // the master key. The Python factory guarantees exactly one is present.
    let account = match credential {
        Some(token_credential) => {
            let py_credential: Py<PyAny> = token_credential.clone().unbind();
            AccountReference::with_credential(
                endpoint_url,
                Arc::new(PyTokenCredential::new(py_credential)),
            )
        }
        None => {
            let key = master_key.ok_or_else(|| {
                PyValueError::new_err(
                    "init_client requires either a master_key or a token credential",
                )
            })?;
            AccountReference::with_master_key(endpoint_url, key.to_string())
        }
    };

    // `create_driver` takes a single `DriverOptions` that now carries the account
    // itself, and it is no longer optional, so always build one. When the client
    // tuned nothing, the builder gets only the account and the driver keeps its
    // defaults (equivalent to the old no-options path); each present setting is
    // layered on top.
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
        builder.build()
    };

    let driver = py
        .allow_threads(|| {
            runtime_ctx
                .tokio_rt
                .block_on(runtime_ctx.driver_runtime.create_driver(driver_options))
        })
        .map_err(|e| PyRuntimeError::new_err(format!("driver init failed: {e}")))?;

    // Insert under write lock, counting this client as the first reference. If
    // two threads raced to build the same endpoint, each built its own distinct
    // driver (create_driver no longer dedups by endpoint); the first to take the
    // lock wins and the loser's freshly built driver is dropped here, so the
    // endpoint still ends up with exactly one shared driver and the count still
    // matches the number of live clients (each will call close_client exactly
    // once).
    {
        let mut cache = drivers().write().unwrap();
        cache
            .entry(handle.clone())
            .or_insert_with(|| DriverEntry {
                driver,
                refcount: 0,
            })
            .refcount += 1;
    }

    Ok(handle)
}

/// Read the optional `preferred_locations` off the prepared client config and
/// turn each region name into a driver `Region` for preferred-region routing.
///
/// Mirrors how `extract_op_modifiers` reads `excludedlocations`: it accepts any
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

/// Read the optional `user_agent_suffix` off the prepared client config and turn
/// it into the driver's typed `UserAgentSuffix`, so the driver stamps it on the
/// User-Agent of every request it issues -- the startup-time analog of the legacy
/// `user_agent_suffix` kwarg. A missing attribute, a Python `None`, or an empty
/// string yields `None`, leaving the driver's default SDK User-Agent in place.
/// (`build_client_config` already normalizes an empty suffix to `None`, so an
/// empty string only reaches here from a hand-built config.)
///
/// The driver's `UserAgentSuffix` is stricter than the legacy path: at most
/// `UserAgentSuffix::MAX_LENGTH` (25) header-safe characters (alphanumeric, `-`,
/// `_`, `.`, `~`). A present value that fails that validation is a hard error
/// rather than a silent drop -- a misconfigured label is loud, matching how the
/// other readers treat a present-but-malformed value -- which also avoids
/// re-introducing the very "suffix silently goes nowhere" gap this carries it to
/// close. `try_new` (not `new`) is used so an over-long/invalid value surfaces as
/// a `ValueError` instead of panicking across the FFI boundary.
fn user_agent_suffix_from_config(
    config: &Bound<'_, PyAny>,
) -> PyResult<Option<UserAgentSuffix>> {
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

/// Build a driver-level `OperationOptions` from the prepared client config's
/// per-account settings -- excluded regions, throttle-retry caps, the hedging
/// threshold, and the chosen read consistency level. These ride on the
/// "account" layer the driver applies to every request the client makes.
///
/// Returns `None` when the config carries none of them, so a client that only
/// set (say) `preferred_locations` still passes no operation options and the
/// driver keeps its defaults. Each field is read defensively: a missing
/// attribute or a Python `None` is "unset" rather than an error, so the binding
/// stays compatible with older/newer `PreparedClientConfig` shapes.
fn operation_options_from_config(
    config: &Bound<'_, PyAny>,
) -> PyResult<Option<OperationOptions>> {
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
        Err(_) => Ok(None),
    }
}

#[pyfunction]
pub(crate) fn close_client(handle: &str) -> PyResult<()> {
    // Drop one client's reference. Only the last client to the endpoint evicts
    // the shared driver; earlier closers just decrement the count so a still-open
    // client to the same account keeps a working driver. An unknown handle (never
    // built, or already evicted) is a no-op, which keeps close idempotent and
    // safe to call from both close() and __del__.
    let mut cache = drivers().write().unwrap();
    let should_evict = match cache.get_mut(handle) {
        Some(entry) => {
            let (next, evict) = apply_close(entry.refcount);
            entry.refcount = next;
            evict
        }
        None => false,
    };
    if should_evict {
        cache.remove(handle);
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{apply_close, read_consistency_from_str};
    use azure_data_cosmos_driver::options::ReadConsistencyStrategy;

    // The reference-counted driver cache evicts an endpoint's driver only when
    // its last client closes. apply_close is the decision behind that: it must
    // drop the count by one and report "evict" exactly when the count reaches
    // zero. This is the rule that stops one client's close from pulling the
    // driver out from under another client to the same account.
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
}


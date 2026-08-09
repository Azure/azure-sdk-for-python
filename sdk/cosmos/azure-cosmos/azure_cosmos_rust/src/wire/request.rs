// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use std::collections::HashMap;
use std::time::Duration;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyDict;

use azure_core::http::headers::{HeaderName, HeaderValue};
use azure_data_cosmos_driver::{
    models::{PartitionKey, PartitionKeyValue},
    options::{
        AvailabilityStrategy, ContentResponseOnWrite, EndToEndOperationLatencyPolicy,
        ExcludedRegions, HedgeThreshold, HedgingStrategy, OperationOptionsBuilder,
    },
};

use serde::Deserialize;

use super::feed_range::{FeedRangePartitionKeyInput, FeedRangePartitionKeySource};
use super::query::QueryTarget;

// ---------------------------------------------------------------------------
// Shared prepared-request input extraction
// ---------------------------------------------------------------------------
//
// Each entry point pulls its inputs off the PreparedRequest with these before
// handing a CosmosOperation builder to run_item_operation.

/// Input modifiers lifted out of `PreparedRequest.headers` by
/// `extract_op_modifiers`. Each field corresponds to a header the driver models
/// as a typed option (activity-id, session token, content-response, excluded
/// regions, end-to-end timeout, availability strategy) or to the catch-all
/// custom-headers passthrough. Fields are `pub(crate)` so the operation runners
/// in sibling modules can consume them directly without going through an accessor.
pub(crate) struct OpModifiers {
    pub(crate) activity_header: Option<String>,
    pub(crate) session_header: Option<String>,
    // ``no_response=True`` -> Disabled, otherwise Enabled. The runner
    // applies this on writes (create / upsert / replace) and ignores it on
    // reads / deletes, which have no body to suppress.
    pub(crate) content_response_on_write: ContentResponseOnWrite,
    pub(crate) excluded_regions_value: Option<ExcludedRegions>,
    pub(crate) end_to_end_timeout: Option<EndToEndOperationLatencyPolicy>,
    // Per-request cross-region hedging control lifted from the
    // ``availabilityStrategy`` option-key. ``Disabled`` turns hedging off for
    // this request (the ``availability_strategy=False`` case); ``Hedging(..)``
    // turns it on with the caller's threshold. ``None`` means the caller did
    // not set it and the driver keeps its default.
    pub(crate) availability_strategy: Option<AvailabilityStrategy>,
    pub(crate) custom_headers: HashMap<HeaderName, HeaderValue>,
}

/// Read container-scoped fields and request settings from a prepared request.
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

/// Read the fields an account-level database operation needs from a
/// ``PreparedRequest``.
///
/// Separate from `extract_common_prepared_inputs` because a database operation
/// has no container and no partition key: reading `container_link` and
/// `partition_key_header` here would be two attribute lookups whose results are
/// thrown away, and it would let a caller believe those fields mean something
/// for a database request. The tuple orders its parts like
/// `extract_common_prepared_inputs`: the identifying value first, the modifiers
/// last.
///
/// Without it a database request goes through the container-shaped reader, which
/// still works -- the prepared request carries an empty container link and an
/// empty partition key -- but it reads two fields that mean nothing here and
/// suggests to the next reader that they do.
pub(crate) fn extract_database_prepared_inputs<'py>(
    prepared: &Bound<'py, PyAny>,
    error_message: &'static str,
) -> PyResult<(String, OpModifiers)> {
    let database_id = extract_required_item_id(prepared, error_message)?;
    let headers_obj = prepared.getattr("headers")?;
    let headers_dict: &Bound<'py, PyDict> = headers_obj.downcast::<PyDict>()?;
    let modifiers = extract_op_modifiers(headers_dict)?;
    Ok((database_id, modifiers))
}

/// Read request modifiers for an account-level operation with no resource id.
pub(crate) fn extract_account_prepared_modifiers<'py>(
    prepared: &Bound<'py, PyAny>,
) -> PyResult<OpModifiers> {
    let headers_obj = prepared.getattr("headers")?;
    let headers_dict: &Bound<'py, PyDict> = headers_obj.downcast::<PyDict>()?;
    extract_op_modifiers(headers_dict)
}

/// Copy the prepared request body into Rust-owned bytes.
pub(crate) fn extract_body_bytes<'py>(prepared: &Bound<'py, PyAny>) -> PyResult<Vec<u8>> {
    prepared.getattr("body_bytes")?.extract()
}

#[derive(Deserialize)]
struct ReadFeedRangesBody {
    #[serde(rename = "forceRefresh", default)]
    force_refresh: bool,
}

/// Parse the optional `forceRefresh` setting for `read_feed_ranges`.
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

/// Read the `read_feed_ranges` refresh setting from a prepared request.
pub(crate) fn extract_read_feed_ranges_force_refresh<'py>(
    prepared: &Bound<'py, PyAny>,
) -> PyResult<bool> {
    let body_bytes = extract_body_bytes(prepared)?;
    parse_read_feed_ranges_force_refresh(&body_bytes)
}

/// Return the required item id or raise the supplied validation error.
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

/// Option-keys that legitimately appear in the ``PreparedRequest.headers`` dict
/// but are NOT wire headers: they are consumed elsewhere in the Python prep
/// (``disableAutomaticIdGeneration`` -> id minting) or moved to a typed
/// driver field (``partitionKey`` -> the partition-key argument), so
/// `extract_op_modifiers` correctly drops them. Listed here only so the
/// ``COSMOS_WIRE_STRICT`` diagnostic does not flag these expected drops as
/// divergence. Compared against the lowercased key.
const INTENTIONALLY_IGNORED_OPTION_KEYS: &[&str] =
    &["disableautomaticidgeneration", "partitionkey"];

fn is_intentionally_ignored_option_key(lower: &str) -> bool {
    INTENTIONALLY_IGNORED_OPTION_KEYS.contains(&lower)
}

/// ``COSMOS_WIRE_STRICT=1`` (or ``true``) turns the silent drop of an
/// unrecognized option-key in `extract_op_modifiers` into a hard error, so a
/// Python-side wire option that was never wired into Rust is caught in tests/CI
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

/// Split prepared headers into driver settings and headers sent to the service.
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
        // means COSMOS_WIRE_STRICT still guards genuine option-key divergence.
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
            "maxitemcount" => Some("x-ms-max-item-count"),
            "prioritylevel" => Some("x-ms-cosmos-priority-level"),
            "throughputbucket" => Some("x-ms-cosmos-throughput-bucket"),
            "offerthroughput" => Some("x-ms-offer-throughput"),
            "autoupgradepolicy" => Some("x-ms-cosmos-offer-autopilot-settings"),
            "continuation" => Some("x-ms-continuation"),
            "contenttype" => Some("content-type"),
            "correlatedactivityid" => Some("x-ms-cosmos-correlated-activityid"),
            "disableruperminuteusage" => Some("x-ms-documentdb-disable-ru-per-minute-usage"),
            "enablecrosspartitionquery" => Some("x-ms-documentdb-query-enablecrosspartition"),
            "enablescaninquery" => Some("x-ms-documentdb-query-enable-scan"),
            "enablescriptlogging" => Some("x-ms-documentdb-script-enable-logging"),
            "isqueryplanrequest" => Some("x-ms-cosmos-is-query-plan-request"),
            "offerenableruperminutethroughput" => {
                Some("x-ms-offer-is-ru-per-minute-throughput-enabled")
            }
            "offertype" => Some("x-ms-offer-type"),
            "populateindexmetrics" => Some("x-ms-cosmos-populateindexmetrics"),
            "populatepartitionkeyrangestatistics" => {
                Some("x-ms-documentdb-populatepartitionstatistics")
            }
            "populatequeryadvice" => Some("x-ms-cosmos-populatequeryadvice"),
            "populatequerymetrics" => Some("x-ms-documentdb-populatequerymetrics"),
            "populatequotainfo" => Some("x-ms-documentdb-populatequotainfo"),
            "queryversion" => Some("x-ms-cosmos-query-version"),
            "resourcetokenexpiryseconds" => Some("x-ms-documentdb-expiry-seconds"),
            "responsecontinuationtokenlimitinkb" => {
                Some("x-ms-documentdb-responsecontinuationtokenlimitinkb")
            }
            "supportedqueryfeatures" => Some("x-ms-cosmos-supported-query-features"),
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
            // on every create/upsert/replace, ``partitionKey``) are carried in the
            // headers dict but are NOT wire headers -- they are consumed
            // elsewhere in the Python prep (id minting) or moved to a typed
            // driver field (partition key), so dropping them here is correct
            // and matches the legacy path.
            //
            // The hazard (a silent-correctness bug) is a *new* wire
            // option added on the Python side (``flatten_options_to_headers`` /
            // ``COMMON_OPTIONS``) without a matching arm above: it would be
            // dropped here, producing wrong wire bytes with green tests.
            // ``COSMOS_WIRE_STRICT=1`` (for tests / CI / local dev) turns an
            // unrecognized, non-allowlisted key into a hard error so the divergence
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
pub(super) fn build_operation_options(
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

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// Parse "dbs/<db>/colls/<coll>" into ("<db>", "<coll>").
///
/// Reads the four segments off the split iterator instead of collecting into a
/// `Vec`, to avoid allocating one per call. The trailing `None` arm rejects a
/// path with extra segments.
pub(super) fn parse_container_link(link: &str) -> PyResult<(String, String)> {
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

/// Parse `dbs/<db>` into a database name.
pub(super) fn parse_database_link(link: &str) -> PyResult<String> {
    let mut parts = link.split('/');
    match (parts.next(), parts.next(), parts.next()) {
        (Some("dbs"), Some(db), None) if !db.is_empty() => Ok(db.to_string()),
        _ => Err(PyValueError::new_err(format!(
            "database link must be 'dbs/<db>', got {link:?}"
        ))),
    }
}

/// Read the database name and request settings for a container feed.
pub(crate) fn extract_container_feed_prepared_inputs<'py>(
    prepared: &Bound<'py, PyAny>,
) -> PyResult<(String, OpModifiers)> {
    let link: String = prepared.getattr("container_link")?.extract()?;
    let database_id = parse_database_link(&link)?;
    let headers_obj = prepared.getattr("headers")?;
    let headers_dict: &Bound<'py, PyDict> = headers_obj.downcast::<PyDict>()?;
    let modifiers = extract_op_modifiers(headers_dict)?;
    Ok((database_id, modifiers))
}

/// Read database and container names plus request settings for a container read.
pub(crate) fn extract_container_point_prepared_inputs<'py>(
    prepared: &Bound<'py, PyAny>,
) -> PyResult<(String, String, OpModifiers)> {
    let link: String = prepared.getattr("container_link")?.extract()?;
    let (database_id, container_id) = parse_container_link(&link)?;
    let headers_obj = prepared.getattr("headers")?;
    let headers_dict: &Bound<'py, PyDict> = headers_obj.downcast::<PyDict>()?;
    let modifiers = extract_op_modifiers(headers_dict)?;
    Ok((database_id, container_id, modifiers))
}

/// Parse the JSON-array partition-key header into a typed `PartitionKey`.
///
/// Accepts every shape the Python helper emits:
///
///   * Single scalar:                  `["customerA"]`, `[123]`, `[true]`, `[null]`
///   * Undefined (PK path missing):    `[{}]`        -> `PartitionKeyValue::undefined()`
///   * Hierarchical (2 or 3 levels):   `["t1","r1"]`, `["t1","r1","s1"]`
///   * Hierarchical with missing leaf: `["t1",null]`
///
/// The one shape still rejected is the bare empty array `[]`, which the driver
/// overloads to mean "cross-partition query" (`PartitionKey::EMPTY` emits the
/// `x-ms-documentdb-query-enablecrosspartition` header instead of
/// `x-ms-documentdb-partitionkey: []`). Until the driver separates those two
/// concepts, this fails fast so a partitionless-container write cannot silently
/// land in the wrong place.
pub(super) fn parse_partition_key_header(header: &str) -> PyResult<PartitionKey> {
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
pub(super) fn parse_feed_range_partition_key_header(
    header: &str,
) -> PyResult<FeedRangePartitionKeyInput> {
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
pub(super) fn parse_query_target_header(header: &str) -> PyResult<QueryTarget> {
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

/// A partial view of a document body that deserializes only the `id` field.
///
/// This skips the rest of the document, so a large body isn't parsed in full
/// just to get one string. The `id` is kept as a `Value` so a
/// present-but-non-string value still gives the "no string id" error rather
/// than a deserialization failure.
#[derive(Deserialize)]
struct BodyId {
    id: Option<serde_json::Value>,
}

/// Read the document `id` out of a JSON body.
///
/// The caller guarantees it is present; we error if it is not rather than
/// inventing one.
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
        extract_account_prepared_modifiers, extract_database_prepared_inputs, extract_item_id,
        extract_op_modifiers, is_intentionally_ignored_option_key, json_value_to_pk_component,
        parse_availability_strategy, parse_container_link, parse_feed_range_partition_key_header,
        parse_partition_key_header, parse_query_target_header,
        parse_read_feed_ranges_force_refresh, FeedRangePartitionKeySource, QueryTarget,
        DEFAULT_HEDGE_THRESHOLD_MS,
    };
    use azure_core::http::headers::{HeaderName, HeaderValue};
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
        // Prep-internal flags that legitimately appear in the headers dict but are
        // NOT wire headers must be on the allowlist, so COSMOS_WIRE_STRICT does
        // not flag the expected silent drop as divergence. Keys are compared lowered.
        assert!(is_intentionally_ignored_option_key(
            "disableautomaticidgeneration"
        ));
        assert!(is_intentionally_ignored_option_key("partitionkey"));
        // A would-be new wire option (or any real wire-name key) must NOT be on the
        // allowlist, so strict mode can catch Python<->Rust divergence on it.
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
    fn database_input_extraction_does_not_require_container_fields() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let attributes = PyDict::new_bound(py);
            attributes
                .set_item("headers", PyDict::new_bound(py))
                .unwrap();
            attributes.set_item("item_id", "db1").unwrap();
            let prepared = py
                .import_bound("types")
                .unwrap()
                .getattr("SimpleNamespace")
                .unwrap()
                .call((), Some(&attributes))
                .unwrap();

            let (database_id, modifiers) =
                extract_database_prepared_inputs(&prepared, "database id required")
                    .expect("database extraction must succeed");

            assert_eq!(database_id, "db1");
            assert!(modifiers.custom_headers.is_empty());
        });
    }

    #[test]
    fn account_input_extraction_only_requires_headers() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let attributes = PyDict::new_bound(py);
            let headers = PyDict::new_bound(py);
            headers.set_item("throughputBucket", 7).unwrap();
            attributes.set_item("headers", headers).unwrap();
            let prepared = py
                .import_bound("types")
                .unwrap()
                .getattr("SimpleNamespace")
                .unwrap()
                .call((), Some(&attributes))
                .unwrap();

            let modifiers = extract_account_prepared_modifiers(&prepared)
                .expect("account extraction must succeed");

            assert_eq!(
                modifiers
                    .custom_headers
                    .get(&HeaderName::from_static("x-ms-cosmos-throughput-bucket"))
                    .expect("throughput bucket must be forwarded")
                    .as_str(),
                "7"
            );
        });
    }

    #[test]
    fn legacy_option_keys_map_to_their_wire_header_names() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let headers = PyDict::new_bound(py);
            let expected = [
                ("maxItemCount", "x-ms-max-item-count"),
                (
                    "resourceTokenExpirySeconds",
                    "x-ms-documentdb-expiry-seconds",
                ),
                ("contentType", "content-type"),
                ("isQueryPlanRequest", "x-ms-cosmos-is-query-plan-request"),
                (
                    "supportedQueryFeatures",
                    "x-ms-cosmos-supported-query-features",
                ),
                ("queryVersion", "x-ms-cosmos-query-version"),
                ("continuation", "x-ms-continuation"),
                (
                    "populateQueryMetrics",
                    "x-ms-documentdb-populatequerymetrics",
                ),
                ("populateIndexMetrics", "x-ms-cosmos-populateindexmetrics"),
                ("populateQueryAdvice", "x-ms-cosmos-populatequeryadvice"),
                ("populateQuotaInfo", "x-ms-documentdb-populatequotainfo"),
            ];
            for (option_key, _) in expected {
                headers.set_item(option_key, "value").unwrap();
            }

            let modifiers = extract_op_modifiers(&headers).expect("extraction must succeed");
            for (_, wire_name) in expected {
                assert_eq!(
                    modifiers
                        .custom_headers
                        .get(&HeaderName::from(wire_name.to_string())),
                    Some(&HeaderValue::from("value".to_string())),
                    "missing mapping for {wire_name}"
                );
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
}

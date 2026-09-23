// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Extract prepared-request fields and build Rust driver operation options.
//!
//! For example, "dbs/sales/colls/orders" becomes database "sales" and container
//! "orders". Body bytes are copied from Python bytes, while settings and typed
//! partition keys are read through their dedicated helpers.

use std::collections::HashMap;
use std::time::Duration;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyBytesMethods};

use azure_core::http::headers::{HeaderName, HeaderValue};
use azure_data_cosmos_driver::{
    models::{PartitionKey, PartitionKeyValue},
    options::{
        AvailabilityStrategy, BinaryEncodingOptions, ContentResponseOnWrite,
        EndToEndOperationLatencyPolicy, ExcludedRegions, OperationOptionsBuilder,
    },
};

use serde::Deserialize;

#[cfg(test)]
use super::feed_range::FeedRangePartitionKeySource;
#[cfg(test)]
use super::legacy_partition_key::{
    legacy_feed_range_partition_key_header, legacy_partition_key_header, legacy_query_target_header,
};
use super::partition_key_input::{extract_partition_key, BindingPartitionKey};
#[cfg(test)]
use super::query::QueryTarget;

// ---------------------------------------------------------------------------
// Shared prepared-request input extraction
// ---------------------------------------------------------------------------
//
// Operation entry points use these helpers before calling their sync/async runners.

/// Binding inputs extracted from `PreparedRequest.headers` and typed `settings`
/// by `settings::extract_settings`. Activity id, session token, no-response,
/// excluded regions, timeout, and availability strategy become typed fields.
/// Other settings can generate or overwrite custom headers; operation-specific
/// code can consume those headers before passing the remainder to the driver.
pub(crate) struct RequestHeadersAndOptions {
    pub(crate) activity_header: Option<String>,
    pub(crate) session_header: Option<String>,
    // ``no_response=True`` -> Disabled, otherwise Enabled. The runner
    // applies this on writes (create / upsert / replace / patch) and ignores it on
    // reads / deletes. This option controls write responses, not read payloads.
    pub(crate) content_response_on_write: ContentResponseOnWrite,
    pub(crate) excluded_regions_value: Option<ExcludedRegions>,
    // Rust driver timeout policy, separate from the binding's remaining timeout.
    pub(crate) driver_timeout_policy: Option<EndToEndOperationLatencyPolicy>,
    // Remaining binding timeout, including metadata work and subsecond limits.
    pub(crate) operation_timeout: Option<Duration>,
    // Per-request cross-region hedging control pulled out of the
    // typed ``settings.hedging`` field. ``Disabled`` turns hedging off for
    // this request (the ``availability_strategy=False`` case); ``Hedging(..)``
    // turns it on with the caller's threshold. ``None`` means the caller did
    // not set it and the driver keeps its default.
    pub(crate) availability_strategy: Option<AvailabilityStrategy>,
    pub(crate) custom_headers: HashMap<HeaderName, HeaderValue>,
}

/// Read container-scoped fields and request settings from a prepared request.
pub(crate) fn extract_common_prepared_inputs<'py>(
    prepared: &Bound<'py, PyAny>,
) -> PyResult<(String, BindingPartitionKey, RequestHeadersAndOptions)> {
    let container_link: String = prepared.getattr("container_link")?.extract()?;
    let partition_key = extract_partition_key(prepared)?;
    let modifiers = super::settings::extract_settings(prepared)?;
    Ok((container_link, partition_key, modifiers))
}

/// Read the fields an account-level database operation needs from a
/// ``PreparedRequest``.
///
/// Database operations use an id and request settings, not a container link or
/// partition key. Read only those account-scoped inputs.
pub(crate) fn extract_database_prepared_inputs<'py>(
    prepared: &Bound<'py, PyAny>,
    error_message: &'static str,
) -> PyResult<(String, RequestHeadersAndOptions)> {
    let database_id = extract_required_item_id(prepared, error_message)?;
    let modifiers = super::settings::extract_settings(prepared)?;
    Ok((database_id, modifiers))
}

/// Read request headers and settings for an account-level operation with no resource id.
pub(crate) fn extract_account_prepared_modifiers<'py>(
    prepared: &Bound<'py, PyAny>,
) -> PyResult<RequestHeadersAndOptions> {
    super::settings::extract_settings(prepared)
}

/// Copy the prepared request body into Rust-owned bytes.
pub(crate) fn extract_body_bytes<'py>(prepared: &Bound<'py, PyAny>) -> PyResult<Vec<u8>> {
    // Read the byte buffer directly, then copy it once; do not extract each byte
    // as a separate Python sequence element.
    Ok(prepared
        .getattr("body_bytes")?
        .downcast::<PyBytes>()?
        .as_bytes()
        .to_vec())
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

/// Build OperationOptions from extracted typed settings and custom headers.
/// Callers supply ``content_response`` for applicable writes (including PATCH);
/// ``None`` leaves that option unset.
pub(super) fn build_operation_options(
    content_response: Option<ContentResponseOnWrite>,
    excluded_regions: Option<ExcludedRegions>,
    driver_timeout_policy: Option<EndToEndOperationLatencyPolicy>,
    availability_strategy: Option<AvailabilityStrategy>,
    custom_headers: HashMap<HeaderName, HeaderValue>,
) -> azure_data_cosmos_driver::options::OperationOptions {
    // Python consumes text JSON, so disable binary response negotiation.
    let mut builder = OperationOptionsBuilder::new()
        .with_binary_encoding(BinaryEncodingOptions::new().with_enabled(false));
    if let Some(cr) = content_response {
        builder = builder.with_content_response_on_write(cr);
    }
    if let Some(regions) = excluded_regions {
        builder = builder.with_excluded_regions(regions);
    }
    if let Some(policy) = driver_timeout_policy {
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

/// Parse "dbs/sales/colls/orders" into ("sales", "orders").
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
) -> PyResult<(String, RequestHeadersAndOptions)> {
    let link: String = prepared.getattr("container_link")?.extract()?;
    let database_id = parse_database_link(&link)?;
    let modifiers = super::settings::extract_settings(prepared)?;
    Ok((database_id, modifiers))
}

/// Read database and container names plus request settings for a container read.
pub(crate) fn extract_container_point_prepared_inputs<'py>(
    prepared: &Bound<'py, PyAny>,
) -> PyResult<(String, String, RequestHeadersAndOptions)> {
    let link: String = prepared.getattr("container_link")?.extract()?;
    let (database_id, container_id) = parse_container_link(&link)?;
    let modifiers = super::settings::extract_settings(prepared)?;
    Ok((database_id, container_id, modifiers))
}

/// Convert a single JSON-array element into a `PartitionKeyValue`.
pub(super) fn json_value_to_pk_component(value: serde_json::Value) -> PyResult<PartitionKeyValue> {
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
        // on this item" (Python's `_Undefined`). Map it to the
        // driver's dedicated ``UNDEFINED`` constant.
        serde_json::Value::Object(obj) if obj.is_empty() => Ok(PartitionKeyValue::UNDEFINED),
        // Anything else is not a valid partition-key component on the wire.
        other => Err(PyValueError::new_err(format!(
            "unsupported partition key value: {other}"
        ))),
    }
}

/// Mirror Python's extraction rules against the exact bytes sent to the driver.
pub(super) fn extract_partition_key_from_body(
    definition: &azure_data_cosmos_driver::models::PartitionKeyDefinition,
    body: &[u8],
) -> PyResult<PartitionKey> {
    use azure_data_cosmos_driver::models::PartitionKeyKind;
    use serde_json::Value;

    let document: Value = serde_json::from_slice(body)
        .map_err(|error| PyValueError::new_err(format!("Invalid item JSON: {error}")))?;
    if !document.is_object() {
        return Err(PyValueError::new_err("An item body must be a JSON object"));
    }
    if definition.paths().is_empty() {
        return Err(PyValueError::new_err(
            "Container metadata requires partition-key paths",
        ));
    }
    let retrieve = |tokens: Vec<&str>| -> Option<Value> {
        let mut value = &document;
        for token in tokens {
            value = value.as_object()?.get(token)?;
        }
        if value.is_object() {
            None
        } else {
            Some(value.clone())
        }
    };
    let values = match definition.kind() {
        PartitionKeyKind::MultiHash => definition
            .paths()
            .iter()
            .map(|path| Ok(retrieve(partition_key_path_tokens(path)?).unwrap_or(Value::Null)))
            .collect::<PyResult<Vec<Value>>>()?,
        PartitionKeyKind::Hash | PartitionKeyKind::Range => {
            let mut tokens = Vec::new();
            for path in definition.paths() {
                tokens.extend(partition_key_path_tokens(path)?);
            }
            match retrieve(tokens) {
                // Python treats a nonempty sequence leaf as multiple components.
                Some(Value::Array(values)) if !values.is_empty() => values,
                Some(value) => vec![value],
                // The driver does not retain systemKey; preserve Python's
                // existing unknown/false fallback rather than inventing it.
                None => vec![Value::Object(Default::default())],
            }
        }
        _ => return Err(PyValueError::new_err("Unsupported partition-key kind")),
    };
    if values.len() > 3 {
        return Err(PyValueError::new_err(
            "Cosmos partition keys can have at most 3 levels",
        ));
    }
    values
        .into_iter()
        .map(json_value_to_pk_component)
        .collect::<PyResult<Vec<_>>>()
        .map(PartitionKey::from)
}

fn partition_key_path_tokens(path: &str) -> PyResult<Vec<&str>> {
    let mut tokens = Vec::new();
    let bytes = path.as_bytes();
    let mut index = 0;
    while index < bytes.len() {
        if bytes[index] != b'/' {
            return Err(PyValueError::new_err(format!(
                "Invalid path character at index {index}"
            )));
        }
        index += 1;
        if index == bytes.len() {
            break;
        }
        if matches!(bytes[index], b'\'' | b'"') {
            let quote = bytes[index];
            let start = index + 1;
            index = start;
            let mut escaped = false;
            while index < bytes.len() {
                if bytes[index] == quote && !escaped {
                    break;
                }
                escaped = bytes[index] == b'\\' && !escaped;
                index += 1;
            }
            if index == bytes.len() {
                return Err(PyValueError::new_err(
                    "Unterminated quoted partition-key path",
                ));
            }
            tokens.push(&path[start..index]);
            index += 1;
        } else {
            let start = index;
            index = path[index..]
                .find('/')
                .map_or(path.len(), |offset| index + offset);
            tokens.push(
                path[start..index].trim_matches(|c: char| {
                    c.is_whitespace() || ('\u{1c}'..='\u{1f}').contains(&c)
                }),
            );
        }
    }
    Ok(tokens)
}

/// A partial view of an item body that deserializes only the `id` field.
///
/// Other fields are not retained, but the deserializer still scans the JSON.
/// The `id` is kept as a `Value` so a
/// present-but-non-string value still gives the "no string id" error rather
/// than a deserialization failure.
#[derive(Deserialize)]
struct BodyId {
    id: Option<serde_json::Value>,
}

/// Read the item `id` out of a JSON body.
///
/// Reject invalid JSON or a missing/non-string id rather than inventing one.
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

/// Prefer a non-empty `PreparedRequest.item_id` for create/upsert, avoiding another
/// body parse. Parse the body's id only when the attribute is `None` or empty;
/// a missing or wrongly typed attribute raises instead of taking that fallback.
/// The binding does not compare a supplied id with the body's id, so request
/// preparation must keep them consistent.
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
        json_value_to_pk_component, legacy_feed_range_partition_key_header,
        legacy_partition_key_header, legacy_query_target_header, parse_container_link,
        parse_read_feed_ranges_force_refresh, FeedRangePartitionKeySource, QueryTarget,
    };
    use azure_core::http::headers::HeaderName;
    use pyo3::prelude::*;
    use pyo3::types::PyDict;

    #[test]
    fn body_snapshot_is_copied_as_bytes_not_iterated_as_a_sequence() {
        pyo3::prepare_freethreaded_python();
        let owned = Python::with_gil(|py| {
            let module = PyModule::from_code_bound(
                py,
                "class Body(bytes):\n    def __iter__(self):\n        raise AssertionError('must copy bytes directly')\n",
                "body_snapshot_test.py",
                "body_snapshot_test",
            ).unwrap();
            let body = module.getattr("Body").unwrap()
                .call1((pyo3::types::PyBytes::new_bound(py, b"\0\xff{}"),)).unwrap();
            let request = py.import_bound("types").unwrap()
                .getattr("SimpleNamespace").unwrap().call0().unwrap();
            request.setattr("body_bytes", body).unwrap();
            super::extract_body_bytes(&request).unwrap()
        });
        assert_eq!(owned, b"\0\xff{}");
    }

    #[test]
    fn body_snapshot_rejects_mutable_sequences() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let request = py.import_bound("types").unwrap()
                .getattr("SimpleNamespace").unwrap().call0().unwrap();
            for value in [
                vec![1u8, 2u8].into_py(py),
                pyo3::types::PyByteArray::new_bound(py, b"{}").into_any().unbind(),
            ] {
                request.setattr("body_bytes", value).unwrap();
                assert!(super::extract_body_bytes(&request).unwrap_err()
                    .is_instance_of::<pyo3::exceptions::PyTypeError>(py));
            }
            request.setattr("body_bytes", pyo3::types::PyBytes::new_bound(py, b"")).unwrap();
            assert!(super::extract_body_bytes(&request).unwrap().is_empty());
        });
    }

    #[test]
    fn operation_options_preserve_the_python_text_json_contract() {
        let options = super::build_operation_options(None, None, None, None, Default::default());
        assert!(!options.binary_encoding.unwrap().enabled);
    }

    // Parser/conversion tests include pure Rust helpers and Python-backed
    // protocol extraction. Legacy header cases exercise a test-only oracle,
    // not the production typed-partition-key protocol.

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
        // Check id extraction with unrelated fields before and after it.
        // Those values are not retained, but their JSON is still scanned.
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

    #[test]
    fn body_key_extraction_preserves_python_shapes_and_path_rules() {
        pyo3::prepare_freethreaded_python();
        for (kind, paths, body, header) in [
            ("Hash", vec!["/pk"], r#"{"pk":"a"}"#, r#"["a"]"#),
            ("Hash", vec!["/pk"], r#"{"pk":null}"#, "[null]"),
            ("Hash", vec!["/pk"], r#"{"pk":true}"#, "[true]"),
            (
                "Hash",
                vec!["/pk"],
                r#"{"pk":9007199254740993}"#,
                "[9007199254740993]",
            ),
            ("Hash", vec!["/pk"], "{}", "[{}]"),
            ("Hash", vec!["/pk"], r#"{"pk":{"x":1}}"#, "[{}]"),
            ("Hash", vec!["/a/b"], r#"{"a":{"b":"v"}}"#, r#"["v"]"#),
            ("Hash", vec!["/a/b"], r#"{"a":1}"#, "[{}]"),
            ("Hash", vec!["/'a/b'"], r#"{"a/b":"v"}"#, r#"["v"]"#),
            ("Hash", vec![r#"/"a\"b""#], r#"{"a\\\"b":"v"}"#, r#"["v"]"#),
            ("Hash", vec![r#"/"a\\""#], r#"{"a\\\\":"v"}"#, r#"["v"]"#),
            ("Hash", vec!["/ pk /"], r#"{"pk":2}"#, "[2]"),
            ("Hash", vec!["//pk"], r#"{"":{"pk":2}}"#, "[2]"),
            ("Hash", vec!["/a", "/b"], r#"{"a":{"b":"v"}}"#, r#"["v"]"#),
            ("Hash", vec!["/pk"], r#"{"pk":["a",null]}"#, r#"["a",null]"#),
            ("Hash", vec!["/pk"], r#"{"pk":"\u4e2d"}"#, r#"["\u4e2d"]"#),
            (
                "Hash",
                vec!["/pk"],
                r#"{"pk":"\ud83d\ude00"}"#,
                r#"["\ud83d\ude00"]"#,
            ),
            ("Range", vec!["/pk"], r#"{"pk":2.5}"#, "[2.5]"),
            ("MultiHash", vec!["/pk"], r#"{"pk":"a"}"#, r#"["a"]"#),
            (
                "MultiHash",
                vec!["/tenant", "/id"],
                r#"{"tenant":"t","id":"minted"}"#,
                r#"["t","minted"]"#,
            ),
            (
                "MultiHash",
                vec!["/a", "/b"],
                r#"{"a":"x"}"#,
                r#"["x",null]"#,
            ),
            (
                "MultiHash",
                vec!["/a", "/b"],
                r#"{"a":{},"b":null}"#,
                "[null,null]",
            ),
        ] {
            let definition = serde_json::from_value(serde_json::json!({
                "paths": paths, "kind": kind, "version": 2,
            }))
            .unwrap();
            assert_eq!(
                super::extract_partition_key_from_body(&definition, body.as_bytes()).unwrap(),
                legacy_partition_key_header(header).unwrap(),
                "{kind}: {body}",
            );
        }
    }

    #[test]
    fn body_key_extraction_rejects_invalid_input_instead_of_guessing() {
        pyo3::prepare_freethreaded_python();
        for (kind, path, body) in [
            ("Hash", "/pk", "not JSON"),
            ("Hash", "/pk", "[]"),
            ("Hash", "/pk", r#"{"pk":[]}"#),
            ("Hash", "/pk", r#"{"pk":[1,2,3,4]}"#),
            ("Hash", "/pk", r#"{"pk":[{"x":1}]}"#),
            ("Hash", "/'bad", "{}"),
            ("Hash", "/'pk'x", "{}"),
            ("Hash", "pk", "{}"),
            ("MultiHash", "/pk", r#"{"pk":["x"]}"#),
        ] {
            let definition = serde_json::from_value(serde_json::json!({
                "paths": [path], "kind": kind, "version": 2,
            }))
            .unwrap();
            assert!(super::extract_partition_key_from_body(&definition, body.as_bytes()).is_err());
        }
    }

    #[test]
    fn body_key_extraction_reports_unsupported_unpaired_surrogates() {
        pyo3::prepare_freethreaded_python();
        let definition = serde_json::from_value(serde_json::json!({
            "paths": ["/pk"], "kind": "Hash", "version": 2,
        }))
        .unwrap();
        // Python can encode these JSON escapes, but serde_json::Value
        // cannot represent them, even in a property unrelated to the key.
        for body in [
            br#"{"pk":"p","value":"\ud800"}"#.as_slice(),
            br#"{"pk":"p","value":"\udfff"}"#.as_slice(),
        ] {
            let error = super::extract_partition_key_from_body(&definition, body).unwrap_err();
            assert!(error.to_string().contains("Invalid item JSON"), "{error}");
        }
    }

    // ---- legacy_partition_key_header -------------------------------------------

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
                legacy_partition_key_header(header).is_ok(),
                "should parse: {header}"
            );
        }
    }

    #[test]
    fn pk_header_rejects_empty_overflow_and_garbage() {
        // The legacy point-operation header oracle rejects an empty array.
        assert!(legacy_partition_key_header("[]").is_err());
        // Cosmos allows at most 3 levels.
        assert!(legacy_partition_key_header(r#"["a","b","c","d"]"#).is_err());
        // Not a JSON array.
        assert!(legacy_partition_key_header("nonsense").is_err());
    }

    // ---- legacy_query_target_header ------------------------------------------

    #[test]
    fn query_target_header_accepts_partition_and_cross_partition_shapes() {
        assert!(matches!(
            legacy_query_target_header("[]").unwrap(),
            QueryTarget::CrossPartition
        ));
        assert!(matches!(
            legacy_query_target_header(r#"["customerA"]"#).unwrap(),
            QueryTarget::Partition(_)
        ));
        assert!(matches!(
            legacy_query_target_header(r#"[null]"#).unwrap(),
            QueryTarget::Partition(_)
        ));
    }

    #[test]
    fn query_target_header_rejects_overflow_and_garbage() {
        assert!(legacy_query_target_header(r#"["a","b","c","d"]"#).is_err());
        assert!(legacy_query_target_header("nonsense").is_err());
    }

    // ---- legacy_feed_range_partition_key_header -------------------------------

    #[test]
    fn feed_range_partition_key_header_accepts_empty_and_partition_shapes() {
        let empty = legacy_feed_range_partition_key_header("[]").unwrap();
        assert_eq!(empty.partition_key.len(), 0);
        assert_eq!(empty.source, FeedRangePartitionKeySource::EmptySentinel);
        let explicit_empty_sequence = legacy_feed_range_partition_key_header("[[]]").unwrap();
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
            let parsed = legacy_feed_range_partition_key_header(header).unwrap();
            assert_eq!(parsed.source, FeedRangePartitionKeySource::Standard);
            assert!(
                parsed.partition_key.len() >= 1,
                "standard header must produce partition-key components"
            );
        }
    }

    #[test]
    fn feed_range_partition_key_header_rejects_overflow_and_garbage() {
        assert!(legacy_feed_range_partition_key_header(r#"["a","b","c","d"]"#).is_err());
        assert!(legacy_feed_range_partition_key_header("nonsense").is_err());
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
        // This integer exceeds exact f64 integer precision. The assertion checks
        // that conversion succeeds, not its exact rounded value, a partition
        // hash, or agreement with service-side routing.
        let big: serde_json::Value = serde_json::from_str("9007199254740993").unwrap(); // 2^53 + 1
        assert!(big.is_i64(), "fixture must be an integer, not a float");
        assert!(
            json_value_to_pk_component(big).is_ok(),
            "large integer PK must map to a finite f64 component without error"
        );
    }

    #[test]
    fn database_input_extraction_does_not_require_container_fields() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let attributes = PyDict::new_bound(py);
            attributes.set_item("protocol_version", 3).unwrap();
            attributes
                .set_item("settings", crate::wire::settings::test_settings(py))
                .unwrap();
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
    fn account_input_extraction_requires_headers_and_options() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let attributes = PyDict::new_bound(py);
            attributes.set_item("protocol_version", 3).unwrap();
            attributes
                .set_item("settings", crate::wire::settings::test_settings(py))
                .unwrap();
            let headers = PyDict::new_bound(py);
            headers
                .set_item("x-ms-cosmos-throughput-bucket", "7")
                .unwrap();
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
}

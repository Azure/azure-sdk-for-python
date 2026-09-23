// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Binding calls for individual items, such as "order-42" in sales/orders.
//!
//! Each function checks PreparedRequest.op and extracts typed inputs before
//! asking the shared item helpers to execute through the Rust driver. Async
//! variants return an awaitable; validation can still fail during the call.

use super::*;
use crate::wire::ItemTarget;
use azure_core::http::headers::HeaderName;
use azure_data_cosmos_driver::models::{ItemReference, Precondition};
use pyo3::exceptions::{PyNotImplementedError, PyValueError};

fn replacement_target(prepared: &Bound<'_, PyAny>, item_id: String) -> PyResult<ItemTarget> {
    match prepared
        .getattr("item_self_link")?
        .extract::<Option<String>>()?
    {
        Some(link) => ItemTarget::from_self_link(&link),
        None => Ok(item_id.into()),
    }
}

fn patch_precondition(
    modifiers: &mut RequestHeadersAndOptions,
    body: &[u8],
) -> PyResult<Option<Precondition>> {
    if modifiers
        .custom_headers
        .contains_key(&HeaderName::from_static("if-none-match"))
    {
        return Err(PyNotImplementedError::new_err(
            "The Python Rust binding does not support If-None-Match for patch_item.",
        ));
    }
    if serde_json::from_slice::<serde_json::Value>(body)
        .ok()
        .is_some_and(|value| value.get("condition").is_some())
    {
        return Err(PyNotImplementedError::new_err(
            "The Python Rust binding does not support filtered patches.",
        ));
    }
    modifiers
        .custom_headers
        .remove(&HeaderName::from_static("if-match"))
        .map(|value| {
            if value.as_str().trim().is_empty() {
                return Err(PyValueError::new_err(
                    "patch_item If-Match must be a non-empty ETag string.",
                ));
            }
            Ok(Precondition::if_match(value.as_str().to_owned()))
        })
        .transpose()
}

fn patch_operation(
    item: ItemReference,
    body: Vec<u8>,
    precondition: Option<Precondition>,
) -> CosmosOperation {
    let operation = CosmosOperation::patch_item(item).with_body(body);
    match precondition {
        Some(precondition) => operation.with_precondition(precondition),
        None => operation,
    }
}

/// Insert a new item, rejecting an existing item with the same id and partition key.
///
/// The Python wrapper normally supplies PreparedRequest.item_id. If that field
/// is None or empty, read the id from body_bytes. Missing or wrongly typed
/// attributes raise instead; this does not select the legacy execution path.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn create_item<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "create_item")?;
    let (container_link, partition_key, mut modifiers, item_id, body_bytes) =
        extract_create_body_inputs(prepared)?;
    modifiers.operation_timeout = crate::wire::deadline::parse_remaining_timeout(timeout_seconds)?;

    execute_item_operation_sync(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        item_id.into(),
        body_bytes,
        "create_item",
        true,
        |item_ref, body| CosmosOperation::create_item(item_ref).with_body(body),
    )
}

/// Create an item or replace the existing item with the same partition key and id.
///
/// This selects the driver's upsert operation rather than implementing an
/// existence check in the binding. Prepared `If-Match` / `If-None-Match`
/// headers remain in `custom_headers`; their enforcement is not done here.
#[pyfunction]
pub(crate) fn upsert_item<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "upsert_item")?;
    let (container_link, partition_key, modifiers, item_id, body_bytes) =
        extract_create_body_inputs(prepared)?;

    execute_item_operation_sync(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        item_id.into(),
        body_bytes,
        "upsert_item",
        true,
        |item_ref, body| CosmosOperation::upsert_item(item_ref).with_body(body),
    )
}

/// Replace the target identified by the prepared request, not by the body.
/// Use item_self_link when supplied for a dictionary target; otherwise use
/// item_id. Preserving a resource-id address prevents replacing a different
/// item that was later created with the same name.
///
/// An existing item is overwritten (HTTP 200). Returns the saved item unless
/// `no_response=True`. `If-Match` / `If-None-Match` flow through
/// `custom_headers`.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn replace_item<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "replace_item")?;
    // A dictionary's resource address must not become a name-based replacement
    // of a different item created later with the same item id.
    let (container_link, partition_key, mut modifiers, item_id, body_bytes) =
        extract_item_body_inputs(prepared, REPLACE_ITEM_ID_REQUIRED)?;
    modifiers.operation_timeout = crate::wire::deadline::parse_remaining_timeout(timeout_seconds)?;
    let target = replacement_target(prepared, item_id)?;

    execute_item_operation_sync(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        target,
        body_bytes,
        "replace_item",
        true,
        |item_ref, body| CosmosOperation::replace_item(item_ref).with_body(body),
    )
}

/// Delete the item named by PreparedRequest.item_id with an explicit partition key.
/// Send no body and leave the write-content-response option unset.
///
/// On success the driver returns HTTP 204 with an empty body.
#[pyfunction]
pub(crate) fn delete_item<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "delete_item")?;
    let (container_link, partition_key, modifiers, item_id) = extract_item_inputs(
        prepared,
        DELETE_ITEM_ID_REQUIRED,
        DELETE_ITEM_PARTITION_KEY_REQUIRED,
    )?;

    execute_item_operation_sync(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        item_id.into(),
        Vec::new(),
        "delete_item",
        false,
        |item_ref, _| CosmosOperation::delete_item(item_ref),
    )
}

/// Read the item named by PreparedRequest.item_id with an explicit partition key.
/// Send no body; return the Rust driver's response through the binding tuple.
///
/// On success returns HTTP 200 with the item JSON. Conditional reads
/// (`If-None-Match`, driven by Python's `etag` + `MatchConditions.IfModified`)
/// come back as HTTP 304 with an empty body when the customer app's cached etag
/// still matches the service backend version; the Python parser treats 304 as a
/// non-error and returns an empty `CosmosDict`.
/// `x-ms-dedicatedgateway-max-age`, driven by
/// `max_integrated_cache_staleness_in_ms`, is forwarded through
/// `custom_headers` like any other per-request header.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn read_item<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "read_item")?;
    let (container_link, partition_key, mut modifiers, item_id) = extract_item_inputs(
        prepared,
        READ_ITEM_ID_REQUIRED,
        READ_ITEM_PARTITION_KEY_REQUIRED,
    )?;
    modifiers.operation_timeout = crate::wire::deadline::parse_remaining_timeout(timeout_seconds)?;

    execute_item_operation_sync(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        item_id.into(),
        Vec::new(),
        "read_item",
        false,
        |item_ref, _| CosmosOperation::read_item(item_ref),
    )
}

/// Patch using the driver's Auto strategy, with a typed caller If-Match guard.
/// Remove the guard from custom headers so it cannot leak to an internal read
/// or override the fresh ETag protecting an internal replacement.
///
/// The body contains `PatchInstructions` (`{"operations": [...]}`) rather
/// than an item, and the URL id comes from `PreparedRequest.item_id`. The driver
/// chooses the execution plan for Auto; this entry point does not guarantee a
/// particular number of service requests. `patch_precondition` accepts If-Match
/// as a typed precondition and rejects If-None-Match and a body `condition`.
/// These binding checks raise errors; they do not repeat the operation through legacy.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn patch_item<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "patch_item")?;
    let (container_link, partition_key, mut modifiers, item_id, body_bytes) =
        extract_item_body_inputs(prepared, PATCH_ITEM_ID_REQUIRED)?;
    modifiers.operation_timeout = crate::wire::deadline::parse_remaining_timeout(timeout_seconds)?;
    let precondition = patch_precondition(&mut modifiers, &body_bytes)?;
    if matches!(partition_key, BindingPartitionKey::Extract) {
        return Err(PyValueError::new_err(
            "patch_item requires an explicit partition key",
        ));
    }

    execute_item_operation_sync(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        item_id.into(),
        body_bytes,
        "patch_item",
        true,
        move |item_ref, body| patch_operation(item_ref, body, precondition),
    )
}

/// Async twin of `create_item`: identical inputs and driver work, returns a
/// Python awaitable instead of a ready tuple.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn create_item_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "create_item")?;
    let (container_link, partition_key, mut modifiers, item_id, body_bytes) =
        extract_create_body_inputs(prepared)?;
    modifiers.operation_timeout = crate::wire::deadline::parse_remaining_timeout(timeout_seconds)?;

    execute_item_operation_async(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        item_id.into(),
        body_bytes,
        "create_item",
        true,
        |item_ref, body| CosmosOperation::create_item(item_ref).with_body(body),
    )
}

/// Async twin of `upsert_item`: identical inputs and driver work, returns a
/// Python awaitable instead of a ready tuple.
#[pyfunction]
pub(crate) fn upsert_item_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "upsert_item")?;
    let (container_link, partition_key, modifiers, item_id, body_bytes) =
        extract_create_body_inputs(prepared)?;

    execute_item_operation_async(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        item_id.into(),
        body_bytes,
        "upsert_item",
        true,
        |item_ref, body| CosmosOperation::upsert_item(item_ref).with_body(body),
    )
}

/// Async twin of `replace_item`: identical inputs and driver work (URL id from
/// the request, not the body), returns a Python awaitable instead of a tuple.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn replace_item_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "replace_item")?;
    let (container_link, partition_key, mut modifiers, item_id, body_bytes) =
        extract_item_body_inputs(prepared, REPLACE_ITEM_ID_REQUIRED)?;
    modifiers.operation_timeout = crate::wire::deadline::parse_remaining_timeout(timeout_seconds)?;
    let target = replacement_target(prepared, item_id)?;

    execute_item_operation_async(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        target,
        body_bytes,
        "replace_item",
        true,
        |item_ref, body| CosmosOperation::replace_item(item_ref).with_body(body),
    )
}

/// Async twin of `delete_item`: identical inputs and driver work, returns a
/// Python awaitable instead of a ready tuple.
#[pyfunction]
pub(crate) fn delete_item_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "delete_item")?;
    let (container_link, partition_key, modifiers, item_id) = extract_item_inputs(
        prepared,
        DELETE_ITEM_ID_REQUIRED,
        DELETE_ITEM_PARTITION_KEY_REQUIRED,
    )?;

    execute_item_operation_async(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        item_id.into(),
        Vec::new(),
        "delete_item",
        false,
        |item_ref, _| CosmosOperation::delete_item(item_ref),
    )
}

/// Async twin of `read_item`: identical inputs and driver work, returns a
/// Python awaitable instead of a ready tuple.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn read_item_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "read_item")?;
    let (container_link, partition_key, mut modifiers, item_id) = extract_item_inputs(
        prepared,
        READ_ITEM_ID_REQUIRED,
        READ_ITEM_PARTITION_KEY_REQUIRED,
    )?;
    modifiers.operation_timeout = crate::wire::deadline::parse_remaining_timeout(timeout_seconds)?;

    execute_item_operation_async(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        item_id.into(),
        Vec::new(),
        "read_item",
        false,
        |item_ref, _| CosmosOperation::read_item(item_ref),
    )
}

/// Async twin of `patch_item`: identical inputs and driver work (body is the
/// PatchInstructions body, target id from the request), returns a Python
/// awaitable instead of a ready tuple.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn patch_item_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "patch_item")?;
    let (container_link, partition_key, mut modifiers, item_id, body_bytes) =
        extract_item_body_inputs(prepared, PATCH_ITEM_ID_REQUIRED)?;
    modifiers.operation_timeout = crate::wire::deadline::parse_remaining_timeout(timeout_seconds)?;
    let precondition = patch_precondition(&mut modifiers, &body_bytes)?;
    if matches!(partition_key, BindingPartitionKey::Extract) {
        return Err(PyValueError::new_err(
            "patch_item requires an explicit partition key",
        ));
    }

    execute_item_operation_async(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        item_id.into(),
        body_bytes,
        "patch_item",
        true,
        move |item_ref, body| patch_operation(item_ref, body, precondition),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use azure_core::http::headers::HeaderValue;
    use azure_data_cosmos_driver::{
        in_memory_emulator::{
            ContainerConfig, InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion,
        },
        models::{AccountReference, PartitionKey, PartitionKeyDefinition},
        options::{BinaryEncodingOptions, DriverOptions, OperationOptionsBuilder},
    };
    use pyo3::types::{PyBytes, PyDict};
    use std::{borrow::Cow, sync::Arc};

    fn modifiers(py: Python<'_>) -> RequestHeadersAndOptions {
        let prepared = py
            .import_bound("types")
            .unwrap()
            .getattr("SimpleNamespace")
            .unwrap()
            .call0()
            .unwrap();
        prepared
            .setattr("container_link", "dbs/db/colls/c")
            .unwrap();
        prepared
            .setattr(
                "partition_key",
                crate::wire::partition_key_input::test_partition_key(py, Some("[\"pk\"]")),
            )
            .unwrap();
        prepared.setattr("headers", PyDict::new_bound(py)).unwrap();
        prepared.setattr("protocol_version", 3).unwrap();
        prepared
            .setattr("settings", crate::wire::settings::test_settings(py))
            .unwrap();
        extract_common_prepared_inputs(&prepared).unwrap().2
    }

    #[test]
    fn patch_guard_is_typed_and_removed_from_custom_headers() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            for etag in ["\"v1\"", "*"] {
                let mut modifiers = modifiers(py);
                modifiers
                    .custom_headers
                    .insert(HeaderName::from_static("if-match"), HeaderValue::from(etag));
                let guard = patch_precondition(&mut modifiers, br#"{"operations":[]}"#).unwrap();
                assert_eq!(guard, Some(Precondition::if_match(etag)));
                assert!(!modifiers
                    .custom_headers
                    .contains_key(&HeaderName::from_static("if-match")));
            }
        });
    }

    #[test]
    fn binding_rejects_unsupported_guards_before_driver_lookup() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let prepared = py
                .import_bound("types")
                .unwrap()
                .getattr("SimpleNamespace")
                .unwrap()
                .call0()
                .unwrap();
            prepared
                .setattr("container_link", "dbs/db/colls/c")
                .unwrap();
            prepared
                .setattr(
                    "partition_key",
                    crate::wire::partition_key_input::test_partition_key(py, Some("[\"pk\"]")),
                )
                .unwrap();
            prepared.setattr("item_id", "item").unwrap();
            prepared.setattr("op", "patch_item").unwrap();
            prepared.setattr("protocol_version", 3).unwrap();
            prepared
                .setattr("settings", crate::wire::settings::test_settings(py))
                .unwrap();
            for filtered in [false, true] {
                let headers = PyDict::new_bound(py);
                if !filtered {
                    headers.set_item("IF-NONE-MATCH", "*").unwrap();
                }
                prepared.setattr("headers", headers).unwrap();
                let body: &[u8] = if filtered {
                    br#"{"condition":"FROM c","operations":[{"op":"set","path":"/n","value":2}]}"#
                } else {
                    br#"{"operations":[{"op":"set","path":"/n","value":2}]}"#
                };
                prepared
                    .setattr("body_bytes", PyBytes::new_bound(py, body))
                    .unwrap();
                assert!(patch_item(py, "unused-handle", &prepared, None)
                    .unwrap_err()
                    .is_instance_of::<PyNotImplementedError>(py));
                assert!(patch_item_async(py, "unused-handle", &prepared, None)
                    .unwrap_err()
                    .is_instance_of::<PyNotImplementedError>(py));
            }
        });
    }

    #[tokio::test]
    async fn guarded_auto_patch_handles_server_and_client_side_mutations() {
        pyo3::prepare_freethreaded_python();
        let url = azure_core::http::Url::parse("https://patch.emulator.local").unwrap();
        let config =
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(config));
        emulator.store().create_database("db");
        emulator.store().create_container_with_config(
            "db",
            "c",
            PartitionKeyDefinition::new(vec![Cow::Borrowed("/pk")]),
            ContainerConfig::new()
                .with_partition_count(1)
                .build()
                .unwrap(),
        );
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let options = OperationOptionsBuilder::new()
            .with_binary_encoding(BinaryEncodingOptions::new().with_enabled(false))
            .build();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5"))
                    .with_operation_options(options)
                    .build(),
            )
            .await
            .unwrap();
        let container = driver
            .resolve_container("db", "c", Default::default())
            .await
            .unwrap();
        let item = ItemReference::from_name(&container, PartitionKey::from("pk"), "item");
        driver
            .execute_singleton_operation(
                CosmosOperation::create_item(item.clone())
                    .with_body(br#"{"id":"item","pk":"pk","n":0}"#.to_vec()),
                Default::default(),
            )
            .await
            .unwrap();
        for op in ["set", "incr"] {
            let read = driver
                .execute_singleton_operation(
                    CosmosOperation::read_item(item.clone()),
                    Default::default(),
                )
                .await
                .unwrap();
            let etag = read
                .headers()
                .to_raw_headers()
                .iter()
                .find(|(name, _)| name.as_str() == "etag")
                .map(|(_, value)| value.as_str().to_owned())
                .unwrap();
            let body = serde_json::to_vec(&serde_json::json!({
                "operations": [{"op": op, "path": "/n", "value": 2}]
            }))
            .unwrap();
            let guard = Python::with_gil(|py| {
                let mut modifiers = modifiers(py);
                modifiers.custom_headers.insert(
                    HeaderName::from_static("if-match"),
                    HeaderValue::from(etag.clone()),
                );
                patch_precondition(&mut modifiers, &body).unwrap()
            });
            let success = driver
                .execute_singleton_operation(
                    patch_operation(item.clone(), body.clone(), guard.clone()),
                    Default::default(),
                )
                .await
                .unwrap();
            assert_eq!(u16::from(success.status().status_code()), 200);
            let rejected = driver
                .execute_singleton_operation(
                    patch_operation(item.clone(), body, guard),
                    Default::default(),
                )
                .await
                .unwrap_err();
            assert_eq!(u16::from(rejected.status().status_code()), 412);
        }
        let final_read = driver
            .execute_singleton_operation(CosmosOperation::read_item(item), Default::default())
            .await
            .unwrap();
        let azure_data_cosmos_driver::models::ResponseBody::Bytes(bytes) = final_read.body() else {
            panic!("expected JSON point response");
        };
        let body: serde_json::Value = serde_json::from_slice(bytes).unwrap();
        assert_eq!(
            body["n"], 4,
            "rejected guards must never reapply a mutation"
        );
    }
}

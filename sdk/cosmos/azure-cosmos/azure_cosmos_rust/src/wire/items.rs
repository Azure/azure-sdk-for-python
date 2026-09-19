// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::partition_key::PartitionKeyInput;
use std::sync::atomic::Ordering;
use std::sync::Arc;

use pyo3::exceptions::{PyRuntimeError, PyTimeoutError};
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{
        ActivityId, CosmosOperation, CosmosResponse, ItemReference, PartitionKey, SessionToken,
    },
};

use super::container_metadata::metadata_error;
use super::deadline::with_item_timeout;
use super::diagnostics::BINDING_OP_COUNT;
use super::request::{build_operation_options, parse_container_link, RequestHeadersAndOptions};
use super::response::tuple_from_result;
use super::{lookup_driver, AbortOnDrop};
use crate::runtime::require_runtime_context;

/// Sync runner shared by all six point operations (`documents/items.rs` sync entries).
/// Steps: increment the binding-invocation counter, look up the rust driver by handle,
/// parse the container link and any explicit key, then -- with the GIL released --
/// block the calling thread on the shared Tokio runtime until the driver resolves
/// the container, extracts an omitted item key, builds and runs the operation,
/// and returns. Turn the driver's
/// `CosmosResponse` (or a `CosmosError` that still carries a wire response) into
/// the `BackendResponse` tuple the Python parser reads. Only three things vary per
/// op, so each entry point passes them in: the item id, whether `no_response`
/// applies (writes only), and a closure that builds the operation from the
/// resolved `ItemReference`. The async sibling below spawns this same future
/// instead of blocking, so both paths run identical driver work.
pub(crate) fn execute_item_operation_sync<'py>(
    py: Python<'py>,
    driver_handle: &str,
    container_link: &str,
    partition_key_input: PartitionKeyInput,
    modifiers: RequestHeadersAndOptions,
    item_id: String,
    body_bytes: Vec<u8>,
    op_name: &str,
    honor_content_response: bool,
    build_op: impl FnOnce(ItemReference, Vec<u8>) -> CosmosOperation + Send,
) -> PyResult<Bound<'py, PyTuple>> {
    // Count runner entry, before driver lookup or execution can fail.
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let partition_key = partition_key_input.into_item_key()?;
    let runtime_ctx = require_runtime_context(op_name)?;

    // Sync path: block the calling thread on the shared runtime until the driver
    // finishes. (The async sibling below spawns the very same future instead, so
    // both paths run identical driver work.)
    let timeout = modifiers.item_timeout;
    let response_result = py.allow_threads(|| {
        runtime_ctx.tokio_rt.block_on(with_item_timeout(
            timeout,
            execute_item_on_driver(
                driver,
                database_name,
                container_name,
                partition_key,
                item_id,
                body_bytes,
                modifiers,
                honor_content_response,
                build_op,
            ),
        ))
    })??;

    tuple_from_result(py, response_result)
}

/// Async sibling of `execute_item_operation_sync`, using the same driver future.
/// Validate inputs under the GIL, spawn driver work on the shared Tokio runtime,
/// and bridge its result to a Python awaitable. Result conversion reacquires the
/// GIL; credential callbacks can also re-enter Python during driver execution.
///
/// The Rust bridge future owns an `AbortOnDrop` guard so dropping that future
/// requests cancellation instead of merely detaching the task. This is not a
/// guarantee of immediate cleanup or cancellation of work already at the service.
pub(crate) fn execute_item_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    container_link: &str,
    partition_key_input: PartitionKeyInput,
    modifiers: RequestHeadersAndOptions,
    item_id: String,
    body_bytes: Vec<u8>,
    op_name: &str,
    honor_content_response: bool,
    build_op: impl FnOnce(ItemReference, Vec<u8>) -> CosmosOperation + Send + 'static,
) -> PyResult<Bound<'py, PyAny>> {
    // Count runner entry, not completion or a network attempt.
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    // Synchronous extraction (GIL held) -- identical to the sync path. Errors
    // here appear when the coroutine is created, before it is awaited.
    let driver = lookup_driver(driver_handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let partition_key = partition_key_input.into_item_key()?;
    let runtime_ctx = require_runtime_context(op_name)?;

    // Spawn the driver work on the shared runtime; `join` is a cheap handle the
    // bridge below awaits without holding the GIL for the wait.
    let timeout = modifiers.item_timeout;
    let join = runtime_ctx.tokio_rt.spawn(with_item_timeout(
        timeout,
        execute_item_on_driver(
            driver,
            database_name,
            container_name,
            partition_key,
            item_id,
            body_bytes,
            modifiers,
            honor_content_response,
            build_op,
        ),
    ));

    // Request cancellation when the bridge future is dropped rather than only
    // dropping the JoinHandle, which would detach the task.
    let abort_guard = AbortOnDrop(join.abort_handle());

    // Bridge the Rust JoinHandle to a Python asyncio awaitable. The response
    // tuple is built under the GIL after the future resolves, exactly like the
    // sync path's `tuple_from_result`.
    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        // Keep the guard until the bridge completes or is dropped.
        let _abort_guard = abort_guard;
        let response_result = join.await.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err("cosmos async operation was cancelled before it completed")
            } else {
                PyRuntimeError::new_err(format!("cosmos async operation task failed: {join_error}"))
            }
        })???;
        Python::with_gil(|py| {
            tuple_from_result(py, response_result).map(|tuple| tuple.into_any().unbind())
        })
    })
}

/// The driver work shared by both runners -- the sync runner
/// (`execute_item_operation_sync`, which blocks on it) and the async runner
/// (`execute_item_operation_async`, which spawns it) -- so the two paths do identical
/// work. Resolve the container, build the operation from the per-op closure, apply
/// the typed activity-id / session-token / content-response / options, and execute
/// it. Preparation failures are Python exceptions, separate from the inner
/// driver result so metadata headers cannot masquerade as an item response.
fn execute_item_on_driver(
    driver: Arc<CosmosDriver>,
    database_name: String,
    container_name: String,
    partition_key: Option<PartitionKey>,
    item_id: String,
    body_bytes: Vec<u8>,
    modifiers: RequestHeadersAndOptions,
    honor_content_response: bool,
    build_op: impl FnOnce(ItemReference, Vec<u8>) -> CosmosOperation + Send,
) -> impl std::future::Future<Output = PyResult<Result<CosmosResponse, CosmosError>>> + Send {
    let deadline = modifiers
        .item_timeout
        .map(|timeout| tokio::time::Instant::now() + timeout);
    async move {
        let resolution_options = if modifiers.item_timeout.is_some() {
            build_operation_options(
                None,
                None,
                modifiers.end_to_end_timeout.clone(),
                None,
                Default::default(),
            )
        } else {
            Default::default()
        };
        let container = driver
            .resolve_container(&database_name, &container_name, resolution_options)
            .await
            .map_err(|error| Python::with_gil(|py| metadata_error(py, error)))?;
        let partition_key = match partition_key {
            Some(key) => key,
            None => super::request::extract_partition_key_from_body(
                container.partition_key_definition(),
                &body_bytes,
            )?,
        };
        if deadline.is_some_and(|deadline| tokio::time::Instant::now() >= deadline) {
            return Err(PyTimeoutError::new_err(
                "Item budget exhausted during metadata or key extraction",
            ));
        }
        let item_ref = ItemReference::from_name(&container, partition_key, item_id);
        let mut op = build_op(item_ref, body_bytes);

        if let Some(activity) = modifiers.activity_header.as_ref() {
            // Pass the supplied activity id to the driver without UUID parsing.
            op = op.with_activity_id(ActivityId::from(activity.clone()));
        }
        if let Some(session) = modifiers.session_header.as_ref() {
            op = op.with_session_token(SessionToken::from(session.clone()));
        }

        // no_response=True only applies to writes; delete / read pass
        // honor_content_response=false and keep the driver default.
        let content_response = if honor_content_response {
            Some(modifiers.content_response_on_write)
        } else {
            None
        };
        let options = build_operation_options(
            content_response,
            modifiers.excluded_regions_value,
            modifiers.end_to_end_timeout,
            modifiers.availability_strategy,
            modifiers.custom_headers,
        );

        Ok(driver.execute_singleton_operation(op, options).await)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use azure_core::http::Url;
    use azure_data_cosmos_driver::{
        in_memory_emulator::{
            ContainerConfig, InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion,
        },
        models::{AccountReference, PartitionKeyDefinition, ResponseBody},
        options::{BinaryEncodingOptions, DriverOptions, OperationOptionsBuilder},
    };
    use pyo3::types::PyDict;

    fn modifiers() -> RequestHeadersAndOptions {
        Python::with_gil(|py| {
            let kwargs = PyDict::new_bound(py);
            kwargs.set_item("headers", PyDict::new_bound(py)).unwrap();
            kwargs.set_item("protocol_version", 3).unwrap();
            kwargs
                .set_item("settings", crate::wire::settings::test_settings(py))
                .unwrap();
            let prepared = py
                .import_bound("types")
                .unwrap()
                .getattr("SimpleNamespace")
                .unwrap()
                .call((), Some(&kwargs))
                .unwrap();
            super::super::request::extract_account_prepared_modifiers(&prepared).unwrap()
        })
    }

    #[tokio::test]
    async fn all_six_items_use_binding_owned_metadata_and_preserve_error_phase() {
        pyo3::prepare_freethreaded_python();
        let url = Url::parse("https://single-call.emulator.local").unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap(),
        ));
        emulator.store().create_database("db");
        emulator.store().create_container_with_config(
            "db",
            "c",
            PartitionKeyDefinition::new(vec!["/pk".into()]),
            ContainerConfig::new()
                .with_partition_count(1)
                .build()
                .unwrap(),
        );
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5"))
                    .with_operation_options(
                        OperationOptionsBuilder::new()
                            .with_binary_encoding(BinaryEncodingOptions::new().with_enabled(false))
                            .build(),
                    )
                    .build(),
            )
            .await
            .unwrap();
        for build in [
            CosmosOperation::create_item,
            CosmosOperation::upsert_item,
            CosmosOperation::replace_item,
        ] {
            let result = execute_item_on_driver(
                driver.clone(),
                "db".into(),
                "c".into(),
                None,
                "item".into(),
                br#"{"id":"item","pk":"A","n":0}"#.to_vec(),
                modifiers(),
                true,
                |item, body| build(item).with_body(body),
            )
            .await
            .unwrap()
            .unwrap();
            assert!(result.status().is_success());
        }
        execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            Some(PartitionKey::from("A")),
            "item".into(),
            br#"{"operations":[{"op":"incr","path":"/n","value":1}]}"#.to_vec(),
            modifiers(),
            true,
            |item, body| CosmosOperation::patch_item(item).with_body(body),
        )
        .await
        .unwrap()
        .unwrap();
        let read = execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            Some(PartitionKey::from("A")),
            "item".into(),
            Vec::new(),
            modifiers(),
            false,
            |item, _| CosmosOperation::read_item(item),
        )
        .await
        .unwrap()
        .unwrap();
        let ResponseBody::Bytes(body) = read.body() else {
            panic!("Expected JSON body");
        };
        assert_eq!(
            serde_json::from_slice::<serde_json::Value>(body).unwrap()["n"],
            1
        );

        // Check selection before execution: the single-partition emulator
        // does not model every service-side header/body mismatch rejection.
        execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            Some(PartitionKey::from("B")),
            "other".into(),
            br#"{"id":"other","pk":"A"}"#.to_vec(),
            modifiers(),
            true,
            |item, body| {
                assert_eq!(item.partition_key(), &PartitionKey::from("B"));
                CosmosOperation::create_item(item).with_body(body)
            },
        )
        .await
        .unwrap()
        .unwrap();

        let mut timed = modifiers();
        timed.item_timeout = Some(std::time::Duration::from_millis(1));
        let pending = execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            None,
            "expired".into(),
            br#"{"id":"expired","pk":"A"}"#.to_vec(),
            timed,
            true,
            |_, _| panic!("Expired preparation must not construct an item"),
        );
        tokio::time::sleep(std::time::Duration::from_millis(5)).await;
        let expired = pending.await.unwrap_err();
        Python::with_gil(|py| assert!(expired.is_instance_of::<PyTimeoutError>(py)));

        execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            Some(PartitionKey::from("A")),
            "item".into(),
            Vec::new(),
            modifiers(),
            false,
            |item, _| CosmosOperation::delete_item(item),
        )
        .await
        .unwrap()
        .unwrap();
        let missing_item = execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            Some(PartitionKey::from("A")),
            "item".into(),
            Vec::new(),
            modifiers(),
            false,
            |item, _| CosmosOperation::read_item(item),
        )
        .await
        .unwrap()
        .unwrap_err();
        assert_eq!(u16::from(missing_item.status().status_code()), 404);
        let missing_container = execute_item_on_driver(
            driver,
            "db".into(),
            "missing".into(),
            None,
            "item".into(),
            br#"{"id":"item","pk":"A"}"#.to_vec(),
            modifiers(),
            true,
            |_, _| panic!("Metadata failure must not construct or execute an item"),
        )
        .await
        .unwrap_err();
        Python::with_gil(|py| {
            assert!(
                missing_container.is_instance_of::<super::super::errors::DriverResponseError>(py)
            );
            let response = missing_container
                .value_bound(py)
                .getattr("args")
                .unwrap()
                .get_item(0)
                .unwrap();
            assert_eq!(response.get_item(0).unwrap().extract::<u16>().unwrap(), 404);
        });
    }
}

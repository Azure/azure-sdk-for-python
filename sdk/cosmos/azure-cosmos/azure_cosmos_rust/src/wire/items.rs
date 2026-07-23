// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use std::sync::atomic::Ordering;
use std::sync::Arc;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{
        ActivityId, CosmosOperation, CosmosResponse, ItemReference, PartitionKey, SessionToken,
    },
};

use super::diagnostics::BINDING_OP_COUNT;
use super::request::{
    build_operation_options, parse_container_link, parse_partition_key_header, OpModifiers,
};
use super::response::tuple_from_result;
use super::{lookup_driver, AbortOnDrop};
use crate::runtime::require_runtime_context;

/// Sync runner shared by all six point operations (`documents/items.rs` sync entries).
/// Steps: bump the binding-invocation counter, look up the rust driver by handle,
/// parse the container link and partition key, then -- with the GIL released --
/// block the calling thread on the shared Tokio runtime until the driver resolves
/// the container, builds and runs the operation, and returns. Turn the driver's
/// `CosmosResponse` (or a `CosmosError` that still carries a wire response) into
/// the `BackendResponse` tuple the Python parser reads. Only three things vary per
/// op, so each entry point passes them in: the item id, whether `no_response`
/// applies (writes only), and a closure that builds the operation from the
/// resolved `ItemReference`. The async sibling below spawns this same future
/// instead of blocking, so both paths run identical driver work.
pub(crate) fn run_item_operation<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
    partition_key_header: &str,
    modifiers: OpModifiers,
    item_id: String,
    op_name: &str,
    honor_content_response: bool,
    build_op: impl FnOnce(ItemReference) -> CosmosOperation + Send,
) -> PyResult<Bound<'py, PyTuple>> {
    // Count that the rust binding actually ran this operation (see
    // BINDING_OP_COUNT). Bumped on entry so it reflects every op routed into the
    // binding on the sync path.
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let partition_key = parse_partition_key_header(partition_key_header)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    // Sync path: block the calling thread on the shared runtime until the driver
    // finishes. (The async sibling below spawns the very same future instead, so
    // both paths run identical driver work.)
    let response_result: Result<CosmosResponse, CosmosError> = py.allow_threads(|| {
        runtime_ctx.tokio_rt.block_on(run_singleton_future(
            driver,
            database_name,
            container_name,
            partition_key,
            item_id,
            modifiers,
            honor_content_response,
            build_op,
        ))
    });

    tuple_from_result(py, response_result)
}

/// Aborts the spawned driver task if this guard is dropped before the task has
/// finished. The problem it solves: a Tokio `JoinHandle` does NOT own its task --
/// dropping the handle *detaches* the task, leaving it to run to completion in the
/// background (holding a connection, spending RU) with its result thrown away. So
/// the async runner keeps this guard (built from the task's `abort_handle()`)
/// alive for the lifetime of the bridged Python awaitable. When asyncio cancels
/// the `await` (a client-side timeout, or the surrounding task being cancelled)
/// `pyo3-async-runtimes` drops the bridging future, which drops this guard, which
/// calls `abort()` -- so the in-flight driver operation is actually cancelled (its
/// connection released, no further work or RU spent) instead of detached. On
/// normal completion the task is already finished, so `abort()` is a harmless
/// Async sibling of `run_item_operation`: same inputs and identical driver work,
/// but instead of blocking a worker thread it spawns the driver future on the
/// shared Tokio runtime (the same runtime the driver was built on, so its
/// connection pool and timers stay put) and hands the asyncio event loop an
/// awaitable that resolves to the `BackendResponse` tuple. Awaiting it uses no
/// Python thread per in-flight call. The awaitable owns an `AbortOnDrop` guard
/// (see above) so a cancelled `await` actually cancels the driver operation
/// rather than detaching it.
pub(crate) fn run_item_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
    partition_key_header: &str,
    modifiers: OpModifiers,
    item_id: String,
    op_name: &str,
    honor_content_response: bool,
    build_op: impl FnOnce(ItemReference) -> CosmosOperation + Send + 'static,
) -> PyResult<Bound<'py, PyAny>> {
    // Count that the rust binding actually ran this operation (see
    // BINDING_OP_COUNT). Bumped on entry, async path.
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    // Synchronous extraction (GIL held) -- identical to the sync path. Errors
    // here surface when the coroutine is created, before it is awaited.
    let driver = lookup_driver(handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let partition_key = parse_partition_key_header(partition_key_header)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    // Spawn the driver work on the shared runtime; `join` is a cheap handle the
    // bridge below awaits without holding the GIL or pinning a worker thread.
    let join = runtime_ctx.tokio_rt.spawn(run_singleton_future(
        driver,
        database_name,
        container_name,
        partition_key,
        item_id,
        modifiers,
        honor_content_response,
        build_op,
    ));

    // Propagate Python-side cancellation to the driver. Without this, cancelling
    // the awaitable would only drop the JoinHandle -- which *detaches* the Tokio
    // task, letting the operation run to completion in the background (holding a
    // connection, spending RU) with its result discarded. Holding this guard for
    // the lifetime of the bridging future means a cancelled `await` drops the
    // guard and aborts the task instead, so a client-side timeout actually stops
    // the work.
    let abort_guard = AbortOnDrop(join.abort_handle());

    // Bridge the Rust JoinHandle to a Python asyncio awaitable. The response
    // tuple is built under the GIL after the future resolves, exactly like the
    // sync path's `tuple_from_result`.
    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        // Keep the abort guard alive for exactly as long as we await the task; if
        // the Python future is cancelled, this block is dropped, dropping the
        // guard and aborting the task (see AbortOnDrop).
        let _abort_guard = abort_guard;
        let response_result = join.await.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err("cosmos async operation was cancelled before it completed")
            } else {
                PyRuntimeError::new_err(format!("cosmos async operation task failed: {join_error}"))
            }
        })?;
        Python::with_gil(|py| {
            tuple_from_result(py, response_result).map(|tuple| tuple.into_any().unbind())
        })
    })
}

// ---------------------------------------------------------------------------
// Query page execution
//
// This is the engine that lets feed-style operations be fetched by the Rust
// driver instead of by the Python HTTP path:
//   * query_items (one SQL query page)
//   * read_all_items (native read-feed, no synthetic SQL)
/// The driver work shared by both runners -- the sync runner
/// (`run_item_operation`, which blocks on it) and the async runner
/// (`run_item_operation_async`, which spawns it) -- so the two paths do identical
/// work. Resolve the container, build the operation from the per-op closure, apply
/// the typed activity-id / session-token / content-response / options, and execute
/// it. Returns the raw driver result; the callers turn it into the Python tuple
/// under the GIL.
async fn run_singleton_future(
    driver: Arc<CosmosDriver>,
    database_name: String,
    container_name: String,
    partition_key: PartitionKey,
    item_id: String,
    modifiers: OpModifiers,
    honor_content_response: bool,
    build_op: impl FnOnce(ItemReference) -> CosmosOperation + Send,
) -> Result<CosmosResponse, CosmosError> {
    let container = driver
        .resolve_container(&database_name, &container_name)
        .await?;
    let item_ref = ItemReference::from_name(&container, partition_key, item_id);
    let mut op = build_op(item_ref);

    if let Some(activity) = modifiers.activity_header.as_ref() {
        // Forward the correlation id verbatim. The legacy path forwards any
        // x-ms-activity-id string; gating on UUID-parseability silently dropped
        // non-UUID correlation ids (e.g. an application-supplied trace id), so
        // server-side request correlation broke for exactly those requests --
        // the moment a customer is trying to trace one. ActivityId accepts any
        // string, and the service treats the header as opaque.
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

    driver.execute_singleton_operation(op, options).await
}

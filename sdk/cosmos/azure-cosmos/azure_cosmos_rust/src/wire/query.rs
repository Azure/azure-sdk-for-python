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
    models::{ActivityId, CosmosOperation, CosmosResponse, FeedRange, PartitionKey, SessionToken},
};

use super::diagnostics::BINDING_OP_COUNT;
use super::request::{
    build_operation_options, parse_container_link, parse_query_target_header, OpModifiers,
};
use super::response::tuple_from_feed_result;
use super::{lookup_driver, AbortOnDrop};
use crate::runtime::require_runtime_context;

// Query and read-all operations share the same feed-shaped response boundary.
// The flow is: the Python wrapper hands us a
// PreparedRequest, we work out scope (single logical partition vs full
// container), ask the driver for one page, and turn the driver's reply back
// into the exact shape the Python feed parser expects.
// ---------------------------------------------------------------------------

/// The scope of the query, worked out from `PreparedRequest.partition_key_header`.
/// This is how we know whether the customer asked for one partition or the whole
/// container.
pub(super) enum QueryTarget {
    /// Search one logical partition (the customer passed a `partition_key`).
    Partition(PartitionKey),
    /// Search the full container (the customer used cross-partition query, or
    /// this is a whole-container `read_all_items`).
    CrossPartition,
}

/// Entry point the binding calls to run one query page and wait for it. Finds the
/// driver for this client, splits the container link into database + container
/// names, works out the query scope, then runs the driver work below and converts
/// the reply into the tuple the Python parser reads. Mirrors `run_item_operation`
/// but builds a `CosmosOperation::query_items` targeting either a logical partition
/// (`["pk"]`) or the full container (`[]`).
pub(crate) fn run_query_operation<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
    partition_key_header: &str,
    modifiers: OpModifiers,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let query_target = parse_query_target_header(partition_key_header)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let response_result: Result<Option<CosmosResponse>, CosmosError> = py.allow_threads(|| {
        runtime_ctx.tokio_rt.block_on(run_query_future(
            driver,
            database_name,
            container_name,
            query_target,
            modifiers,
            body_bytes,
        ))
    });

    tuple_from_feed_result(py, response_result)
}

/// Async sibling of `run_query_operation`.
pub(crate) fn run_query_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
    partition_key_header: &str,
    modifiers: OpModifiers,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let query_target = parse_query_target_header(partition_key_header)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let join = runtime_ctx.tokio_rt.spawn(run_query_future(
        driver,
        database_name,
        container_name,
        query_target,
        modifiers,
        body_bytes,
    ));
    let abort_guard = AbortOnDrop(join.abort_handle());

    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let response_result = join.await.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err("cosmos async operation was cancelled before it completed")
            } else {
                PyRuntimeError::new_err(format!("cosmos async operation task failed: {join_error}"))
            }
        })?;
        Python::with_gil(|py| {
            tuple_from_feed_result(py, response_result).map(|tuple| tuple.into_any().unbind())
        })
    })
}

/// Entry point the binding calls to run one read_all_items feed page and wait for it.
/// The partition-key header controls scope:
///   * `[]` => full-container read (`read_all_items_cross_partition`)
///   * non-empty array => logical-partition read (`read_all_items`)
///
/// The shared driver owns the execution choice: full-container reads are represented
/// internally as a query so its planner handles topology, fan-out, and continuation.
pub(crate) fn run_read_all_items_operation<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
    partition_key_header: &str,
    modifiers: OpModifiers,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let query_target = parse_query_target_header(partition_key_header)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let response_result: Result<Option<CosmosResponse>, CosmosError> = py.allow_threads(|| {
        runtime_ctx.tokio_rt.block_on(run_read_all_items_future(
            driver,
            database_name,
            container_name,
            query_target,
            modifiers,
        ))
    });

    tuple_from_feed_result(py, response_result)
}

/// Async sibling of `run_read_all_items_operation`.
pub(crate) fn run_read_all_items_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
    partition_key_header: &str,
    modifiers: OpModifiers,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let query_target = parse_query_target_header(partition_key_header)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let join = runtime_ctx.tokio_rt.spawn(run_read_all_items_future(
        driver,
        database_name,
        container_name,
        query_target,
        modifiers,
    ));
    let abort_guard = AbortOnDrop(join.abort_handle());

    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let response_result = join.await.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err("cosmos async operation was cancelled before it completed")
            } else {
                PyRuntimeError::new_err(format!("cosmos async operation task failed: {join_error}"))
            }
        })?;
        Python::with_gil(|py| {
            tuple_from_feed_result(py, response_result).map(|tuple| tuple.into_any().unbind())
        })
    })
}
/// The actual driver work for one query page. Resolves the container, builds a
/// `FeedRange` that limits the search to one partition or opens it to the whole
/// container, then builds a `query_items` operation carrying the query JSON (from
/// the request body) plus the session token, activity id, excluded regions,
/// timeout, and any custom headers the wrapper attached. Returns one page.
async fn run_query_future(
    driver: Arc<CosmosDriver>,
    database_name: String,
    container_name: String,
    query_target: QueryTarget,
    modifiers: OpModifiers,
    body_bytes: Vec<u8>,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let container = driver
        .resolve_container(&database_name, &container_name)
        .await?;
    let feed_range = match query_target {
        QueryTarget::Partition(partition_key) => {
            FeedRange::for_partition(partition_key, container.partition_key_definition())
        }
        QueryTarget::CrossPartition => FeedRange::full(),
    };
    let mut op = CosmosOperation::query_items(container, Some(feed_range)).with_body(body_bytes);

    if let Some(activity) = modifiers.activity_header.as_ref() {
        op = op.with_activity_id(ActivityId::from(activity.clone()));
    }
    if let Some(session) = modifiers.session_header.as_ref() {
        op = op.with_session_token(SessionToken::from(session.clone()));
    }

    let options = build_operation_options(
        None,
        modifiers.excluded_regions_value,
        modifiers.end_to_end_timeout,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    driver.execute_operation(op, options).await
}

/// Driver work for `read_all_items`: resolve the container and pass the requested
/// scope to the shared driver. A logical partition uses read-feed; full-container
/// scope uses the driver's internal query representation.
async fn run_read_all_items_future(
    driver: Arc<CosmosDriver>,
    database_name: String,
    container_name: String,
    query_target: QueryTarget,
    modifiers: OpModifiers,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let container = driver
        .resolve_container(&database_name, &container_name)
        .await?;
    let mut op = match query_target {
        // The public Python API currently produces full-container scope. Keep the
        // partition arm so this binding remains ready for a partition-scoped API.
        QueryTarget::Partition(partition_key) => {
            CosmosOperation::read_all_items(container, partition_key)
        }
        QueryTarget::CrossPartition => CosmosOperation::read_all_items_cross_partition(container),
    };

    if let Some(activity) = modifiers.activity_header.as_ref() {
        op = op.with_activity_id(ActivityId::from(activity.clone()));
    }
    if let Some(session) = modifiers.session_header.as_ref() {
        op = op.with_session_token(SessionToken::from(session.clone()));
    }

    let options = build_operation_options(
        None,
        modifiers.excluded_regions_value,
        modifiers.end_to_end_timeout,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    driver.execute_operation(op, options).await
}

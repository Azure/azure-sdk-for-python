// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Fetch one item-query page without retaining a feed cursor.
//!
//! The binding chooses the scope from the typed partition key, asks the Rust
//! driver for one page, and returns a binding response tuple. Public retained
//! paging uses the feed cursor in item_feed.rs instead of these compatibility helpers.

use super::partition_key_input::BindingPartitionKey;
use std::sync::Arc;

use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{ActivityId, CosmosOperation, CosmosResponse, FeedRange, PartitionKey, SessionToken},
};

use super::deadline::{parse_remaining_timeout, with_page_timeout};
use super::driver_runner::{
    run_prepared_driver_operation_async, run_prepared_driver_operation_sync,
};
use super::request::{build_operation_options, parse_container_link, RequestHeadersAndOptions};
use super::response::tuple_from_feed_result;

/// The scope of the query, worked out from `PreparedRequest.partition_key`.
/// A supplied key is converted to a feed range using the container definition.
pub(super) enum QueryTarget {
    /// Search the range derived from the supplied partition-key components.
    Partition(PartitionKey),
    /// Search the full container.
    CrossPartition,
}

/// Prepare and execute one query page, then return its binding response tuple.
/// Resolve the container link and typed query scope before waiting. The supplied
/// page timeout covers metadata resolution and execution together.
pub(crate) fn run_query_operation<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    container_link: &str,
    partition_key_input: BindingPartitionKey,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
    op_name: &str,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    run_prepared_driver_operation_sync(
        py,
        driver_handle,
        op_name,
        move |driver| {
            let (database_name, container_name) = parse_container_link(container_link)?;
            let query_target = partition_key_input.into_query_target()?;
            Ok(with_page_timeout(
                timeout,
                run_query_future(
                    driver,
                    database_name,
                    container_name,
                    query_target,
                    modifiers,
                    body_bytes,
                ),
            ))
        },
        |py, result| tuple_from_feed_result(py, result?),
    )
}

/// Async sibling of `run_query_operation`.
pub(crate) fn run_query_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    container_link: &str,
    partition_key_input: BindingPartitionKey,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
    op_name: &str,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    run_prepared_driver_operation_async(
        py,
        driver_handle,
        op_name,
        move |driver| {
            let (database_name, container_name) = parse_container_link(container_link)?;
            let query_target = partition_key_input.into_query_target()?;
            Ok(with_page_timeout(
                timeout,
                run_query_future(
                    driver,
                    database_name,
                    container_name,
                    query_target,
                    modifiers,
                    body_bytes,
                ),
            ))
        },
        |py, result| tuple_from_feed_result(py, result?),
    )
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
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let container = driver
        .resolve_container(&database_name, &container_name, Default::default())
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
        modifiers.driver_timeout_policy,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    driver.execute_operation(op, options).await
}

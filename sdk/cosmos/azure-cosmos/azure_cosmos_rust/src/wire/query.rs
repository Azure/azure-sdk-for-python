// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Fetch one item-query or read-all page without retaining a feed cursor.
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

const READ_ALL_ITEMS_QUERY_BODY: &[u8] = br#"{"query":"SELECT * FROM root r"}"#;

/// The scope of the query, worked out from `PreparedRequest.partition_key`.
/// A supplied key is converted to a feed range using the container definition.
pub(super) enum QueryTarget {
    /// Search the range derived from the supplied partition-key components.
    Partition(PartitionKey),
    /// Search the full container (the customer app used cross-partition query, or
    /// this is a whole-container `read_all_items`).
    CrossPartition,
}

/// Selects the driver operation used by `read_all_items`.
enum ReadAllItemsExecution {
    ReadFeed(PartitionKey),
    Query,
}

impl From<QueryTarget> for ReadAllItemsExecution {
    fn from(target: QueryTarget) -> Self {
        match target {
            QueryTarget::Partition(partition_key) => Self::ReadFeed(partition_key),
            QueryTarget::CrossPartition => Self::Query,
        }
    }
}

/// Prepare and execute one query page, then return its binding response tuple.
/// Resolve the container link and typed query scope before waiting. The supplied
/// page timeout covers metadata resolution and execution together.
pub(crate) fn run_query_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
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
    driver_handle: &str,
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

/// Entry point the binding calls to run one `read_all_items` page and wait for it.
/// Typed `BindingPartitionKey` selects a full-container query or partition read-feed.
pub(crate) fn run_read_all_items_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
    container_link: &str,
    partition_key_input: BindingPartitionKey,
    modifiers: RequestHeadersAndOptions,
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
                run_read_all_items_future(
                    driver,
                    database_name,
                    container_name,
                    query_target,
                    modifiers,
                ),
            ))
        },
        |py, result| tuple_from_feed_result(py, result?),
    )
}

/// Async sibling of `run_read_all_items_operation`.
pub(crate) fn run_read_all_items_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    container_link: &str,
    partition_key_input: BindingPartitionKey,
    modifiers: RequestHeadersAndOptions,
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
                run_read_all_items_future(
                    driver,
                    database_name,
                    container_name,
                    query_target,
                    modifiers,
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

/// Rust driver work for stateless `read_all_items`. A supplied partition key
/// selects read-feed; whole-container scope selects `SELECT * FROM root r`.
/// Public retained paging uses `item_feed.rs`, not this one-page helper.
async fn run_read_all_items_future(
    driver: Arc<CosmosDriver>,
    database_name: String,
    container_name: String,
    query_target: QueryTarget,
    modifiers: RequestHeadersAndOptions,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let container = driver
        .resolve_container(&database_name, &container_name, Default::default())
        .await?;
    let mut op = match ReadAllItemsExecution::from(query_target) {
        // Keep partition read-feed distinct from the whole-container query.
        ReadAllItemsExecution::ReadFeed(partition_key) => {
            CosmosOperation::read_all_items(container, partition_key)
        }
        ReadAllItemsExecution::Query => {
            CosmosOperation::query_items(container, Some(FeedRange::full()))
                .with_body(READ_ALL_ITEMS_QUERY_BODY.to_vec())
        }
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
        modifiers.driver_timeout_policy,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    driver.execute_operation(op, options).await
}

#[cfg(test)]
mod tests {
    use super::{PartitionKey, QueryTarget, ReadAllItemsExecution, READ_ALL_ITEMS_QUERY_BODY};

    #[test]
    fn read_all_items_query_matches_legacy_python_rewrite() {
        let payload: serde_json::Value = serde_json::from_slice(READ_ALL_ITEMS_QUERY_BODY).unwrap();

        assert_eq!(payload["query"], "SELECT * FROM root r");
    }

    #[test]
    fn read_all_items_selects_execution_from_scope() {
        assert!(matches!(
            ReadAllItemsExecution::from(QueryTarget::CrossPartition),
            ReadAllItemsExecution::Query
        ));
        assert!(matches!(
            ReadAllItemsExecution::from(QueryTarget::Partition(PartitionKey::from("tenant-a"))),
            ReadAllItemsExecution::ReadFeed(_)
        ));
    }
}

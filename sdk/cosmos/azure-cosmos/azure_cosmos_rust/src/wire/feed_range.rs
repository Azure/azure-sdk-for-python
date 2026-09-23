// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::partition_key_input::BindingPartitionKey;
use std::sync::atomic::Ordering;
use std::sync::Arc;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{
        FeedRange, PartitionKey, PartitionKeyDefinition, PartitionKeyKind, PartitionKeyVersion,
    },
};

use super::diagnostics::BINDING_OP_COUNT;
use super::request::parse_container_link;
use super::response::{
    tuple_from_feed_range_from_partition_key_result, tuple_from_is_feed_range_subset_result,
    tuple_from_partition_key_ranges_result,
};
use super::{lookup_driver, AbortOnDrop};
use crate::feed_range_subset::compute_is_feed_range_subset;
use crate::runtime::require_runtime_context;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
/// Describes which Python partition-key form produced the parsed key.
pub(super) enum FeedRangePartitionKeySource {
    /// A normal partition-key value.
    Standard,
    /// The typed marker for Python's internal empty partition key.
    EmptySentinel,
    /// A caller supplied an empty sequence as the partition key.
    ExplicitEmptySequence,
}

#[derive(Clone, Debug)]
/// A parsed partition key and the Python form that produced it.
pub(super) struct FeedRangePartitionKeyInput {
    pub(super) partition_key: PartitionKey,
    pub(super) source: FeedRangePartitionKeySource,
}

#[derive(Debug)]
/// Values returned to Python for a feed range.
pub(super) struct FeedRangeFromPartitionKeyPayload {
    pub(super) min: String,
    pub(super) max: String,
    pub(super) is_max_inclusive: bool,
}

#[derive(Debug)]
/// Errors that preserve the Python behavior of feed-range calculation.
pub(super) enum FeedRangeFromPartitionKeyError {
    Cosmos(CosmosError),
    Validation(String),
    LegacyAttribute(String),
    LegacyType(String),
}

/// Handle empty partition-key forms whose result depends on the container definition.
pub(super) fn maybe_handle_feed_range_partition_key_special_case(
    definition: &PartitionKeyDefinition,
    source: FeedRangePartitionKeySource,
) -> Result<Option<FeedRangeFromPartitionKeyPayload>, FeedRangeFromPartitionKeyError> {
    match source {
        FeedRangePartitionKeySource::Standard => Ok(None),
        FeedRangePartitionKeySource::EmptySentinel => {
            if definition.version() == PartitionKeyVersion::V1 {
                return Err(FeedRangeFromPartitionKeyError::LegacyType(
                    "Unexpected type for PK component: <class 'azure.cosmos.partition_key._Empty'>"
                        .to_string(),
                ));
            }
            let epk = "00000000000000000000000000000000".to_string();
            Ok(Some(FeedRangeFromPartitionKeyPayload {
                min: epk.clone(),
                max: epk,
                is_max_inclusive: true,
            }))
        }
        FeedRangePartitionKeySource::ExplicitEmptySequence => {
            if definition.kind() == PartitionKeyKind::MultiHash {
                Ok(None)
            } else {
                Err(FeedRangeFromPartitionKeyError::LegacyAttribute(
                    "'int' object has no attribute 'upper'".to_string(),
                ))
            }
        }
    }
}

/// Entry point that enumerates every partition-key range for one container.
/// The Python wrapper uses this to implement `ContainerProxy.read_feed_ranges`
/// on the Rust path (sync version).
pub(crate) fn run_read_feed_ranges_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
    container_link: &str,
    force_refresh: bool,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let response_result = py.allow_threads(|| {
        runtime_ctx.tokio_rt.block_on(run_read_feed_ranges_future(
            driver,
            database_name,
            container_name,
            force_refresh,
        ))
    });

    tuple_from_partition_key_ranges_result(py, response_result)
}

/// Async sibling of `run_read_feed_ranges_operation`.
pub(crate) fn run_read_feed_ranges_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    container_link: &str,
    force_refresh: bool,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let join = runtime_ctx.tokio_rt.spawn(run_read_feed_ranges_future(
        driver,
        database_name,
        container_name,
        force_refresh,
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
            tuple_from_partition_key_ranges_result(py, response_result)
                .map(|tuple| tuple.into_any().unbind())
        })
    })
}

/// Entry point that computes the feed range one partition key falls into.
pub(crate) fn run_feed_range_from_partition_key_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
    container_link: &str,
    partition_key_input: BindingPartitionKey,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let partition_key_input = partition_key_input.into_feed_range_key()?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let response_result = py.allow_threads(|| {
        runtime_ctx
            .tokio_rt
            .block_on(run_feed_range_from_partition_key_future(
                driver,
                database_name,
                container_name,
                partition_key_input,
            ))
    });

    tuple_from_feed_range_from_partition_key_result(py, response_result)
}

/// Async sibling of `run_feed_range_from_partition_key_operation`.
pub(crate) fn run_feed_range_from_partition_key_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    container_link: &str,
    partition_key_input: BindingPartitionKey,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let partition_key_input = partition_key_input.into_feed_range_key()?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let join = runtime_ctx
        .tokio_rt
        .spawn(run_feed_range_from_partition_key_future(
            driver,
            database_name,
            container_name,
            partition_key_input,
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
            tuple_from_feed_range_from_partition_key_result(py, response_result)
                .map(|tuple| tuple.into_any().unbind())
        })
    })
}
/// Resolve the container and ask the Rust driver for its partition-key ranges.
/// Pass force_refresh to the Rust driver; cache lookup and range ordering are
/// its responsibility, not work performed by this helper.
async fn run_read_feed_ranges_future(
    driver: Arc<CosmosDriver>,
    database_name: String,
    container_name: String,
    force_refresh: bool,
) -> Result<
    Option<Vec<azure_data_cosmos_driver::models::partition_key_range::PartitionKeyRange>>,
    CosmosError,
> {
    let container = driver
        .resolve_container(&database_name, &container_name, Default::default())
        .await?;
    driver
        .resolve_all_partition_key_ranges(&container, force_refresh)
        .await
}

/// Resolve container metadata and compute bounds for the supplied partition key.
/// Return the bounds and inclusivity flag; response.rs builds the Python body.
async fn run_feed_range_from_partition_key_future(
    driver: Arc<CosmosDriver>,
    database_name: String,
    container_name: String,
    partition_key_input: FeedRangePartitionKeyInput,
) -> Result<FeedRangeFromPartitionKeyPayload, FeedRangeFromPartitionKeyError> {
    let container = driver
        .resolve_container(&database_name, &container_name, Default::default())
        .await
        .map_err(FeedRangeFromPartitionKeyError::Cosmos)?;
    let definition = container.partition_key_definition();
    if let Some(payload) =
        maybe_handle_feed_range_partition_key_special_case(definition, partition_key_input.source)?
    {
        return Ok(payload);
    }
    let partition_key = partition_key_input.partition_key;
    let pk_len = partition_key.len();
    let path_len = definition.paths().len();
    if definition.kind() == PartitionKeyKind::MultiHash && pk_len > path_len {
        return Err(FeedRangeFromPartitionKeyError::Validation(format!(
            "{pk_len} partition key components provided. Expected less than {path_len} components (number of container partition key definition components)."
        )));
    }

    let epk = FeedRange::for_partition(partition_key, definition)
        .min_inclusive()
        .to_hex();

    let (max, is_max_inclusive) =
        if definition.kind() == PartitionKeyKind::MultiHash && pk_len < path_len {
            // Prefix key semantics on MultiHash match the legacy Python helper:
            // normal prefix -> max = min + "FF"; MIN/ MAX sentinels keep their
            // dedicated closed forms.
            if epk.is_empty() {
                (String::new(), false)
            } else if epk == "FF" {
                ("FF".to_string(), false)
            } else {
                (format!("{epk}FF"), false)
            }
        } else {
            (epk.clone(), true)
        };

    Ok(FeedRangeFromPartitionKeyPayload {
        min: epk,
        max,
        is_max_inclusive,
    })
}
/// Check whether the child range in the request body is inside the parent range.
pub(crate) fn run_is_feed_range_subset_operation<'py>(
    py: Python<'py>,
    body_bytes: Vec<u8>,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let result = compute_is_feed_range_subset(&body_bytes);
    tuple_from_is_feed_range_subset_result(py, result)
}

/// Schedule the local subset comparison on the Tokio runtime and return an awaitable.
/// This path requires an initialized RuntimeContext but does not look up a
/// CosmosDriver object or contact the service backend.
pub(crate) fn run_is_feed_range_subset_operation_async<'py>(
    py: Python<'py>,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let runtime_ctx = require_runtime_context(op_name)?;

    let join = runtime_ctx
        .tokio_rt
        .spawn(async move { compute_is_feed_range_subset(&body_bytes) });
    let abort_guard = AbortOnDrop(join.abort_handle());

    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let result = join.await.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err("cosmos async operation was cancelled before it completed")
            } else {
                PyRuntimeError::new_err(format!("cosmos async operation task failed: {join_error}"))
            }
        })?;
        Python::with_gil(|py| {
            tuple_from_is_feed_range_subset_result(py, result)
                .map(|tuple| tuple.into_any().unbind())
        })
    })
}

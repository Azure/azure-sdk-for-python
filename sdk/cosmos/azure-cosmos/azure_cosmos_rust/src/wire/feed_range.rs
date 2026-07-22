// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(super) enum FeedRangePartitionKeySource {
    Standard,
    EmptySentinel,
    ExplicitEmptySequence,
}

#[derive(Clone, Debug)]
pub(super) struct FeedRangePartitionKeyInput {
    pub(super) partition_key: PartitionKey,
    pub(super) source: FeedRangePartitionKeySource,
}

#[derive(Debug)]
pub(super) struct FeedRangeFromPartitionKeyPayload {
    pub(super) min: String,
    pub(super) max: String,
    pub(super) is_max_inclusive: bool,
}

#[derive(Debug)]
pub(super) enum FeedRangeFromPartitionKeyError {
    Cosmos(CosmosError),
    Validation(String),
    LegacyAttribute(String),
    LegacyType(String),
}

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
    handle: &str,
    container_link: &str,
    force_refresh: bool,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
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
    handle: &str,
    container_link: &str,
    force_refresh: bool,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
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

/// Entry point that computes the feed-range envelope for one partition key.
pub(crate) fn run_feed_range_from_partition_key_operation<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
    partition_key_header: &str,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let partition_key_input = parse_feed_range_partition_key_header(partition_key_header)?;
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
    handle: &str,
    container_link: &str,
    partition_key_header: &str,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let partition_key_input = parse_feed_range_partition_key_header(partition_key_header)?;
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
/// Driver work for `read_feed_ranges`: resolve the container, ask the driver for
/// all partition-key ranges (cached unless `force_refresh` is true), and return
/// them in min-EPK order.
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
        .resolve_container(&database_name, &container_name)
        .await?;
    Ok(driver
        .resolve_all_partition_key_ranges(&container, force_refresh)
        .await)
}

/// Driver work for `feed_range_from_partition_key`: resolve container metadata,
/// compute the effective-partition-key envelope for the supplied partition key,
/// and return it in the legacy Python feed-range shape.
async fn run_feed_range_from_partition_key_future(
    driver: Arc<CosmosDriver>,
    database_name: String,
    container_name: String,
    partition_key_input: FeedRangePartitionKeyInput,
) -> Result<FeedRangeFromPartitionKeyPayload, FeedRangeFromPartitionKeyError> {
    let container = driver
        .resolve_container(&database_name, &container_name)
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
        .as_str()
        .to_owned();

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
pub(crate) fn run_is_feed_range_subset_operation<'py>(
    py: Python<'py>,
    body_bytes: Vec<u8>,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let result = compute_is_feed_range_subset(&body_bytes);
    tuple_from_is_feed_range_subset_result(py, result)
}

/// Async sibling of `run_is_feed_range_subset_operation`. The work is still a
/// pure local computation; it runs on the shared Tokio runtime only so the async
/// caller gets a real awaitable, matching every other async entry point.
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

// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Binding calls for feed-range lookup and local subset comparison.
//!
//! Lookup uses the retained CosmosDriver object. Subset comparison reads the
//! two ranges from body bytes and does not contact the service backend.

use super::*;

/// Read the container's partition-key ranges through the Rust driver.
///
/// The request body may carry `{"forceRefresh": true}` to force a cache
/// refresh. An illustrative response body is
/// `{"PartitionKeyRanges":[{"id":"0","minInclusive":"","maxExclusive":"FF"}]}`.
#[pyfunction]
pub(crate) fn read_feed_ranges<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "read_feed_ranges")?;
    let (container_link, force_refresh) = extract_read_feed_ranges_inputs(prepared)?;
    run_read_feed_ranges_operation(
        py,
        driver_handle,
        &container_link,
        force_refresh,
        "read_feed_ranges",
    )
}

/// Compute a feed range from the typed partition key and container metadata.
///
/// Return a response tuple whose body contains Range with min, max,
/// isMinInclusive, and isMaxInclusive fields.
#[pyfunction]
pub(crate) fn feed_range_from_partition_key<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "feed_range_from_partition_key")?;
    let (container_link, partition_key) = extract_feed_range_from_partition_key_inputs(prepared)?;
    run_feed_range_from_partition_key_operation(
        py,
        driver_handle,
        &container_link,
        partition_key,
        "feed_range_from_partition_key",
    )
}

/// Check locally whether one feed range sits entirely inside another. No service request;
/// the two feed ranges arrive in the request body as `{"parent": <feed-range
/// dict>, "child": <feed-range dict>}` and the answer comes back as
/// `{"IsSubset": <bool>}`. The binding normalizes both ranges to `[min, max)`
/// bounds before calling the driver's local subset comparison.
#[pyfunction]
pub(crate) fn is_feed_range_subset<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "is_feed_range_subset")?;
    let _ = driver_handle;
    crate::wire::settings::validate_request_protocol(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_is_feed_range_subset_operation(py, body_bytes)
}

/// Return an awaitable that reads a container's partition-key ranges.
#[pyfunction]
pub(crate) fn read_feed_ranges_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "read_feed_ranges")?;
    let (container_link, force_refresh) = extract_read_feed_ranges_inputs(prepared)?;
    run_read_feed_ranges_operation_async(
        py,
        driver_handle,
        &container_link,
        force_refresh,
        "read_feed_ranges",
    )
}

/// Async twin of `feed_range_from_partition_key`.
#[pyfunction]
pub(crate) fn feed_range_from_partition_key_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "feed_range_from_partition_key")?;
    let (container_link, partition_key) = extract_feed_range_from_partition_key_inputs(prepared)?;
    run_feed_range_from_partition_key_operation_async(
        py,
        driver_handle,
        &container_link,
        partition_key,
        "feed_range_from_partition_key",
    )
}

/// Async twin of `is_feed_range_subset`.
#[pyfunction]
pub(crate) fn is_feed_range_subset_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "is_feed_range_subset")?;
    let _ = driver_handle;
    crate::wire::settings::validate_request_protocol(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_is_feed_range_subset_operation_async(py, body_bytes, "is_feed_range_subset")
}

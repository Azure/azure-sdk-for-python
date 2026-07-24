// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;

/// Enumerate the container's partition-key ranges.
#[pyfunction]
pub(crate) fn read_feed_ranges<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, force_refresh) = extract_read_feed_ranges_inputs(prepared)?;
    run_read_feed_ranges_operation(
        py,
        handle,
        &container_link,
        force_refresh,
        "read_feed_ranges",
    )
}

/// feed_range_from_partition_key: compute the feed range that one partition key falls into.
#[pyfunction]
pub(crate) fn feed_range_from_partition_key<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header) =
        extract_feed_range_from_partition_key_inputs(prepared)?;
    run_feed_range_from_partition_key_operation(
        py,
        handle,
        &container_link,
        &partition_key_header,
        "feed_range_from_partition_key",
    )
}

/// is_feed_range_subset: pure client-side check of whether one feed range's
/// effective-partition-key span sits entirely inside another's. No network call;
/// the two feed ranges arrive in the request body as `{"parent": <feed-range
/// dict>, "child": <feed-range dict>}` and the answer comes back as
/// `{"IsSubset": <bool>}`. The binding normalizes both ranges to `[min, max)`
/// bounds (matching the legacy python path) before asking the driver. Without it,
/// is_feed_range_subset could not run on the rust backend and would stay on the
/// legacy python path.
#[pyfunction]
pub(crate) fn is_feed_range_subset<'py>(
    py: Python<'py>,
    _handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let body_bytes = extract_body_bytes(prepared)?;
    run_is_feed_range_subset_operation(py, body_bytes)
}

#[pyfunction]
pub(crate) fn read_feed_ranges_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, force_refresh) = extract_read_feed_ranges_inputs(prepared)?;
    run_read_feed_ranges_operation_async(
        py,
        handle,
        &container_link,
        force_refresh,
        "read_feed_ranges",
    )
}

/// Async twin of `feed_range_from_partition_key`.
#[pyfunction]
pub(crate) fn feed_range_from_partition_key_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header) =
        extract_feed_range_from_partition_key_inputs(prepared)?;
    run_feed_range_from_partition_key_operation_async(
        py,
        handle,
        &container_link,
        &partition_key_header,
        "feed_range_from_partition_key",
    )
}

/// Async twin of `is_feed_range_subset`.
#[pyfunction]
pub(crate) fn is_feed_range_subset_async<'py>(
    py: Python<'py>,
    _handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let body_bytes = extract_body_bytes(prepared)?;
    run_is_feed_range_subset_operation_async(py, body_bytes, "is_feed_range_subset")
}

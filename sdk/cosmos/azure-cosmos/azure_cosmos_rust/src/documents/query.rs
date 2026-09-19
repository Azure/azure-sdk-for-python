// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;

/// Execute one query page through the shared driver's one-shot compatibility path.
/// Public retained-cursor iteration uses `wire/item_feed.rs` instead.
///
/// The query JSON is in `PreparedRequest.body_bytes`.
/// `PreparedRequest.partition_key` selects a partition-key-derived range or
/// full-container scope. Returns a feed body
/// (`{"Documents":[...]}`) so the Python query iterator can consume it with the
/// same shape as the legacy path.
#[pyfunction]
pub(crate) fn query_items<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key, modifiers, body_bytes) = extract_query_inputs(prepared)?;
    run_query_operation(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        body_bytes,
        "query_items",
    )
}

/// One-shot `read_all_items`: a supplied partition key selects read-feed;
/// whole-container scope selects `SELECT * FROM root r`. This is separate from
/// the retained-cursor path used for public feed iteration.
#[pyfunction]
pub(crate) fn read_all_items<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key, modifiers) = extract_read_all_inputs(prepared)?;
    run_read_all_items_operation(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        "read_all_items",
    )
}

/// Async twin of `query_items`.
#[pyfunction]
pub(crate) fn query_items_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key, modifiers, body_bytes) = extract_query_inputs(prepared)?;
    run_query_operation_async(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        body_bytes,
        "query_items",
    )
}

/// Async twin of `read_all_items`: identical inputs/driver work; returns a Python
/// awaitable instead of a ready tuple.
#[pyfunction]
pub(crate) fn read_all_items_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key, modifiers) = extract_read_all_inputs(prepared)?;
    run_read_all_items_operation_async(
        py,
        driver_handle,
        &container_link,
        partition_key,
        modifiers,
        "read_all_items",
    )
}

// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Binding functions for stateless item-query page fetching.
//!
//! Each call fetches one page without retaining a feed cursor between calls.
//! Public retained paging uses fetch_page_with_cursor in wire/item_feed.rs.
//! Stateless paging can still reuse a cached CosmosDriver object.

use super::*;

/// Execute one query page through the stateless compatibility path.
/// Public retained paging uses `wire/item_feed.rs` instead.
///
/// The query JSON is in `PreparedRequest.body_bytes`.
/// `PreparedRequest.partition_key` selects a partition-key-derived range or
/// full-container scope. Returns a feed body
/// (`{"Documents":[...]}`) so the Python query iterator can consume it with the
/// same shape as the legacy path.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn query_items<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "query_items")?;
    let (container_link, partition_key, modifiers, body_bytes) = extract_body_inputs(prepared)?;
    run_query_operation(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        &container_link,
        partition_key,
        modifiers,
        body_bytes,
        "query_items",
        timeout_seconds,
    )
}

/// Async twin of `query_items`.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn query_items_async<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "query_items")?;
    let (container_link, partition_key, modifiers, body_bytes) = extract_body_inputs(prepared)?;
    run_query_operation_async(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        &container_link,
        partition_key,
        modifiers,
        body_bytes,
        "query_items",
        timeout_seconds,
    )
}

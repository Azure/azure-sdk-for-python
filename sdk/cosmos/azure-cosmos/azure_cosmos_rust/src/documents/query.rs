// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;

/// Execute one query page through the shared driver.
#[pyfunction]
pub(crate) fn query_items<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers, body_bytes) =
        extract_query_inputs(prepared)?;
    run_query_operation(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        body_bytes,
        "query_items",
    )
}

/// `read_all_items`: a specific partition key uses read-feed; full-container
/// scope uses the legacy-compatible internal query rewrite.
#[pyfunction]
pub(crate) fn read_all_items<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (container_link, partition_key_header, modifiers) = extract_read_all_inputs(prepared)?;
    run_read_all_items_operation(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        "read_all_items",
    )
}

/// Async twin of `query_items`.
#[pyfunction]
pub(crate) fn query_items_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers, body_bytes) =
        extract_query_inputs(prepared)?;
    run_query_operation_async(
        py,
        handle,
        &container_link,
        &partition_key_header,
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
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (container_link, partition_key_header, modifiers) = extract_read_all_inputs(prepared)?;
    run_read_all_items_operation_async(
        py,
        handle,
        &container_link,
        &partition_key_header,
        modifiers,
        "read_all_items",
    )
}

// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;

/// Create an account-level database and return its service response.
#[pyfunction]
pub(crate) fn create_database<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (_container_link, _partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_create_database_operation(py, handle, modifiers, body_bytes, "create_database")
}

/// Async counterpart of [`create_database`].
#[pyfunction]
pub(crate) fn create_database_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (_container_link, _partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_create_database_operation_async(py, handle, modifiers, body_bytes, "create_database_async")
}

#[pyfunction]
/// Return the named database, creating it only when the existence read returns 404.
pub(crate) fn create_database_if_not_exists<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (_container_link, _partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    let database_id = extract_required_item_id(
        prepared,
        "create_database_if_not_exists requires a database id",
    )?;
    run_create_database_if_not_exists_operation(
        py,
        handle,
        modifiers,
        database_id,
        body_bytes,
        "create_database_if_not_exists",
    )
}

#[pyfunction]
/// Async counterpart of [`create_database_if_not_exists`].
pub(crate) fn create_database_if_not_exists_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (_container_link, _partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    let database_id = extract_required_item_id(
        prepared,
        "create_database_if_not_exists_async requires a database id",
    )?;
    run_create_database_if_not_exists_operation_async(
        py,
        handle,
        modifiers,
        database_id,
        body_bytes,
        "create_database_if_not_exists_async",
    )
}

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

/// Read an account-level database and return its service properties.
///
/// The public API this serves is `create_database_if_not_exists`, which first
/// asks whether the database is already there and creates it only if the read
/// comes back not-found. The Rust driver has a create-database call and a
/// read-database call, but no combined get-or-create, so Python does the
/// combining and needs both halves available here.
///
/// Without this the read half had no Rust call to make, and a customer on the
/// Rust backend would have had that one method drop to the older Python
/// transport -- different retry behavior and different diagnostics from every
/// other call on the same client.
#[pyfunction]
pub(crate) fn read_database<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (_container_link, _partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let database_id = extract_required_item_id(prepared, "read_database requires a database id")?;
    run_read_database_operation(py, handle, modifiers, database_id, "read_database")
}

/// Async counterpart of [`read_database`].
#[pyfunction]
pub(crate) fn read_database_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (_container_link, _partition_key_header, modifiers) =
        extract_common_prepared_inputs(prepared)?;
    let database_id = extract_required_item_id(prepared, "read_database requires a database id")?;
    run_read_database_operation_async(py, handle, modifiers, database_id, "read_database_async")
}

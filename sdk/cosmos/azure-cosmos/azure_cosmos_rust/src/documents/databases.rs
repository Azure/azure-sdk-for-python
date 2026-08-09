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
    let modifiers = extract_account_prepared_modifiers(prepared)?;
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
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_create_database_operation_async(py, handle, modifiers, body_bytes, "create_database_async")
}

/// Read an account-level database and return its service properties.
///
/// Two public APIs land here. `DatabaseProxy.read` is the direct one: a customer
/// asks for a database's properties. `create_database_if_not_exists` is the
/// indirect one -- it first asks whether the database is already there and
/// creates it only if this read comes back not-found. The Rust driver has a
/// create-database call and a read-database call, but no combined get-or-create,
/// so Python does the combining and needs both halves available here.
///
/// Without this the read half had no Rust call to make, and a customer on the
/// Rust backend would have had both of those methods drop to the older Python
/// transport -- different retry behavior and different diagnostics from every
/// other call on the same client.
#[pyfunction]
pub(crate) fn read_database<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, "read_database requires a database id")?;
    run_read_database_operation(py, handle, modifiers, database_id, "read_database")
}

/// Async counterpart of [`read_database`].
#[pyfunction]
pub(crate) fn read_database_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, "read_database requires a database id")?;
    run_read_database_operation_async(py, handle, modifiers, database_id, "read_database_async")
}

/// Delete a database and return the service response.
/// A successful delete has status 204 and an empty body.
#[pyfunction]
pub(crate) fn delete_database<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, DELETE_DATABASE_ID_REQUIRED)?;
    run_delete_database_operation(py, handle, modifiers, database_id, "delete_database")
}

/// Return an awaitable that deletes a database.
#[pyfunction]
pub(crate) fn delete_database_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, DELETE_DATABASE_ID_REQUIRED)?;
    run_delete_database_operation_async(py, handle, modifiers, database_id, "delete_database_async")
}

/// Read one page of the account's databases, for `client.list_databases()`.
///
/// This is where a prepared Python request crosses into Rust. It reads the
/// request options off the prepared object and hands them to the wire layer.
/// It uses `extract_account_prepared_modifiers` rather than the extractor the
/// container-scoped operations use, because at account scope there is no
/// container link or partition key to read.
#[pyfunction]
pub(crate) fn list_databases<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    run_list_databases_operation(py, handle, modifiers, "list_databases")
}

/// Async counterpart of [`list_databases`].
#[pyfunction]
pub(crate) fn list_databases_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    run_list_databases_operation_async(py, handle, modifiers, "list_databases_async")
}

/// Run a database query and return one page of matching databases.
#[pyfunction]
pub(crate) fn query_databases<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_query_databases_operation(py, handle, modifiers, body_bytes, "query_databases")
}

/// Return an awaitable that runs one page of a database query.
#[pyfunction]
pub(crate) fn query_databases_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_query_databases_operation_async(py, handle, modifiers, body_bytes, "query_databases_async")
}

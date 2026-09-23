// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Binding calls for database operations, without a container or partition key.
//!
//! For example, a prepared read names database "sales". The binding returns a
//! response tuple; the Python wrapper parses its body into database properties.

use super::*;

/// Create an account-level database and return a binding response tuple.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn create_database<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "create_database")?;
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_create_database_operation(
        py, driver_handle, modifiers, body_bytes, "create_database", timeout_seconds,
    )
}

/// Async counterpart of [`create_database`].
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn create_database_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "create_database")?;
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_create_database_operation_async(
        py, driver_handle, modifiers, body_bytes, "create_database_async", timeout_seconds,
    )
}

/// Read a database and return its properties as body bytes in a response tuple.
/// DatabaseProxy.read uses this directly. The Python wrapper also uses it as
/// the read step of create_database_if_not_exists; this binding call does not
/// make the read/create decision or perform both operations.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn read_database<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "read_database")?;
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, "read_database requires a database id")?;
    run_read_database_operation(py, driver_handle, modifiers, database_id, "read_database", timeout_seconds)
}

/// Async counterpart of [`read_database`].
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn read_database_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "read_database")?;
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, "read_database requires a database id")?;
    run_read_database_operation_async(py, driver_handle, modifiers, database_id, "read_database_async", timeout_seconds)
}

/// Delete a database and return the service response.
/// A successful delete has status 204 and an empty body.
#[pyfunction]
pub(crate) fn delete_database<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "delete_database")?;
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, DELETE_DATABASE_ID_REQUIRED)?;
    run_delete_database_operation(py, driver_handle, modifiers, database_id, "delete_database")
}

/// Return an awaitable that deletes a database.
#[pyfunction]
pub(crate) fn delete_database_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "delete_database")?;
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, DELETE_DATABASE_ID_REQUIRED)?;
    run_delete_database_operation_async(py, driver_handle, modifiers, database_id, "delete_database_async")
}

/// Read one page of the account's databases, for `client.list_databases()`.
///
/// Read settings from PreparedRequest and pass them to the execution helpers.
/// It uses `extract_account_prepared_modifiers` rather than the extractor the
/// container operations use, because at account scope there is no
/// container link or partition key to read.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn list_databases<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "list_databases")?;
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    run_list_databases_operation(py, driver_handle, modifiers, "list_databases", timeout_seconds)
}

/// Async counterpart of [`list_databases`].
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn list_databases_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "list_databases")?;
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    run_list_databases_operation_async(py, driver_handle, modifiers, "list_databases_async", timeout_seconds)
}

/// Run a database query and return one page of matching databases.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn query_databases<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "query_databases")?;
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_query_databases_operation(
        py,
        driver_handle,
        modifiers,
        body_bytes,
        "query_databases",
        timeout_seconds,
    )
}

/// Return an awaitable that runs one page of a database query.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None))]
pub(crate) fn query_databases_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "query_databases")?;
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_query_databases_operation_async(
        py,
        driver_handle,
        modifiers,
        body_bytes,
        "query_databases_async",
        timeout_seconds,
    )
}

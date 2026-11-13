// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Expose Rust driver database operations to the Python wrapper.
//!
//! A customer app reading database "sales" needs its properties from the
//! service backend. The Python wrapper passes the binding a prepared request
//! identifying the read_database operation, database "sales", and applicable
//! operation settings. These binding functions extract the database name and
//! operation settings, then pass them to execution helpers that call the
//! Rust driver.
//!
//! The Rust driver performs the service operation. The binding returns a
//! response tuple containing the body bytes; the Python wrapper parses that
//! body into the database properties returned to the customer app.
//!
//! The synchronous and asynchronous entry points serve the same operation;
//! the asynchronous entry points return Python awaitables.

use super::*;

/// Create an account-level database and return a binding response tuple.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn create_database<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "create_database")?;
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_create_database_operation(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        body_bytes,
        "create_database",
        timeout_seconds,
        include_attempts,
    )
}

/// Async counterpart of [`create_database`].
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn create_database_async<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "create_database")?;
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_create_database_operation_async(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        body_bytes,
        "create_database_async",
        timeout_seconds,
        include_attempts,
    )
}

/// Read a database and return its properties as body bytes in a response tuple.
/// DatabaseProxy.read reaches this entry through DatabaseHelper and BindingAdapter.
/// The Python wrapper also uses it as the read step of
/// create_database_if_not_exists; this binding call does not make the read/create
/// decision or perform both operations.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn read_database<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "read_database")?;
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, "read_database requires a database id")?;
    run_read_database_operation(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        database_id,
        "read_database",
        timeout_seconds,
        include_attempts,
    )
}

/// Async counterpart of [`read_database`].
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn read_database_async<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "read_database")?;
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, "read_database requires a database id")?;
    run_read_database_operation_async(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        database_id,
        "read_database_async",
        timeout_seconds,
        include_attempts,
    )
}

/// Delete a database and return the service response.
/// A successful delete has status 204 and an empty body.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn delete_database<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "delete_database")?;
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, DELETE_DATABASE_ID_REQUIRED)?;
    run_delete_database_operation(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        database_id,
        "delete_database",
        timeout_seconds,
        include_attempts,
    )
}

/// Return an awaitable that deletes a database.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn delete_database_async<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "delete_database")?;
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, DELETE_DATABASE_ID_REQUIRED)?;
    run_delete_database_operation_async(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        database_id,
        "delete_database_async",
        timeout_seconds,
        include_attempts,
    )
}

/// Read one page of the account's databases, for `client.list_databases()`.
///
/// Read settings from PreparedRequest and pass them to the execution helpers.
/// It uses `extract_account_prepared_modifiers` rather than the extractor the
/// container operations use, because at account scope there is no
/// container link or partition key to read.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn list_databases<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "list_databases")?;
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    run_list_databases_operation(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        "list_databases",
        timeout_seconds,
        include_attempts,
    )
}

/// Async counterpart of [`list_databases`].
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn list_databases_async<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "list_databases")?;
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    run_list_databases_operation_async(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        "list_databases_async",
        timeout_seconds,
        include_attempts,
    )
}

/// Run a database query and return one page of matching databases.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn query_databases<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    super::validate_prepared_operation(prepared, "query_databases")?;
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_query_databases_operation(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        body_bytes,
        "query_databases",
        timeout_seconds,
        include_attempts,
    )
}

/// Return an awaitable that runs one page of a database query.
#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn query_databases_async<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'py, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    super::validate_prepared_operation(prepared, "query_databases")?;
    let modifiers = extract_account_prepared_modifiers(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_query_databases_operation_async(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        modifiers,
        body_bytes,
        "query_databases_async",
        timeout_seconds,
        include_attempts,
    )
}

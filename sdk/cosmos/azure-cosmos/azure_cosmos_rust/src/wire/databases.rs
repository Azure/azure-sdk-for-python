// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use std::sync::Arc;

use pyo3::exceptions::PyTimeoutError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{ActivityId, CosmosOperation, CosmosResponse, DatabaseReference, SessionToken},
    options::{ContentResponseOnWrite, OperationOptions},
};

use super::deadline::{parse_remaining_timeout, with_timeout};
use super::driver_runner::{run_driver_operation_async, run_driver_operation_sync};
use super::request::{build_operation_options, RequestHeadersAndOptions};
use super::response::{
    tuple_from_database_feed_result, tuple_from_query_databases_result, tuple_from_result,
};

/// Create a database and convert the response for synchronous Python code.
pub(crate) fn run_create_database_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
    operation_name: &str,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_sync(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            with_timeout(timeout, run_create_database_future(driver, modifiers, body_bytes))
        },
        |py, result| {
            tuple_from_result(py, result.map_err(|error| {
                PyTimeoutError::new_err(format!("Database creation timed out: {error}"))
            })?)
        },
    )
}

/// Create a database and return a Python awaitable.
pub(crate) fn run_create_database_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
    operation_name: &str,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_async(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            with_timeout(timeout, run_create_database_future(driver, modifiers, body_bytes))
        },
        |py, result| {
            tuple_from_result(py, result.map_err(|error| {
                PyTimeoutError::new_err(format!("Database creation timed out: {error}"))
            })?)
        },
    )
}

/// Read a database and convert the response for synchronous Python code.
pub(crate) fn run_read_database_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    operation_name: &str,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_sync(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            with_timeout(timeout, run_read_database_future(driver, modifiers, database_id))
        },
        |py, result| {
            tuple_from_result(py, result.map_err(|error| {
                PyTimeoutError::new_err(format!("Database read timed out: {error}"))
            })?)
        },
    )
}

/// Read a database and return a Python awaitable.
pub(crate) fn run_read_database_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    operation_name: &str,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_async(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            with_timeout(timeout, run_read_database_future(driver, modifiers, database_id))
        },
        |py, result| {
            tuple_from_result(py, result.map_err(|error| {
                PyTimeoutError::new_err(format!("Database read timed out: {error}"))
            })?)
        },
    )
}

/// Delete a database and convert the response for synchronous Python code.
pub(crate) fn run_delete_database_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        driver_handle,
        operation_name,
        move |driver| run_delete_database_future(driver, modifiers, database_id),
        tuple_from_result,
    )
}

/// Delete a database and return a Python awaitable.
pub(crate) fn run_delete_database_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        driver_handle,
        operation_name,
        move |driver| run_delete_database_future(driver, modifiers, database_id),
        tuple_from_result,
    )
}

/// Read one page of databases and convert it for synchronous Python code.
pub(crate) fn run_list_databases_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    operation_name: &str,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_sync(
        py,
        driver_handle,
        operation_name,
        move |driver| with_timeout(timeout, run_list_databases_future(driver, modifiers)),
        |py, result| {
            tuple_from_database_feed_result(py, result.map_err(|error| {
                PyTimeoutError::new_err(format!("Database listing timed out: {error}"))
            })?)
        },
    )
}

/// Async counterpart of [`run_list_databases_operation`]: returns an awaitable
/// instead of blocking, so an async caller's event loop keeps running while the
/// page is in flight.
pub(crate) fn run_list_databases_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    operation_name: &str,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_async(
        py,
        driver_handle,
        operation_name,
        move |driver| with_timeout(timeout, run_list_databases_future(driver, modifiers)),
        |py, result| {
            tuple_from_database_feed_result(py, result.map_err(|error| {
                PyTimeoutError::new_err(format!("Database listing timed out: {error}"))
            })?)
        },
    )
}

/// Run one page of a database query for synchronous Python code.
pub(crate) fn run_query_databases_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        driver_handle,
        operation_name,
        move |driver| run_query_databases_future(driver, modifiers, body_bytes),
        tuple_from_query_databases_result,
    )
}

/// Run one page of a database query and return a Python awaitable.
pub(crate) fn run_query_databases_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        driver_handle,
        operation_name,
        move |driver| run_query_databases_future(driver, modifiers, body_bytes),
        tuple_from_query_databases_result,
    )
}

/// Add request ids and build the driver options for a database operation.
fn prepare_database_operation(
    mut op: CosmosOperation,
    modifiers: RequestHeadersAndOptions,
    content_response: Option<ContentResponseOnWrite>,
) -> (CosmosOperation, OperationOptions) {
    if let Some(activity) = modifiers.activity_header {
        op = op.with_activity_id(ActivityId::from(activity));
    }
    if let Some(session) = modifiers.session_header {
        op = op.with_session_token(SessionToken::from(session));
    }
    let options = build_operation_options(
        content_response,
        modifiers.excluded_regions_value,
        modifiers.end_to_end_timeout,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    (op, options)
}

/// Send a create-database request and return the created database properties.
async fn run_create_database_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
) -> Result<CosmosResponse, CosmosError> {
    let op = CosmosOperation::create_database(driver.account().clone()).with_body(body_bytes);
    let (op, options) =
        prepare_database_operation(op, modifiers, Some(ContentResponseOnWrite::Enabled));
    driver.execute_singleton_operation(op, options).await
}

/// Read a database by name.
async fn run_read_database_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
) -> Result<CosmosResponse, CosmosError> {
    let database = DatabaseReference::from_name(driver.account().clone(), database_id);
    let (op, options) =
        prepare_database_operation(CosmosOperation::read_database(database), modifiers, None);
    driver.execute_singleton_operation(op, options).await
}

/// Delete a database by name.
async fn run_delete_database_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
) -> Result<CosmosResponse, CosmosError> {
    let database = DatabaseReference::from_name(driver.account().clone(), database_id);
    let (op, options) =
        prepare_database_operation(CosmosOperation::delete_database(database), modifiers, None);
    driver.execute_singleton_operation(op, options).await
}

/// Execute one page of a database feed.
/// `None` means the feed has no page to return.
async fn run_database_feed_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    op: CosmosOperation,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let (op, options) = prepare_database_operation(op, modifiers, None);
    driver.execute_operation(op, options).await
}

/// Read one page of all databases in the account.
async fn run_list_databases_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let op = CosmosOperation::read_all_databases(driver.account().clone());
    run_database_feed_future(driver, modifiers, op).await
}

/// Return one page of databases that match the query body.
async fn run_query_databases_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let op = CosmosOperation::query_databases(driver.account().clone()).with_body(body_bytes);
    run_database_feed_future(driver, modifiers, op).await
}

// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Runs container create, read, list, and query operations.

use std::sync::Arc;

use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{ActivityId, CosmosOperation, CosmosResponse, DatabaseReference, SessionToken},
    options::{ContentResponseOnWrite, OperationOptions},
};

use super::driver_runner::{run_driver_operation_async, run_driver_operation_sync};
use super::request::{build_operation_options, OpModifiers};
use super::response::{
    tuple_from_container_feed_result, tuple_from_query_containers_result, tuple_from_result,
};

/// Create a container and convert the response for synchronous Python code.
pub(crate) fn run_create_container_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        handle,
        operation_name,
        move |driver| run_create_container_future(driver, modifiers, database_id, body_bytes),
        tuple_from_result,
    )
}

/// Create a container and return a Python awaitable.
pub(crate) fn run_create_container_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        handle,
        operation_name,
        move |driver| run_create_container_future(driver, modifiers, database_id, body_bytes),
        tuple_from_result,
    )
}

/// Read a container and convert the response for synchronous Python code.
pub(crate) fn run_read_container_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    container_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        handle,
        operation_name,
        move |driver| run_read_container_future(driver, modifiers, database_id, container_id),
        tuple_from_result,
    )
}

/// Read a container and return a Python awaitable.
pub(crate) fn run_read_container_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    container_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        handle,
        operation_name,
        move |driver| run_read_container_future(driver, modifiers, database_id, container_id),
        tuple_from_result,
    )
}

/// Read one page of containers and convert it for synchronous Python code.
pub(crate) fn run_list_containers_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        handle,
        operation_name,
        move |driver| run_list_containers_future(driver, modifiers, database_id),
        tuple_from_container_feed_result,
    )
}

/// Read one page of containers and return a Python awaitable.
pub(crate) fn run_list_containers_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        handle,
        operation_name,
        move |driver| run_list_containers_future(driver, modifiers, database_id),
        tuple_from_container_feed_result,
    )
}

/// Run one page of a container query for synchronous Python code.
pub(crate) fn run_query_containers_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        handle,
        operation_name,
        move |driver| run_query_containers_future(driver, modifiers, database_id, body_bytes),
        tuple_from_query_containers_result,
    )
}

/// Run one page of a container query and return a Python awaitable.
pub(crate) fn run_query_containers_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        handle,
        operation_name,
        move |driver| run_query_containers_future(driver, modifiers, database_id, body_bytes),
        tuple_from_query_containers_result,
    )
}

/// Add request ids and build the driver options for a container operation.
fn prepare_container_operation(
    mut op: CosmosOperation,
    modifiers: OpModifiers,
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

/// Send a create-container request and return the created container properties.
async fn run_create_container_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
) -> Result<CosmosResponse, CosmosError> {
    let database = DatabaseReference::from_name(driver.account().clone(), database_id);
    let op = CosmosOperation::create_container(database).with_body(body_bytes);
    let (op, options) =
        prepare_container_operation(op, modifiers, Some(ContentResponseOnWrite::Enabled));
    driver.execute_singleton_operation(op, options).await
}

/// Read a container directly by database and container name.
async fn run_read_container_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    database_id: String,
    container_id: String,
) -> Result<CosmosResponse, CosmosError> {
    let database = DatabaseReference::from_name(driver.account().clone(), database_id);
    let op = CosmosOperation::read_container_by_name(database, container_id);
    let (op, options) = prepare_container_operation(op, modifiers, None);
    driver.execute_singleton_operation(op, options).await
}

/// Execute one page of a container feed.
/// `None` means the feed has no page to return.
async fn run_container_feed_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    op: CosmosOperation,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let (op, options) = prepare_container_operation(op, modifiers, None);
    driver.execute_operation(op, options).await
}

/// Read one page of all containers in a database.
async fn run_list_containers_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    database_id: String,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let database = DatabaseReference::from_name(driver.account().clone(), database_id);
    let op = CosmosOperation::read_all_containers(database);
    run_container_feed_future(driver, modifiers, op).await
}

/// Return one page of containers that match the query body.
async fn run_query_containers_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let database = DatabaseReference::from_name(driver.account().clone(), database_id);
    let op = CosmosOperation::query_containers(database).with_body(body_bytes);
    run_container_feed_future(driver, modifiers, op).await
}

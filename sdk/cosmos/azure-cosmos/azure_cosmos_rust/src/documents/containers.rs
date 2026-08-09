// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use pyo3::prelude::*;
use pyo3::types::PyTuple;

use crate::wire::{
    extract_body_bytes, extract_container_feed_prepared_inputs,
    extract_container_point_prepared_inputs, extract_database_prepared_inputs,
    resolve_container_metadata as run_resolve_container_metadata,
    resolve_container_metadata_async as run_resolve_container_metadata_async,
    run_create_container_operation, run_create_container_operation_async,
    run_list_containers_operation, run_list_containers_operation_async,
    run_query_containers_operation, run_query_containers_operation_async,
    run_read_container_operation, run_read_container_operation_async,
};

const CREATE_CONTAINER_DATABASE_REQUIRED: &str =
    "create_container: PreparedRequest.item_id is required (the id of the database to create the container in)";

/// Resolve a container name to its resource id and partition key definition.
#[pyfunction]
pub(crate) fn resolve_container_metadata<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_resolve_container_metadata(py, handle, container_link)
}

/// Return an awaitable that resolves a container's metadata.
#[pyfunction]
pub(crate) fn resolve_container_metadata_async<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_resolve_container_metadata_async(py, handle, container_link)
}

/// Create a container from the definition prepared by Python.
/// The returned tuple contains the service response used by `DatabaseProxy.create_container`.
#[pyfunction]
pub(crate) fn create_container<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, CREATE_CONTAINER_DATABASE_REQUIRED)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_create_container_operation(
        py,
        handle,
        modifiers,
        database_id,
        body_bytes,
        "create_container",
    )
}

/// Return an awaitable that creates a container.
#[pyfunction]
pub(crate) fn create_container_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (database_id, modifiers) =
        extract_database_prepared_inputs(prepared, CREATE_CONTAINER_DATABASE_REQUIRED)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_create_container_operation_async(
        py,
        handle,
        modifiers,
        database_id,
        body_bytes,
        "create_container_async",
    )
}

/// Read a container's properties by database and container name.
#[pyfunction]
pub(crate) fn read_container<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (database_id, container_id, modifiers) = extract_container_point_prepared_inputs(prepared)?;
    run_read_container_operation(
        py,
        handle,
        modifiers,
        database_id,
        container_id,
        "read_container",
    )
}

/// Return an awaitable that reads a container's properties.
#[pyfunction]
pub(crate) fn read_container_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (database_id, container_id, modifiers) = extract_container_point_prepared_inputs(prepared)?;
    run_read_container_operation_async(
        py,
        handle,
        modifiers,
        database_id,
        container_id,
        "read_container_async",
    )
}

/// Read one page of containers in a database.
#[pyfunction]
pub(crate) fn list_containers<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (database_id, modifiers) = extract_container_feed_prepared_inputs(prepared)?;
    run_list_containers_operation(py, handle, modifiers, database_id, "list_containers")
}

/// Return an awaitable that reads one page of containers.
#[pyfunction]
pub(crate) fn list_containers_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (database_id, modifiers) = extract_container_feed_prepared_inputs(prepared)?;
    run_list_containers_operation_async(py, handle, modifiers, database_id, "list_containers_async")
}

/// Run a container query and return one page of matching containers.
#[pyfunction]
pub(crate) fn query_containers<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (database_id, modifiers) = extract_container_feed_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_query_containers_operation(
        py,
        handle,
        modifiers,
        database_id,
        body_bytes,
        "query_containers",
    )
}

/// Return an awaitable that runs one page of a container query.
#[pyfunction]
pub(crate) fn query_containers_async<'py>(
    py: Python<'py>,
    handle: &str,
    prepared: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let (database_id, modifiers) = extract_container_feed_prepared_inputs(prepared)?;
    let body_bytes = extract_body_bytes(prepared)?;
    run_query_containers_operation_async(
        py,
        handle,
        modifiers,
        database_id,
        body_bytes,
        "query_containers_async",
    )
}

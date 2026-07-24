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

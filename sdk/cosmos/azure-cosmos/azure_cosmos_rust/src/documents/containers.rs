// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use pyo3::prelude::*;
use pyo3::types::PyTuple;

use crate::wire::{
    resolve_container_metadata as run_resolve_container_metadata,
    resolve_container_metadata_async as run_resolve_container_metadata_async,
};

#[pyfunction]
pub(crate) fn resolve_container_metadata<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_resolve_container_metadata(py, handle, container_link)
}

#[pyfunction]
pub(crate) fn resolve_container_metadata_async<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_resolve_container_metadata_async(py, handle, container_link)
}

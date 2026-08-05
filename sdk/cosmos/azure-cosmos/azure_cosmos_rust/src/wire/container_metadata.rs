// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use super::request::parse_container_link;
use super::response::tuple_from_container_metadata_result;
use super::{lookup_driver, AbortOnDrop};
use crate::runtime::require_runtime_context;

pub(crate) fn resolve_container_metadata<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    let driver = lookup_driver(handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let runtime_ctx = require_runtime_context("resolve_container_metadata")?;
    let result = py.allow_threads(|| {
        runtime_ctx
            .tokio_rt
            .block_on(driver.resolve_container(&database_name, &container_name))
    });
    tuple_from_container_metadata_result(py, result)
}

pub(crate) fn resolve_container_metadata_async<'py>(
    py: Python<'py>,
    handle: &str,
    container_link: &str,
) -> PyResult<Bound<'py, PyAny>> {
    let driver = lookup_driver(handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let runtime_ctx = require_runtime_context("resolve_container_metadata_async")?;
    let join = runtime_ctx.tokio_rt.spawn(async move {
        driver
            .resolve_container(&database_name, &container_name)
            .await
    });
    let abort_guard = AbortOnDrop(join.abort_handle());

    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let result = join.await.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err(
                    "container metadata resolution was cancelled before it completed",
                )
            } else {
                PyRuntimeError::new_err(format!(
                    "container metadata resolution task failed: {join_error}"
                ))
            }
        })?;
        Python::with_gil(|py| {
            tuple_from_container_metadata_result(py, result).map(|tuple| tuple.into_any().unbind())
        })
    })
}

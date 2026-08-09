// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Runs driver operations for synchronous and asynchronous Python calls.

use std::future::Future;
use std::sync::atomic::Ordering;
use std::sync::Arc;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::driver::CosmosDriver;

use super::diagnostics::BINDING_OP_COUNT;
use super::{lookup_driver, AbortOnDrop};
use crate::runtime::require_runtime_context;

/// Converts a driver result into the response tuple returned to Python.
pub(super) type ResponseTupleConverter<R> =
    for<'py> fn(Python<'py>, R) -> PyResult<Bound<'py, PyTuple>>;

/// Run an operation on the shared runtime and return its response tuple.
/// The function releases the Python lock while it waits.
pub(super) fn run_driver_operation_sync<'py, R, F, Fut>(
    py: Python<'py>,
    handle: &str,
    operation_name: &str,
    operation_future_factory: F,
    convert_response: ResponseTupleConverter<R>,
) -> PyResult<Bound<'py, PyTuple>>
where
    F: FnOnce(Arc<CosmosDriver>) -> Fut + Send,
    Fut: Future<Output = R>,
    R: Send,
{
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let runtime_ctx = require_runtime_context(operation_name)?;
    let response_result = py.allow_threads(|| {
        runtime_ctx
            .tokio_rt
            .block_on(operation_future_factory(driver))
    });
    convert_response(py, response_result)
}

/// Start an operation on the shared runtime and return a Python awaitable.
/// Dropping the awaitable cancels the spawned task.
pub(super) fn run_driver_operation_async<'py, R, F, Fut>(
    py: Python<'py>,
    handle: &str,
    operation_name: &str,
    operation_future_factory: F,
    convert_response: ResponseTupleConverter<R>,
) -> PyResult<Bound<'py, PyAny>>
where
    F: FnOnce(Arc<CosmosDriver>) -> Fut + Send + 'static,
    Fut: Future<Output = R> + Send + 'static,
    R: Send + 'static,
{
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let runtime_ctx = require_runtime_context(operation_name)?;
    let join = runtime_ctx.tokio_rt.spawn(operation_future_factory(driver));
    let abort_guard = AbortOnDrop(join.abort_handle());
    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let response_result = join.await.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err("cosmos async operation was cancelled before it completed")
            } else {
                PyRuntimeError::new_err(format!("cosmos async operation task failed: {join_error}"))
            }
        })?;
        Python::with_gil(|py| {
            convert_response(py, response_result).map(|tuple| tuple.into_any().unbind())
        })
    })
}

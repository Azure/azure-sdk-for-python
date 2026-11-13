// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

#[cfg(test)]
pub(crate) fn run_handoff_observed<'py, R, F, Fut>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    prepare: F,
    convert_response: ResponseTupleConverter<R>,
    slot: usize,
) -> PyResult<Bound<'py, PyAny>>
where
    F: FnOnce(Arc<CosmosDriver>) -> PyResult<Fut>,
    Fut: Future<Output = R> + Send + 'static,
    R: Send + 'static,
{
    use crate::handoff_experiment::mark;
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = driver_handle.driver();
    let future = prepare(driver)?;
    let runtime_ctx = require_runtime_context("handoff_experiment")?;
    let join = runtime_ctx.tokio_rt.spawn(async move {
        let result = future.await;
        mark(slot, 0);
        result
    });
    let abort_guard = AbortOnDrop(join.abort_handle());
    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let joined = join.await;
        mark(slot, 1);
        let response_result = joined.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err("cosmos async operation was cancelled before it completed")
            } else {
                PyRuntimeError::new_err(format!("cosmos async operation task failed: {join_error}"))
            }
        })?;
        mark(slot, 2);
        Python::with_gil(|py| {
            mark(slot, 3);
            let result =
                convert_response(py, response_result).map(|tuple| tuple.into_any().unbind());
            mark(slot, 4);
            result
        })
    })
}

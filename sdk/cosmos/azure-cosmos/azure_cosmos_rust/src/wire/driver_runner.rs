// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Share driver-reference retention, waiting, and result conversion across binding calls.
//!
//! For example, an item read retains the CosmosDriver owned by its driver handle.
//! The sync path waits on the calling thread with Python's global interpreter
//! lock (GIL) released. The async path schedules work on the Tokio runtime and
//! returns a Python awaitable. Both convert the result with the GIL held.

use std::future::Future;
#[cfg(any(test, feature = "test-probes"))]
use std::sync::atomic::Ordering;
use std::sync::Arc;
use std::time::Duration;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::driver::CosmosDriver;

#[cfg(any(test, feature = "test-probes"))]
use super::diagnostics::BINDING_OP_COUNT;
use super::errors::{catch_operation_panic, operation_join_error};
use super::AbortOnDrop;
use crate::runtime::require_runtime_context;

/// Convert a Rust driver result into the binding response tuple returned to Python.
pub(super) type ResponseTupleConverter<R> =
    for<'py> fn(Python<'py>, R) -> PyResult<Bound<'py, PyTuple>>;

/// Let Ctrl+C interrupt a synchronous wait without restarting the operation.
/// A raising signal handler drops this future, not work already sent to the service.
/// Only Python's main thread handles signals; blocking Rust code cannot be preempted.
pub(super) fn block_on_with_signals<F>(
    py: Python<'_>,
    runtime: &tokio::runtime::Runtime,
    future: F,
) -> PyResult<F::Output>
where
    F: Future + Send,
    F::Output: Send,
{
    let mut future = std::pin::pin!(future);
    loop {
        py.check_signals()?;
        let result = py.allow_threads(|| {
            runtime.block_on(async {
                // Borrow the same pinned future: only the wait slice expires.
                tokio::time::timeout(Duration::from_millis(100), future.as_mut()).await
            })
        });
        py.check_signals()?;
        if let Ok(result) = result {
            return Ok(result);
        }
    }
}

/// Run an operation on the Tokio runtime and return its binding response tuple.
/// Release the GIL while waiting; this still blocks the calling thread.
pub(super) fn run_driver_operation_sync<'py, R, F, Fut>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    operation_name: &str,
    operation_future_factory: F,
    convert_response: ResponseTupleConverter<R>,
) -> PyResult<Bound<'py, PyTuple>>
where
    F: FnOnce(Arc<CosmosDriver>) -> Fut + Send,
    Fut: Future<Output = R> + Send,
    R: Send,
{
    run_prepared_driver_operation_sync(
        py,
        driver_handle,
        operation_name,
        move |driver| Ok(operation_future_factory(driver)),
        convert_response,
    )
}

/// Retain the handle's driver before preparation, preserving synchronous validation errors.
pub(super) fn run_prepared_driver_operation_sync<'py, R, F, Fut>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    operation_name: &str,
    prepare: F,
    convert_response: ResponseTupleConverter<R>,
) -> PyResult<Bound<'py, PyTuple>>
where
    F: FnOnce(Arc<CosmosDriver>) -> PyResult<Fut>,
    Fut: Future<Output = R> + Send,
    R: Send,
{
    catch_operation_panic(|| {
        #[cfg(any(test, feature = "test-probes"))]
        BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
        let driver = driver_handle.driver();
        let future = prepare(driver)?;
        let runtime_ctx = require_runtime_context(operation_name)?;
        let response_result = block_on_with_signals(py, runtime_ctx.tokio_rt, future)?;
        convert_response(py, response_result)
    })
}

/// Start an operation on the Tokio runtime and return a Python awaitable.
/// The Rust bridge future owns a guard that requests task cancellation when
/// dropped. Merely discarding a Python reference is not a cancellation contract.
pub(super) fn run_driver_operation_async<'py, R, F, Fut>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    operation_name: &str,
    operation_future_factory: F,
    convert_response: ResponseTupleConverter<R>,
) -> PyResult<Bound<'py, PyAny>>
where
    F: FnOnce(Arc<CosmosDriver>) -> Fut + Send + 'static,
    Fut: Future<Output = R> + Send + 'static,
    R: Send + 'static,
{
    run_prepared_driver_operation_async(
        py,
        driver_handle,
        operation_name,
        move |driver| Ok(operation_future_factory(driver)),
        convert_response,
    )
}

/// Preparation errors are raised before returning the awaitable, not on await.
pub(super) fn run_prepared_driver_operation_async<'py, R, F, Fut>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    operation_name: &str,
    prepare: F,
    convert_response: ResponseTupleConverter<R>,
) -> PyResult<Bound<'py, PyAny>>
where
    F: FnOnce(Arc<CosmosDriver>) -> PyResult<Fut>,
    Fut: Future<Output = R> + Send + 'static,
    R: Send + 'static,
{
    #[cfg(any(test, feature = "test-probes"))]
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = driver_handle.driver();
    let future = catch_operation_panic(|| prepare(driver))?;
    let runtime_ctx = require_runtime_context(operation_name)?;
    let join = runtime_ctx.tokio_rt.spawn(future);
    let abort_guard = AbortOnDrop(join.abort_handle());
    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let response_result = join.await.map_err(|join_error| {
            operation_join_error(join_error, |join_error| {
                if join_error.is_cancelled() {
                    PyRuntimeError::new_err(
                        "cosmos async operation was cancelled before it completed",
                    )
                } else {
                    PyRuntimeError::new_err(format!(
                        "cosmos async operation task failed: {join_error}"
                    ))
                }
            })
        })?;
        Python::with_gil(|py| {
            catch_operation_panic(|| convert_response(py, response_result))
                .map(|tuple| tuple.into_any().unbind())
        })
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::driver_runtime::RuntimeHandle;
    use crate::runtime::{acquire_driver_handle, runtime_context};
    use azure_data_cosmos_driver::in_memory_emulator::{
        InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion,
    };
    use pyo3::exceptions::PyValueError;
    use url::Url;

    #[test]
    fn signal_wait_keeps_one_future_and_its_original_deadline() {
        crate::test_support::prepare_python();
        Python::with_gil(|py| {
            let runtime = runtime_context().tokio_rt;
            let starts = std::sync::atomic::AtomicUsize::new(0);
            let value = block_on_with_signals(py, runtime, async {
                starts.fetch_add(1, Ordering::SeqCst);
                tokio::time::sleep(Duration::from_millis(250)).await;
                7
            })
            .unwrap();
            assert_eq!(value, 7);
            assert_eq!(starts.load(Ordering::SeqCst), 1);

            let started = std::time::Instant::now();
            let result = block_on_with_signals(
                py,
                runtime,
                super::super::deadline::with_operation_timeout(
                    Some(Duration::from_millis(250)),
                    std::future::pending::<()>(),
                ),
            )
            .unwrap();
            assert!(result
                .unwrap_err()
                .is_instance_of::<pyo3::exceptions::PyTimeoutError>(py));
            assert!(started.elapsed() < Duration::from_secs(2));
        });
    }

    fn prepare(phase: String) -> PyResult<impl Future<Output = u32> + Send> {
        if phase == "prepare" {
            panic!("injected operation panic");
        }
        if phase == "validation" {
            return Err(PyValueError::new_err("ordinary validation error"));
        }
        Ok(async move {
            if phase == "execute" {
                panic!("injected operation panic");
            }
            7
        })
    }

    fn response(py: Python<'_>, value: u32) -> PyResult<Bound<'_, PyTuple>> {
        Ok(PyTuple::new_bound(py, [value]))
    }

    fn panicking_response(_py: Python<'_>, _value: u32) -> PyResult<Bound<'_, PyTuple>> {
        panic!("injected operation panic");
    }

    #[pyfunction]
    fn sync_call<'py>(
        py: Python<'py>,
        handle: &crate::runtime::DriverHandle,
        phase: String,
    ) -> PyResult<Bound<'py, PyTuple>> {
        let convert = if phase == "convert" {
            panicking_response
        } else {
            response
        };
        run_prepared_driver_operation_sync(
            py,
            handle,
            "panic parity test",
            move |_| prepare(phase),
            convert,
        )
    }

    #[pyfunction]
    fn async_call<'py>(
        py: Python<'py>,
        handle: &crate::runtime::DriverHandle,
        phase: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let convert = if phase == "convert" {
            panicking_response
        } else {
            response
        };
        run_prepared_driver_operation_async(
            py,
            handle,
            "panic parity test",
            move |_| prepare(phase),
            convert,
        )
    }

    #[test]
    fn operation_panics_are_catchable_and_match_across_sync_and_async() {
        crate::test_support::prepare_python();
        let endpoint = Url::parse("https://panic-parity.emulator.local").unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", endpoint.clone())])
                .unwrap(),
        ));
        let runtime = runtime_context()
            .tokio_rt
            .block_on(emulator.runtime_builder().build())
            .unwrap();
        Python::with_gil(|py| {
            let runtime = Py::new(py, RuntimeHandle::new(runtime)).unwrap();
            let handle = Py::new(
                py,
                acquire_driver_handle(
                    py,
                    endpoint.as_str(),
                    Some("ZW11bGF0b3Ita2V5"),
                    None,
                    None,
                    Some(runtime.borrow(py)),
                )
                .unwrap(),
            )
            .unwrap();
            let exports = PyModule::new_bound(py, "panic_parity_exports").unwrap();
            exports
                .add_function(wrap_pyfunction!(sync_call, &exports).unwrap())
                .unwrap();
            exports
                .add_function(wrap_pyfunction!(async_call, &exports).unwrap())
                .unwrap();
            let helper = PyModule::from_code_bound(
                py,
                r#"
import asyncio

async def await_call(function, handle, phase):
    return await function(handle, phase)

def invoke(function, handle, phase, asynchronous):
    try:
        result = (asyncio.run(await_call(function, handle, phase)) if asynchronous
                  else function(handle, phase))
        assert result == (7,)
        return ("success", True, "")
    except BaseException as error:
        return (type(error).__name__, isinstance(error, Exception), str(error))
"#,
                "panic_parity_test.py",
                "panic_parity_test",
            )
            .unwrap();
            for phase in ["prepare", "execute", "convert", "validation", "success"] {
                let expected = match phase {
                    "validation" => ("ValueError", true, "ordinary validation error"),
                    "success" => ("success", true, ""),
                    _ => (
                        "RuntimeError",
                        true,
                        "Rust operation panicked: injected operation panic",
                    ),
                };
                for asynchronous in [false, true] {
                    let result: (String, bool, String) = helper
                        .getattr("invoke")
                        .unwrap()
                        .call1((
                            exports
                                .getattr(if asynchronous {
                                    "async_call"
                                } else {
                                    "sync_call"
                                })
                                .unwrap(),
                            &handle,
                            phase,
                            asynchronous,
                        ))
                        .unwrap()
                        .extract()
                        .unwrap();
                    assert_eq!(
                        (result.0.as_str(), result.1, result.2.as_str()),
                        expected,
                        "phase={phase}, asynchronous={asynchronous}",
                    );
                }
            }
        });
    }
}

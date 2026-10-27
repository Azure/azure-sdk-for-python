// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Own explicit driver runtimes and the lazily initialized default singleton.
//! Python runtime objects and acquired drivers retain independent references.
//! A failed default initialization leaves the singleton available for retry.

use std::sync::{
    atomic::{AtomicU64, Ordering},
    Arc,
};
use std::time::Duration;

use azure_data_cosmos_driver::{driver::CosmosDriverRuntime, options::ConnectionPoolOptions};
use pyo3::{exceptions::PyValueError, prelude::*};
use tokio::sync::OnceCell;

use crate::runtime::{get_config_opt, runtime_context};

static DEFAULT_RUNTIME: OnceCell<RuntimeHandle> = OnceCell::const_new();
static NEXT_RUNTIME_ID: AtomicU64 = AtomicU64::new(1);

#[pyclass(name = "_CosmosRuntime", module = "azure.cosmos._rust", frozen)]
#[derive(Clone)]
pub(crate) struct RuntimeHandle {
    pub(crate) driver_runtime: Arc<CosmosDriverRuntime>,
    pub(crate) id: u64,
}

impl RuntimeHandle {
    pub(crate) fn new(driver_runtime: Arc<CosmosDriverRuntime>) -> Self {
        Self {
            driver_runtime,
            id: NEXT_RUNTIME_ID.fetch_add(1, Ordering::Relaxed),
        }
    }
}

#[pymethods]
impl RuntimeHandle {
    #[getter]
    fn id(&self) -> u64 {
        self.id
    }

    #[getter]
    fn timeouts(&self) -> (f64, f64, f64) {
        let options = self.driver_runtime.connection_pool();
        (
            options.max_connect_timeout().as_secs_f64(),
            options.max_dataplane_request_timeout().as_secs_f64(),
            options.max_metadata_request_timeout().as_secs_f64(),
        )
    }
}

fn duration(options: &Bound<'_, PyAny>, name: &str) -> PyResult<Option<Duration>> {
    get_config_opt::<f64>(options, name)?
        .map(|seconds| {
            Duration::try_from_secs_f64(seconds).map_err(|_| {
                PyValueError::new_err(format!("{name} must be finite, non-negative seconds"))
            })
        })
        .transpose()
}

fn connection_options(options: Option<&Bound<'_, PyAny>>) -> PyResult<ConnectionPoolOptions> {
    let mut builder = ConnectionPoolOptions::builder();
    if let Some(options) = options {
        if let Some(value) = duration(options, "connection_timeout")? {
            builder = builder.with_max_connect_timeout(value);
        }
        if let Some(value) = duration(options, "data_http_request_timeout")? {
            builder = builder.with_max_dataplane_request_timeout(value);
        }
        if let Some(value) = duration(options, "metadata_http_request_timeout")? {
            builder = builder.with_max_metadata_request_timeout(value);
        }
        if let Some(value) = duration(options, "idle_connection_timeout")? {
            builder = builder.with_idle_connection_timeout(value);
        }
        if let Some(value) = get_config_opt::<usize>(options, "max_idle_connections_per_endpoint")?
        {
            builder = builder.with_max_idle_connections_per_endpoint(value);
        }
        if let Some(value) = get_config_opt::<bool>(options, "proxy_allowed")? {
            builder = builder.with_proxy_allowed(value);
        }
    }
    builder
        .build()
        .map_err(|error| PyValueError::new_err(format!("invalid connection pool options: {error}")))
}

async fn build(options: ConnectionPoolOptions) -> PyResult<RuntimeHandle> {
    let driver_runtime = CosmosDriverRuntime::builder()
        .with_connection_pool(options)
        .build()
        .await
        .map_err(|error| {
            pyo3::exceptions::PyRuntimeError::new_err(format!(
                "driver runtime build failed: {error}"
            ))
        })?;
    Ok(RuntimeHandle::new(driver_runtime))
}

pub(crate) async fn default_runtime() -> PyResult<RuntimeHandle> {
    DEFAULT_RUNTIME
        .get_or_try_init(|| async { build(connection_options(None)?).await })
        .await
        .cloned()
}

pub(crate) fn default_configuration() -> Option<(f64, f64, f64)> {
    DEFAULT_RUNTIME.get().map(RuntimeHandle::timeouts)
}

#[pyfunction(name = "_create_runtime")]
#[pyo3(signature = (options=None))]
pub(crate) fn create_runtime(
    py: Python<'_>,
    options: Option<&Bound<'_, PyAny>>,
) -> PyResult<RuntimeHandle> {
    let options = connection_options(options)?;
    let context = runtime_context();
    py.allow_threads(|| context.tokio_rt.block_on(build(options)))
}

#[pyfunction(name = "_create_runtime_async")]
#[pyo3(signature = (options=None))]
pub(crate) fn create_runtime_async<'py>(
    py: Python<'py>,
    options: Option<&Bound<'_, PyAny>>,
) -> PyResult<Bound<'py, PyAny>> {
    let options = connection_options(options)?;
    runtime_context();
    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let runtime = build(options).await?;
        Python::with_gil(|py| Py::new(py, runtime))
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_is_shared_but_explicit_runtimes_are_distinct() {
        runtime_context().tokio_rt.block_on(async {
            let (first, second) = tokio::join!(default_runtime(), default_runtime());
            let first = first.unwrap();
            let second = second.unwrap();
            assert_eq!(first.id, second.id);
            assert!(Arc::ptr_eq(&first.driver_runtime, &second.driver_runtime));
            let custom = build(connection_options(None).unwrap()).await.unwrap();
            assert_ne!(first.id, custom.id);
            assert!(!Arc::ptr_eq(&first.driver_runtime, &custom.driver_runtime));
        });
    }

    #[tokio::test]
    async fn failed_initialization_does_not_poison_a_singleton() {
        let cell: OnceCell<RuntimeHandle> = OnceCell::const_new();
        let failed = cell
            .get_or_try_init(|| async { Err::<RuntimeHandle, _>("initialization failed") })
            .await;
        assert!(failed.is_err());
        assert!(cell.get().is_none());
        assert!(cell
            .get_or_try_init(|| build(connection_options(None).unwrap()))
            .await
            .is_ok());
    }
}

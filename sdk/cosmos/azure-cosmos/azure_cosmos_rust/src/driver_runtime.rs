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

#[cfg(test)]
static FAIL_NEXT_RUNTIME_BUILD: std::sync::atomic::AtomicBool =
    std::sync::atomic::AtomicBool::new(false);

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
    #[cfg(test)]
    if FAIL_NEXT_RUNTIME_BUILD.swap(false, Ordering::SeqCst) {
        return Err(pyo3::exceptions::PyRuntimeError::new_err(
            "injected runtime build failure",
        ));
    }

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
    fn runtime_preserves_all_explicit_connection_options() {
        crate::test_support::prepare_python();
        Python::with_gil(|py| {
            let module = PyModule::from_code_bound(
                py,
                "from types import SimpleNamespace\n\
                 options = SimpleNamespace(connection_timeout=2, \
                 data_http_request_timeout=8, metadata_http_request_timeout=20)",
                "runtime_options.py",
                "runtime_options",
            )
            .unwrap();
            let options = module.getattr("options").unwrap();
            for (idle_seconds, max_idle, proxy_allowed) in [(600, 17, false), (900, 23, true)] {
                options
                    .setattr("idle_connection_timeout", idle_seconds)
                    .unwrap();
                options
                    .setattr("max_idle_connections_per_endpoint", max_idle)
                    .unwrap();
                options.setattr("proxy_allowed", proxy_allowed).unwrap();

                let runtime = create_runtime(py, Some(&options)).unwrap();
                let pool = runtime.driver_runtime.connection_pool();
                assert_eq!(pool.max_connect_timeout(), Duration::from_secs(2));
                assert_eq!(pool.max_dataplane_request_timeout(), Duration::from_secs(8));
                assert_eq!(pool.max_metadata_request_timeout(), Duration::from_secs(20));
                assert_eq!(
                    pool.idle_connection_timeout(),
                    Some(Duration::from_secs(idle_seconds))
                );
                assert_eq!(pool.max_idle_connections_per_endpoint(), max_idle);
                assert_eq!(pool.proxy_allowed(), proxy_allowed);
            }
        });
    }

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

    #[test]
    fn failed_default_initialization_can_retry() {
        const CHILD_ENV: &str = "AZURE_COSMOS_RUNTIME_RETRY_TEST_CHILD";
        if std::env::var_os(CHILD_ENV).is_none() {
            // Isolate the real singleton and failure injection from other runtime tests.
            let output = std::process::Command::new(std::env::current_exe().unwrap())
                .args([
                    "--exact",
                    "driver_runtime::tests::failed_default_initialization_can_retry",
                    "--nocapture",
                    "--test-threads=1",
                ])
                .env(CHILD_ENV, "1")
                .output()
                .expect("start isolated runtime initialization test");
            let stdout = String::from_utf8_lossy(&output.stdout);
            assert!(
                output.status.success() && stdout.contains("1 passed"),
                "isolated runtime initialization test failed:\n{stdout}\n{}",
                String::from_utf8_lossy(&output.stderr),
            );
            return;
        }

        crate::test_support::prepare_python();
        runtime_context().tokio_rt.block_on(async {
            assert!(default_configuration().is_none());
            FAIL_NEXT_RUNTIME_BUILD.store(true, Ordering::SeqCst);
            let error = default_runtime()
                .await
                .err()
                .expect("runtime build failure must reach the caller");
            Python::with_gil(|py| {
                assert!(error.is_instance_of::<pyo3::exceptions::PyRuntimeError>(py));
                assert_eq!(
                    error.value_bound(py).to_string(),
                    "injected runtime build failure"
                );
            });
            assert!(default_configuration().is_none());

            let recovered = default_runtime().await.unwrap();
            assert_eq!(default_configuration(), Some(recovered.timeouts()));

            FAIL_NEXT_RUNTIME_BUILD.store(true, Ordering::SeqCst);
            let reused = default_runtime().await.unwrap();
            assert_eq!(recovered.id, reused.id);
            assert!(Arc::ptr_eq(
                &recovered.driver_runtime,
                &reused.driver_runtime
            ));
            assert!(
                FAIL_NEXT_RUNTIME_BUILD.swap(false, Ordering::SeqCst),
                "cached runtime must not invoke the builder again"
            );
        });
    }
}

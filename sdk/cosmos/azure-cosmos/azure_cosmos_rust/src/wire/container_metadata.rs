// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use super::deadline::{parse_remaining_timeout, with_operation_timeout};
use super::errors::_DriverResponseError;
use super::request::{build_operation_options, parse_container_link};
use super::response::tuple_from_result;
use super::{lookup_driver, AbortOnDrop};
use crate::runtime::require_runtime_context;
use azure_data_cosmos_driver::options::EndToEndOperationLatencyPolicy;
use azure_data_cosmos_driver::{
    error::CosmosError,
    models::{ContainerReference, PartitionKeyKind},
};

fn metadata_result<'py>(
    py: Python<'py>,
    result: Result<ContainerReference, CosmosError>,
) -> PyResult<Bound<'py, PyTuple>> {
    match result {
        Ok(container) => {
            let definition = container.partition_key_definition();
            let kind = match definition.kind() {
                PartitionKeyKind::Hash => "Hash",
                PartitionKeyKind::MultiHash => "MultiHash",
                PartitionKeyKind::Range => "Range",
                _ => return Err(PyRuntimeError::new_err("Unsupported partition-key kind")),
            };
            let paths = PyTuple::new_bound(py, definition.paths().iter().map(|path| path.as_ref()));
            // The driver does not retain systemKey. None means unknown, not false.
            Ok(PyTuple::new_bound(
                py,
                [
                    container.rid().into_py(py),
                    paths.into_any().unbind(),
                    kind.into_py(py),
                    py.None(),
                ],
            ))
        }
        Err(error) => Err(metadata_error(py, error)),
    }
}

pub(super) fn metadata_error(py: Python<'_>, error: CosmosError) -> PyErr {
    match tuple_from_result(py, Err(error)) {
        Ok(response) => _DriverResponseError::new_err((response.unbind(),)),
        Err(error) => error,
    }
}

/// Resolve a container and return its resource id and partition key definition.
pub(crate) fn get_container_metadata<'py>(
    py: Python<'py>,
    driver_handle: &str,
    container_link: &str,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    let options = build_operation_options(
        None,
        None,
        timeout.map(EndToEndOperationLatencyPolicy::new),
        None,
        Default::default(),
    );
    let driver = lookup_driver(driver_handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let runtime_ctx = require_runtime_context("get_container_metadata")?;
    let result = py.allow_threads(|| {
        runtime_ctx.tokio_rt.block_on(with_operation_timeout(
            timeout,
            driver.resolve_container(&database_name, &container_name, options),
        ))
    })?;
    metadata_result(py, result)
}

/// Return an awaitable that resolves a container's metadata.
pub(crate) fn get_container_metadata_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    container_link: &str,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    let options = build_operation_options(
        None,
        None,
        timeout.map(EndToEndOperationLatencyPolicy::new),
        None,
        Default::default(),
    );
    let driver = lookup_driver(driver_handle)?;
    let (database_name, container_name) = parse_container_link(container_link)?;
    let runtime_ctx = require_runtime_context("get_container_metadata_async")?;
    let operation = async move {
        driver
            .resolve_container(&database_name, &container_name, options)
            .await
    };
    let join = runtime_ctx
        .tokio_rt
        .spawn(with_operation_timeout(timeout, operation));
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
        })??;
        Python::with_gil(|py| metadata_result(py, result).map(|tuple| tuple.into_any().unbind()))
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use azure_core::http::Url;
    use azure_data_cosmos_driver::{
        in_memory_emulator::{
            ContainerConfig, InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion,
        },
        models::{AccountReference, PartitionKeyDefinition},
        options::DriverOptions,
    };
    use std::sync::Arc;

    #[tokio::test]
    async fn metadata_success_is_a_typed_tuple_and_missing_container_is_an_error() {
        pyo3::prepare_freethreaded_python();
        let url = Url::parse("https://metadata.emulator.local").unwrap();
        let config =
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(config));
        emulator.store().create_database("db");
        for (name, definition) in [
            ("hash", r#"{"paths":["/pk"],"kind":"Hash","version":2}"#),
            (
                "single-hpk",
                r#"{"paths":["/pk"],"kind":"MultiHash","version":2}"#,
            ),
            (
                "hpk",
                r#"{"paths":["/tenant","/id"],"kind":"MultiHash","version":2}"#,
            ),
        ] {
            let definition: PartitionKeyDefinition = serde_json::from_str(definition).unwrap();
            emulator.store().create_container_with_config(
                "db",
                name,
                definition,
                ContainerConfig::new()
                    .with_partition_count(1)
                    .build()
                    .unwrap(),
            );
        }
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5"))
                    .build(),
            )
            .await
            .unwrap();
        for (name, paths, kind) in [
            ("hash", vec!["/pk"], "Hash"),
            ("single-hpk", vec!["/pk"], "MultiHash"),
            ("hpk", vec!["/tenant", "/id"], "MultiHash"),
        ] {
            for _ in 0..2 {
                let container = driver
                    .resolve_container("db", name, Default::default())
                    .await
                    .unwrap();
                let rid = container.rid().to_owned();
                Python::with_gil(|py| {
                    let result = metadata_result(py, Ok(container)).unwrap();
                    assert_eq!(result.len(), 4);
                    assert_eq!(
                        result.get_item(0).unwrap().extract::<String>().unwrap(),
                        rid
                    );
                    assert!(result.get_item(1).unwrap().is_instance_of::<PyTuple>());
                    assert_eq!(
                        result
                            .get_item(1)
                            .unwrap()
                            .extract::<Vec<String>>()
                            .unwrap(),
                        paths
                    );
                    assert_eq!(
                        result.get_item(2).unwrap().extract::<String>().unwrap(),
                        kind
                    );
                    assert!(result.get_item(3).unwrap().is_none());
                });
            }
        }
        let missing = driver
            .resolve_container("db", "missing", Default::default())
            .await;
        Python::with_gil(|py| {
            let error = metadata_result(py, missing).unwrap_err();
            assert!(error.is_instance_of::<_DriverResponseError>(py));
            let response = error
                .value_bound(py)
                .getattr("args")
                .unwrap()
                .get_item(0)
                .unwrap();
            assert_eq!(response.len().unwrap(), 5);
            assert_eq!(response.get_item(0).unwrap().extract::<u16>().unwrap(), 404);
            assert!(!response
                .get_item(3)
                .unwrap()
                .extract::<Vec<u8>>()
                .unwrap()
                .is_empty());
        });
    }
}

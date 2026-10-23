// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Execute one atomic batch through the selected driver and its runtime.

use std::sync::Arc;

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{ActivityId, CosmosOperation, CosmosResponse, PartitionKey, SessionToken},
    options::ContentResponseOnWrite,
};
use pyo3::{exceptions::PyValueError, prelude::*, types::PyTuple};

use super::{
    container_metadata::metadata_error,
    deadline::{parse_remaining_timeout, with_operation_timeout},
    driver_runner::{run_driver_operation_async, run_driver_operation_sync},
    request::{
        build_operation_options, extract_body_bytes, extract_common_prepared_inputs,
        parse_container_link, RequestHeadersAndOptions,
    },
    response::{tuple_from_result, tuple_from_result_with_attempts},
};

struct BatchRequest {
    database: String,
    container: String,
    key: PartitionKey,
    body: Vec<u8>,
    modifiers: RequestHeadersAndOptions,
}

impl BatchRequest {
    fn extract(prepared: &Bound<'_, PyAny>, timeout_seconds: Option<f64>) -> PyResult<Self> {
        crate::ffi::validate_prepared_operation(prepared, "execute_item_batch")?;
        let (link, key, mut modifiers) = extract_common_prepared_inputs(prepared)?;
        let (database, container) = parse_container_link(&link)?;
        let key = key
            .into_item_key()?
            .ok_or_else(|| PyValueError::new_err("execute_item_batch requires an explicit partition key"))?;
        modifiers.operation_timeout = parse_remaining_timeout(timeout_seconds)?;
        Ok(Self {
            database,
            container,
            key,
            body: extract_body_bytes(prepared)?,
            modifiers,
        })
    }

    fn execute(
        self,
        driver: Arc<CosmosDriver>,
    ) -> impl std::future::Future<Output = PyResult<Result<CosmosResponse, CosmosError>>> + Send {
        let timeout = self.modifiers.operation_timeout;
        let timed = with_operation_timeout(timeout, async move {
            let resolution = build_operation_options(
                None,
                self.modifiers.excluded_regions_value.clone(),
                self.modifiers.driver_timeout_policy.clone(),
                None,
                Default::default(),
            );
            let container = driver
                .resolve_container(&self.database, &self.container, resolution)
                .await
                .map_err(|error| Python::with_gil(|py| metadata_error(py, error)))?;
            let mut operation = CosmosOperation::batch(container, self.key).with_body(self.body);
            if let Some(activity) = self.modifiers.activity_header {
                operation = operation.with_activity_id(ActivityId::from(activity));
            }
            if let Some(session) = self.modifiers.session_header {
                operation = operation.with_session_token(SessionToken::from(session));
            }
            let options = build_operation_options(
                Some(ContentResponseOnWrite::Enabled),
                self.modifiers.excluded_regions_value,
                self.modifiers.driver_timeout_policy,
                self.modifiers.availability_strategy,
                self.modifiers.custom_headers,
            );
            Ok(driver.execute_singleton_operation(operation, options).await)
        });
        async move { timed.await? }
    }
}

#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn execute_item_batch<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'_, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    let request = BatchRequest::extract(prepared, timeout_seconds)?;
    run_driver_operation_sync(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        "execute_item_batch",
        move |driver| request.execute(driver),
        if include_attempts {
            |py, result| tuple_from_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_result(py, result?)
        },
    )
}

#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn execute_item_batch_async<'py>(
    py: Python<'py>,
    driver_handle: &Bound<'_, PyAny>,
    prepared: &Bound<'_, PyAny>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let request = BatchRequest::extract(prepared, timeout_seconds)?;
    run_driver_operation_async(
        py,
        &*driver_handle.extract::<PyRef<'_, crate::runtime::DriverHandle>>()?,
        "execute_item_batch",
        move |driver| request.execute(driver),
        if include_attempts {
            |py, result| tuple_from_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_result(py, result?)
        },
    )
}

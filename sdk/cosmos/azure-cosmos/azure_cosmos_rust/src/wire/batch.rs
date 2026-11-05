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
    response::{tuple_from_result, with_attempt_diagnostics},
};

#[derive(Clone)]
enum BatchResult {
    ResolutionFailed(CosmosError),
    Executed(Result<CosmosResponse, CosmosError>),
}

fn finish_batch<'py>(
    py: Python<'py>,
    result: BatchResult,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    let diagnostics = if include_attempts {
        match &result {
            BatchResult::ResolutionFailed(error) | BatchResult::Executed(Err(error)) => {
                error.diagnostics()
            }
            BatchResult::Executed(Ok(response)) => Some(response.diagnostics()),
        }
    } else {
        None
    };
    let response = match result {
        BatchResult::ResolutionFailed(error) => Err(metadata_error(py, error)),
        BatchResult::Executed(result) => tuple_from_result(py, result),
    };
    if include_attempts {
        // Successful metadata resolution omits diagnostics, even on a warm client.
        with_attempt_diagnostics(
            py,
            response,
            diagnostics,
            super::response::AttemptCoverage::Incomplete("metadata_diagnostics_unavailable"),
        )
    } else {
        response
    }
}

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
        let key = key.into_item_key()?.ok_or_else(|| {
            PyValueError::new_err("execute_item_batch requires an explicit partition key")
        })?;
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
    ) -> impl std::future::Future<Output = PyResult<BatchResult>> + Send {
        let timeout = self.modifiers.operation_timeout;
        let timed = with_operation_timeout(timeout, async move {
            let resolution = build_operation_options(
                None,
                self.modifiers.excluded_regions_value.clone(),
                self.modifiers.driver_timeout_policy.clone(),
                None,
                Default::default(),
            );
            let container = match driver
                .resolve_container(&self.database, &self.container, resolution)
                .await
            {
                Ok(container) => container,
                Err(error) => return BatchResult::ResolutionFailed(error),
            };
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
            BatchResult::Executed(driver.execute_singleton_operation(operation, options).await)
        });
        timed
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
            |py, result| finish_batch(py, result?, true)
        } else {
            |py, result| finish_batch(py, result?, false)
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
            |py, result| finish_batch(py, result?, true)
        } else {
            |py, result| finish_batch(py, result?, false)
        },
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use azure_core::http::{StatusCode, Url};
    use azure_data_cosmos_driver::{
        error::{status_codes, CosmosStatus},
        in_memory_emulator::{InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion},
        models::{AccountReference, ItemReference, PartitionKeyDefinition},
        options::DriverOptions,
    };

    // Obtain real diagnostics without relying on an external account.
    async fn response_and_metadata_error() -> (CosmosResponse, CosmosError) {
        pyo3::prepare_freethreaded_python();
        let url = Url::parse("https://batch.emulator.local").unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap(),
        ));
        emulator.store().create_database("sales");
        emulator.store().create_container(
            "sales",
            "orders",
            PartitionKeyDefinition::from("/customerId"),
        );
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_account_key(url, "ZW11bGF0b3Ita2V5"))
                    .build(),
            )
            .await
            .unwrap();
        let container = driver
            .resolve_container("sales", "orders", Default::default())
            .await
            .unwrap();
        let response = driver
            .execute_singleton_operation(
                CosmosOperation::create_item(ItemReference::from_name(
                    &container,
                    PartitionKey::from("customer-17"),
                    "order-17",
                ))
                .with_body(br#"{"id":"order-17","customerId":"customer-17"}"#.to_vec()),
                Default::default(),
            )
            .await
            .unwrap();
        let error = driver
            .resolve_container("sales", "missing", Default::default())
            .await
            .unwrap_err();
        (response, error)
    }

    fn assert_incomplete(payload: Bound<'_, PyAny>) {
        assert!(!payload
            .get_item("complete")
            .unwrap()
            .extract::<bool>()
            .unwrap());
        assert!(
            payload
                .get_item("request_count")
                .unwrap()
                .extract::<usize>()
                .unwrap()
                > 0
        );
    }

    #[tokio::test]
    async fn batch_completion_preserves_responses_and_marks_details_incomplete() {
        let (response, _) = response_and_metadata_error().await;
        let diagnostics = response.diagnostics();
        Python::with_gil(|py| {
            let result = BatchResult::Executed(Ok(response));
            let ordinary = finish_batch(py, result.clone(), false).unwrap();
            let traced = finish_batch(py, result, true).unwrap();
            assert!(traced.get_item(0).unwrap().eq(ordinary).unwrap());
            assert_incomplete(traced.get_item(1).unwrap());

            let error = CosmosError::builder()
                .with_status(CosmosStatus::new(StatusCode::BadRequest))
                .with_diagnostics(diagnostics)
                .with_message("request rejected")
                .build();
            let result = BatchResult::Executed(Err(error));
            let ordinary = finish_batch(py, result.clone(), false).unwrap();
            let traced = finish_batch(py, result, true).unwrap();
            assert!(traced.get_item(0).unwrap().eq(ordinary).unwrap());
            assert_incomplete(traced.get_item(1).unwrap());
        });
    }

    #[tokio::test]
    async fn batch_completion_preserves_metadata_transport_and_timeout_errors() {
        let (response, metadata) = response_and_metadata_error().await;
        let diagnostics = response.diagnostics();
        let timeout = CosmosStatus::new(StatusCode::RequestTimeout)
            .with_sub_status(status_codes::substatus::CLIENT_OPERATION_TIMEOUT.value());
        let errors = [
            BatchResult::ResolutionFailed(metadata),
            BatchResult::Executed(Err(CosmosError::builder()
                .with_status(CosmosStatus::new(StatusCode::ServiceUnavailable))
                .with_diagnostics(diagnostics.clone())
                .with_message("transport failed")
                .build())),
            BatchResult::Executed(Err(CosmosError::builder()
                .with_status(timeout)
                .with_diagnostics(diagnostics)
                .with_message("expired")
                .build())),
        ];
        Python::with_gil(|py| {
            for result in errors {
                let ordinary = finish_batch(py, result.clone(), false).unwrap_err();
                let traced = finish_batch(py, result, true).unwrap_err();
                assert!(ordinary.get_type_bound(py).is(&traced.get_type_bound(py)));
                assert!(ordinary
                    .value_bound(py)
                    .getattr("args")
                    .unwrap()
                    .eq(traced.value_bound(py).getattr("args").unwrap())
                    .unwrap());
                assert!(!ordinary
                    .value_bound(py)
                    .hasattr("_cosmos_attempt_payload")
                    .unwrap());
                assert_incomplete(
                    traced
                        .value_bound(py)
                        .getattr("_cosmos_attempt_payload")
                        .unwrap(),
                );
            }
        });
    }
}

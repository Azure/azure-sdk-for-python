// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Runs container create, read, replace, delete, list, and query operations.

use std::future::Future;
use std::sync::Arc;
use std::time::Duration;

use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::{CosmosError, CosmosStatus},
    models::{
        ActivityId, CosmosOperation, CosmosResponse, DatabaseReference, SessionToken, SubStatusCode,
    },
    options::{ContentResponseOnWrite, OperationOptions},
};

use super::driver_runner::{run_driver_operation_async, run_driver_operation_sync};
use super::request::{build_operation_options, OpModifiers};
use super::response::{
    tuple_from_container_feed_result, tuple_from_query_containers_result, tuple_from_result,
};

/// Create a container and convert the response for synchronous Python code.
pub(crate) fn run_create_container_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        handle,
        operation_name,
        move |driver| run_create_container_future(driver, modifiers, database_id, body_bytes),
        tuple_from_result,
    )
}

/// Create a container and return a Python awaitable.
pub(crate) fn run_create_container_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        handle,
        operation_name,
        move |driver| run_create_container_future(driver, modifiers, database_id, body_bytes),
        tuple_from_result,
    )
}

/// Read a container and convert the response for synchronous Python code.
pub(crate) fn run_read_container_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    container_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        handle,
        operation_name,
        move |driver| run_read_container_future(driver, modifiers, database_id, container_id),
        tuple_from_result,
    )
}

/// Read a container and return a Python awaitable.
pub(crate) fn run_read_container_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    container_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        handle,
        operation_name,
        move |driver| run_read_container_future(driver, modifiers, database_id, container_id),
        tuple_from_result,
    )
}

/// Delete a container and convert the response for synchronous Python code.
pub(crate) fn run_delete_container_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    container_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        handle,
        operation_name,
        move |driver| run_delete_container_future(driver, modifiers, database_id, container_id),
        tuple_from_result,
    )
}

/// Delete a container and return a Python awaitable.
pub(crate) fn run_delete_container_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    container_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        handle,
        operation_name,
        move |driver| run_delete_container_future(driver, modifiers, database_id, container_id),
        tuple_from_result,
    )
}

/// Replace a container and convert its response for synchronous Python code.
pub(crate) fn run_replace_container_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    container_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        handle,
        operation_name,
        move |driver| {
            run_replace_container_future(driver, modifiers, database_id, container_id, body_bytes)
        },
        tuple_from_result,
    )
}

/// Replace a container and return a Python awaitable.
pub(crate) fn run_replace_container_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    container_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        handle,
        operation_name,
        move |driver| {
            run_replace_container_future(driver, modifiers, database_id, container_id, body_bytes)
        },
        tuple_from_result,
    )
}

/// Read one page of containers and convert it for synchronous Python code.
pub(crate) fn run_list_containers_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        handle,
        operation_name,
        move |driver| run_list_containers_future(driver, modifiers, database_id),
        tuple_from_container_feed_result,
    )
}

/// Read one page of containers and return a Python awaitable.
pub(crate) fn run_list_containers_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        handle,
        operation_name,
        move |driver| run_list_containers_future(driver, modifiers, database_id),
        tuple_from_container_feed_result,
    )
}

/// Run one page of a container query for synchronous Python code.
pub(crate) fn run_query_containers_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        handle,
        operation_name,
        move |driver| run_query_containers_future(driver, modifiers, database_id, body_bytes),
        tuple_from_query_containers_result,
    )
}

/// Run one page of a container query and return a Python awaitable.
pub(crate) fn run_query_containers_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        handle,
        operation_name,
        move |driver| run_query_containers_future(driver, modifiers, database_id, body_bytes),
        tuple_from_query_containers_result,
    )
}

/// Add request ids and build the driver options for a container operation.
fn prepare_container_operation(
    mut op: CosmosOperation,
    modifiers: OpModifiers,
    content_response: Option<ContentResponseOnWrite>,
) -> (CosmosOperation, OperationOptions) {
    if let Some(activity) = modifiers.activity_header {
        op = op.with_activity_id(ActivityId::from(activity));
    }
    if let Some(session) = modifiers.session_header {
        op = op.with_session_token(SessionToken::from(session));
    }
    let options = build_operation_options(
        content_response,
        modifiers.excluded_regions_value,
        modifiers.end_to_end_timeout,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    (op, options)
}

/// Send a create-container request and return the created container properties.
async fn run_create_container_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
) -> Result<CosmosResponse, CosmosError> {
    let database = DatabaseReference::from_name(driver.account().clone(), database_id);
    let op = CosmosOperation::create_container(database).with_body(body_bytes);
    let (op, options) =
        prepare_container_operation(op, modifiers, Some(ContentResponseOnWrite::Enabled));
    driver.execute_singleton_operation(op, options).await
}

/// Read a container directly by database and container name.
async fn run_read_container_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    database_id: String,
    container_id: String,
) -> Result<CosmosResponse, CosmosError> {
    let database = DatabaseReference::from_name(driver.account().clone(), database_id);
    let op = CosmosOperation::read_container_by_name(database, container_id);
    let (op, options) = prepare_container_operation(op, modifiers, None);
    driver.execute_singleton_operation(op, options).await
}

fn container_resolution_options(modifiers: &OpModifiers) -> OperationOptions {
    // Conditions and customer headers belong to the write, not its metadata GET.
    build_operation_options(
        None,
        modifiers.excluded_regions_value.clone(),
        modifiers.end_to_end_timeout.clone(),
        modifiers.availability_strategy.clone(),
        Default::default(),
    )
}

async fn with_container_timeout<T>(
    timeout: Option<Duration>,
    timeout_message: &'static str,
    operation: impl Future<Output = Result<T, CosmosError>>,
) -> Result<T, CosmosError> {
    let Some(duration) = timeout else {
        return operation.await;
    };
    tokio::time::timeout(duration, operation)
        .await
        .map_err(|error| {
            CosmosError::builder()
                .with_status(
                    CosmosStatus::new(azure_core::http::StatusCode::RequestTimeout)
                        .with_sub_status(SubStatusCode::CLIENT_OPERATION_TIMEOUT.value()),
                )
                .with_message(timeout_message)
                .with_source(error)
                .build()
        })?
}

/// Rust resolves metadata; one explicit timeout covers both lookup and deletion.
async fn run_delete_container_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    database_id: String,
    container_id: String,
) -> Result<CosmosResponse, CosmosError> {
    let timeout = modifiers
        .end_to_end_timeout
        .as_ref()
        .map(|policy| policy.timeout());
    let resolution_options = container_resolution_options(&modifiers);
    with_container_timeout(
        timeout,
        "delete_container timeout exceeded during metadata resolution or deletion",
        async move {
            let container = driver
                .resolve_container(&database_id, &container_id, resolution_options)
                .await?;
            let (op, options) = prepare_container_operation(
                CosmosOperation::delete_container(container),
                modifiers,
                None,
            );
            driver.execute_singleton_operation(op, options).await
        },
    )
    .await
}

/// One timeout covers metadata lookup and PUT; only PUT receives the replacement conditions.
async fn run_replace_container_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    database_id: String,
    container_id: String,
    body_bytes: Vec<u8>,
) -> Result<CosmosResponse, CosmosError> {
    let timeout = modifiers
        .end_to_end_timeout
        .as_ref()
        .map(|policy| policy.timeout());
    let resolution_options = container_resolution_options(&modifiers);
    with_container_timeout(
        timeout,
        "replace_container timeout exceeded during metadata resolution or replacement",
        async move {
            let container = driver
                .resolve_container(&database_id, &container_id, resolution_options)
                .await?;
            let (op, options) = prepare_container_operation(
                CosmosOperation::replace_container(container).with_body(body_bytes),
                modifiers,
                Some(ContentResponseOnWrite::Enabled),
            );
            driver.execute_singleton_operation(op, options).await
        },
    )
    .await
}

/// Execute one page of a container feed.
/// `None` means the feed has no page to return.
async fn run_container_feed_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    op: CosmosOperation,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let (op, options) = prepare_container_operation(op, modifiers, None);
    driver.execute_operation(op, options).await
}

/// Read one page of all containers in a database.
async fn run_list_containers_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    database_id: String,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let database = DatabaseReference::from_name(driver.account().clone(), database_id);
    let op = CosmosOperation::read_all_containers(database);
    run_container_feed_future(driver, modifiers, op).await
}

/// Return one page of containers that match the query body.
async fn run_query_containers_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let database = DatabaseReference::from_name(driver.account().clone(), database_id);
    let op = CosmosOperation::query_containers(database).with_body(body_bytes);
    run_container_feed_future(driver, modifiers, op).await
}

#[cfg(test)]
mod tests {
    use super::*;
    use azure_core::http::headers::{HeaderName, HeaderValue};
    use azure_data_cosmos_driver::options::EndToEndOperationLatencyPolicy;
    use std::sync::atomic::{AtomicBool, Ordering};

    #[test]
    fn resolution_does_not_inherit_write_conditions() {
        let modifiers = OpModifiers {
            activity_header: None,
            session_header: None,
            content_response_on_write: ContentResponseOnWrite::Enabled,
            excluded_regions_value: None,
            end_to_end_timeout: Some(EndToEndOperationLatencyPolicy::new(Duration::from_secs(2))),
            availability_strategy: None,
            custom_headers: [(
                HeaderName::from_static("if-none-match"),
                HeaderValue::from_static("*"),
            )]
            .into_iter()
            .collect(),
        };
        let options = container_resolution_options(&modifiers);
        assert!(options.custom_headers.is_none());
        assert_eq!(
            options.end_to_end_latency_policy.unwrap().timeout(),
            Duration::from_secs(2)
        );
        assert_eq!(modifiers.custom_headers.len(), 1);
    }

    #[tokio::test]
    async fn container_timeout_preserves_success_and_driver_errors() {
        for timeout in [None, Some(Duration::from_secs(1))] {
            assert_eq!(
                with_container_timeout(timeout, "container mutation timed out", async { Ok(42) })
                    .await
                    .unwrap(),
                42
            );
            let error =
                with_container_timeout::<()>(timeout, "container mutation timed out", async {
                    Err(CosmosError::builder()
                        .with_status(CosmosStatus::new(azure_core::http::StatusCode::NotFound))
                        .with_message("missing container")
                        .build())
                })
                .await
                .unwrap_err();
            assert_eq!(
                error.status().status_code(),
                azure_core::http::StatusCode::NotFound
            );
        }
    }

    #[tokio::test]
    async fn container_timeout_drops_the_entire_lookup_and_write_future() {
        struct Dropped(Arc<AtomicBool>);
        impl Drop for Dropped {
            fn drop(&mut self) {
                self.0.store(true, Ordering::SeqCst);
            }
        }
        let dropped = Arc::new(AtomicBool::new(false));
        let marker = Dropped(dropped.clone());
        let error = with_container_timeout(
            Some(Duration::from_millis(1)),
            "container mutation timed out",
            async move {
                let _marker = marker;
                std::future::pending::<Result<(), CosmosError>>().await
            },
        )
        .await
        .unwrap_err();
        assert_eq!(
            error.status().status_code(),
            azure_core::http::StatusCode::RequestTimeout
        );
        assert_eq!(
            error.status().sub_status(),
            Some(SubStatusCode::CLIENT_OPERATION_TIMEOUT)
        );
        assert!(dropped.load(Ordering::SeqCst));
    }
}

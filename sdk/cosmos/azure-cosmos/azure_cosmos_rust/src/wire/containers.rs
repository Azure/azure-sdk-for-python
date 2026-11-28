// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Execute container operations using the Rust driver.
//!
//! For example, a read names database "sales" and container "orders". Replacement
//! and deletion first resolve container metadata; their helpers keep lookup and
//! the final operation within one supplied timeout.

use std::future::Future;
use std::sync::Arc;
use std::time::Duration;

use pyo3::exceptions::PyTimeoutError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{
        ActivityId, CosmosOperation, CosmosResponse, DatabaseReference, ResponseBody, SessionToken,
    },
    options::{ContentResponseOnWrite, OperationOptions},
};

use super::deadline::{
    parse_remaining_timeout, with_deadline, with_operation_timeout, with_timeout,
};
use super::driver_runner::{run_driver_operation_async, run_driver_operation_sync};
use super::request::{build_operation_options, RequestHeadersAndOptions};
use super::response::{
    tuple_from_container_feed_result, tuple_from_container_feed_result_with_attempts,
    tuple_from_query_containers_result, tuple_from_query_containers_result_with_attempts,
    tuple_from_resolved_result_with_attempts, tuple_from_result, tuple_from_result_with_attempts,
};

/// Create a container and convert the response for synchronous Python code.
pub(crate) fn run_create_container_operation<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_sync(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            let timed = with_timeout(
                timeout,
                run_create_container_future(driver, modifiers, database_id, body_bytes),
            );
            async move {
                timed.await.map_err(|error| {
                    PyTimeoutError::new_err(format!("Container creation timed out: {error}"))
                })
            }
        },
        if include_attempts {
            |py, result| tuple_from_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_result(py, result?)
        },
    )
}

/// Create a container and return a Python awaitable.
pub(crate) fn run_create_container_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_async(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            let timed = with_timeout(
                timeout,
                run_create_container_future(driver, modifiers, database_id, body_bytes),
            );
            async move {
                timed.await.map_err(|error| {
                    PyTimeoutError::new_err(format!("Container creation timed out: {error}"))
                })
            }
        },
        if include_attempts {
            |py, result| tuple_from_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_result(py, result?)
        },
    )
}

/// Read a container and convert the response for synchronous Python code.
pub(crate) fn run_read_container_operation<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    container_id: String,
    operation_name: &str,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_sync(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            run_read_container_future(driver, modifiers, database_id, container_id, timeout)
        },
        if include_attempts {
            |py, result| tuple_from_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_result(py, result?)
        },
    )
}

/// Read a container and return a Python awaitable.
pub(crate) fn run_read_container_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    container_id: String,
    operation_name: &str,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_async(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            run_read_container_future(driver, modifiers, database_id, container_id, timeout)
        },
        if include_attempts {
            |py, result| tuple_from_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_result(py, result?)
        },
    )
}

/// Delete a container and convert the response for synchronous Python code.
pub(crate) fn run_delete_container_operation<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    container_id: String,
    operation_name: &str,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        driver_handle,
        operation_name,
        move |driver| run_delete_container_future(driver, modifiers, database_id, container_id),
        if include_attempts {
            |py, result| tuple_from_resolved_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_result(py, result?)
        },
    )
}

/// Delete a container and return a Python awaitable.
pub(crate) fn run_delete_container_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    container_id: String,
    operation_name: &str,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        driver_handle,
        operation_name,
        move |driver| run_delete_container_future(driver, modifiers, database_id, container_id),
        if include_attempts {
            |py, result| tuple_from_resolved_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_result(py, result?)
        },
    )
}

/// Replace a container and convert its response for synchronous Python code.
pub(crate) fn run_replace_container_operation<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    container_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    run_driver_operation_sync(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            run_replace_container_future(driver, modifiers, database_id, container_id, body_bytes)
        },
        if include_attempts {
            |py, result| tuple_from_resolved_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_result(py, result?)
        },
    )
}

/// Replace a container and return a Python awaitable.
pub(crate) fn run_replace_container_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    container_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    run_driver_operation_async(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            run_replace_container_future(driver, modifiers, database_id, container_id, body_bytes)
        },
        if include_attempts {
            |py, result| tuple_from_resolved_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_result(py, result?)
        },
    )
}

/// Read one page of containers and convert it for synchronous Python code.
pub(crate) fn run_list_containers_operation<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    operation_name: &str,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    let timeout = super::deadline::parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_sync(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            super::deadline::with_page_timeout(
                timeout,
                run_list_containers_future(driver, modifiers, database_id),
            )
        },
        if include_attempts {
            |py, result| tuple_from_container_feed_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_container_feed_result(py, result?)
        },
    )
}

/// Read one page of containers and return a Python awaitable.
pub(crate) fn run_list_containers_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    operation_name: &str,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let timeout = super::deadline::parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_async(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            super::deadline::with_page_timeout(
                timeout,
                run_list_containers_future(driver, modifiers, database_id),
            )
        },
        if include_attempts {
            |py, result| tuple_from_container_feed_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_container_feed_result(py, result?)
        },
    )
}

/// Run one page of a container query for synchronous Python code.
pub(crate) fn run_query_containers_operation<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    let timeout = super::deadline::parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_sync(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            super::deadline::with_page_timeout(
                timeout,
                run_query_containers_future(driver, modifiers, database_id, body_bytes),
            )
        },
        if include_attempts {
            |py, result| tuple_from_query_containers_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_query_containers_result(py, result?)
        },
    )
}

/// Run one page of a container query and return a Python awaitable.
pub(crate) fn run_query_containers_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    body_bytes: Vec<u8>,
    operation_name: &str,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let timeout = super::deadline::parse_remaining_timeout(timeout_seconds)?;
    run_driver_operation_async(
        py,
        driver_handle,
        operation_name,
        move |driver| {
            super::deadline::with_page_timeout(
                timeout,
                run_query_containers_future(driver, modifiers, database_id, body_bytes),
            )
        },
        if include_attempts {
            |py, result| tuple_from_query_containers_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_query_containers_result(py, result?)
        },
    )
}

/// Attach the activity id and session token, when supplied, and build container operation options.
fn prepare_container_operation(
    mut op: CosmosOperation,
    modifiers: RequestHeadersAndOptions,
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
        modifiers.configured_driver_timeout_policy,
        modifiers.availability_strategy,
        modifiers.throughput_control,
        modifiers.utf8_decoding_mode,
        modifiers.read_consistency_strategy.filter(|_| op.is_read_only()),
        modifiers.custom_headers,
    );
    (op, options)
}

/// Send a create-container request and return the Rust driver's response.
async fn run_create_container_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
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
///
/// The deadline is recorded now. The read gets the whole budget; the cache refresh
/// gets only the time left, and running out there still returns the read.
fn run_read_container_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    container_id: String,
    timeout: Option<Duration>,
) -> impl Future<Output = PyResult<Result<CosmosResponse, CosmosError>>> {
    let deadline = timeout.map(|duration| tokio::time::Instant::now() + duration);
    async move {
        let resolution_options = container_resolution_options(&modifiers);
        let database = DatabaseReference::from_name(driver.account().clone(), database_id.clone());
        let op = CosmosOperation::read_container_by_name(database, container_id.clone());
        let (op, options) = prepare_container_operation(op, modifiers, None);
        let response =
            match with_deadline(deadline, driver.execute_singleton_operation(op, options)).await {
                Ok(Ok(response)) => response,
                Ok(Err(error)) => return Ok(Err(error)),
                Err(error) => {
                    return Err(PyTimeoutError::new_err(format!(
                        "Container read timed out: {error}"
                    )))
                }
            };
        // Box::pin keeps the cache lookup's large future on the heap, not inside this one.
        let _ = with_deadline(
            deadline,
            Box::pin(refresh_cached_container_if_recreated(
                &driver,
                &database_id,
                &container_id,
                &response,
                resolution_options,
            )),
        )
        .await;
        Ok(Ok(response))
    }
}

/// Update the Rust driver's container cache when `read()` finds a recreated container.
///
/// Example: "orders" was cached with partition key path "/pk", then deleted and
/// recreated with "/id". Legacy `read()` refreshes its cached metadata, so the next
/// write uses "/id". The driver only refreshes after a failed request, so we compare
/// the `_rid` just read with the cached one and refresh only when they differ.
/// The read already succeeded, so a failed refresh is ignored; the driver still
/// recovers on its next stale-cache error.
async fn refresh_cached_container_if_recreated(
    driver: &CosmosDriver,
    database_id: &str,
    container_id: &str,
    response: &CosmosResponse,
    options: OperationOptions,
) {
    #[derive(serde::Deserialize)]
    struct ContainerRid {
        #[serde(rename = "_rid")]
        rid: String,
    }

    let ResponseBody::Bytes(body) = response.body() else {
        return;
    };
    let Ok(read) = serde_json::from_slice::<ContainerRid>(body) else {
        return;
    };
    // Served from the cache when present; a cold cache fetches the current container.
    let Ok(cached) = driver
        .resolve_container_by_name(database_id, container_id, options.clone())
        .await
    else {
        return;
    };
    if cached.rid() != read.rid {
        let _ = driver
            .refresh_container_if_recreated(&cached, options)
            .await;
    }
}

fn container_resolution_options(modifiers: &RequestHeadersAndOptions) -> OperationOptions {
    // Conditions and customer app headers belong to the write, not its metadata GET.
    build_operation_options(
        None,
        modifiers.excluded_regions_value.clone(),
        modifiers.configured_driver_timeout_policy.clone(),
        modifiers.availability_strategy.clone(),
        None,
        modifiers.utf8_decoding_mode,
        None,
        Default::default(),
    )
}

/// Ask the Rust driver to resolve metadata; one timeout covers lookup and deletion.
fn run_delete_container_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    container_id: String,
) -> impl Future<Output = PyResult<Result<CosmosResponse, CosmosError>>> {
    let timeout = container_operation_timeout(&modifiers);
    let resolution_options = container_resolution_options(&modifiers);
    with_operation_timeout(timeout, async move {
        let container = driver
            .resolve_container(&database_id, &container_id, resolution_options)
            .await?;
        let (op, options) = prepare_container_operation(
            CosmosOperation::delete_container(container),
            modifiers,
            None,
        );
        driver.execute_singleton_operation(op, options).await
    })
}

/// One timeout covers metadata lookup and PUT; only PUT receives the replacement conditions.
fn run_replace_container_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
    container_id: String,
    body_bytes: Vec<u8>,
) -> impl Future<Output = PyResult<Result<CosmosResponse, CosmosError>>> {
    let timeout = container_operation_timeout(&modifiers);
    let resolution_options = container_resolution_options(&modifiers);
    with_operation_timeout(timeout, async move {
        let container = driver
            .resolve_container(&database_id, &container_id, resolution_options)
            .await?;
        let (op, options) = prepare_container_operation(
            CosmosOperation::replace_container(container).with_body(body_bytes),
            modifiers,
            Some(ContentResponseOnWrite::Enabled),
        );
        driver.execute_singleton_operation(op, options).await
    })
}

fn container_operation_timeout(modifiers: &RequestHeadersAndOptions) -> Option<Duration> {
    let configured = modifiers
        .configured_driver_timeout_policy
        .as_ref()
        .map(|policy| policy.timeout());
    match (modifiers.remaining_binding_timeout, configured) {
        (Some(remaining), Some(configured)) => Some(remaining.min(configured)),
        (remaining, configured) => remaining.or(configured),
    }
}

/// Execute one page of a container feed.
/// `None` means the feed has no page to return.
async fn run_container_feed_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    op: CosmosOperation,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let (op, options) = prepare_container_operation(op, modifiers, None);
    driver.execute_operation(op, options).await
}

/// Read one page of all containers in a database.
async fn run_list_containers_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    database_id: String,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let database = DatabaseReference::from_name(driver.account().clone(), database_id);
    let op = CosmosOperation::read_all_containers(database);
    run_container_feed_future(driver, modifiers, op).await
}

/// Return one page of containers that match the query body.
async fn run_query_containers_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
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
    use azure_data_cosmos_driver::error::CosmosStatus;
    use azure_data_cosmos_driver::options::EndToEndOperationLatencyPolicy;
    use std::sync::atomic::{AtomicBool, Ordering};

    #[test]
    fn resolution_does_not_inherit_write_conditions() {
        let modifiers = RequestHeadersAndOptions {
            activity_header: None,
            session_header: None,
            content_response_on_write: ContentResponseOnWrite::Enabled,
            excluded_regions_value: None,
            configured_driver_timeout_policy: Some(EndToEndOperationLatencyPolicy::new(
                Duration::from_secs(2),
            )),
            remaining_binding_timeout: None,
            availability_strategy: None,
            read_consistency_strategy: None,
            patch_strategy: None,
            throughput_control: None,
            utf8_decoding_mode: None,
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

    #[test]
    fn container_mutation_uses_remaining_budget_without_rounding_or_extension() {
        let mut modifiers = RequestHeadersAndOptions {
            activity_header: None,
            session_header: None,
            content_response_on_write: ContentResponseOnWrite::Enabled,
            excluded_regions_value: None,
            configured_driver_timeout_policy: None,
            remaining_binding_timeout: None,
            availability_strategy: None,
            read_consistency_strategy: None,
            patch_strategy: None,
            throughput_control: None,
            utf8_decoding_mode: None,
            custom_headers: Default::default(),
        };
        assert_eq!(container_operation_timeout(&modifiers), None);
        modifiers.configured_driver_timeout_policy =
            Some(EndToEndOperationLatencyPolicy::new(Duration::from_secs(2)));
        assert_eq!(
            container_operation_timeout(&modifiers),
            Some(Duration::from_secs(2))
        );
        modifiers.remaining_binding_timeout = Some(Duration::from_millis(125));
        assert_eq!(
            container_operation_timeout(&modifiers),
            Some(Duration::from_millis(125))
        );
        modifiers.remaining_binding_timeout = Some(Duration::from_secs(3));
        assert_eq!(
            container_operation_timeout(&modifiers),
            Some(Duration::from_secs(2))
        );
        modifiers.configured_driver_timeout_policy = None;
        assert_eq!(
            container_operation_timeout(&modifiers),
            Some(Duration::from_secs(3))
        );
    }

    #[tokio::test(start_paused = true)]
    async fn container_scheduling_delay_does_not_restart_the_budget() {
        crate::test_support::prepare_python();
        let polled = AtomicBool::new(false);
        let timed = with_operation_timeout(Some(Duration::from_millis(5)), async {
            polled.store(true, Ordering::SeqCst);
        });
        tokio::time::advance(Duration::from_millis(6)).await;
        let error = timed.await.unwrap_err();
        assert!(!polled.load(Ordering::SeqCst));
        Python::with_gil(|py| assert!(error.is_instance_of::<PyTimeoutError>(py)));
    }

    #[tokio::test]
    async fn container_timeout_preserves_success_and_driver_errors() {
        for timeout in [None, Some(Duration::from_secs(1))] {
            assert_eq!(
                with_operation_timeout(timeout, async { Ok::<_, CosmosError>(42) })
                    .await
                    .unwrap()
                    .unwrap(),
                42
            );
            let error = with_operation_timeout(timeout, async {
                Err::<(), _>(
                    CosmosError::builder()
                        .with_status(CosmosStatus::new(azure_core::http::StatusCode::NotFound))
                        .with_message("missing container")
                        .build(),
                )
            })
            .await
            .unwrap()
            .unwrap_err();
            assert_eq!(
                error.status().status_code(),
                azure_core::http::StatusCode::NotFound
            );
        }
    }

    #[tokio::test]
    async fn container_timeout_drops_the_entire_lookup_and_write_future() {
        crate::test_support::prepare_python();
        struct Dropped(Arc<AtomicBool>);
        impl Drop for Dropped {
            fn drop(&mut self) {
                self.0.store(true, Ordering::SeqCst);
            }
        }
        let dropped = Arc::new(AtomicBool::new(false));
        let marker = Dropped(dropped.clone());
        let error = with_operation_timeout(Some(Duration::from_millis(1)), async move {
            let _marker = marker;
            std::future::pending::<Result<(), CosmosError>>().await
        })
        .await
        .unwrap_err();
        Python::with_gil(|py| assert!(error.is_instance_of::<PyTimeoutError>(py)));
        assert!(dropped.load(Ordering::SeqCst));
    }

    #[tokio::test(start_paused = true)]
    async fn container_mutations_use_shared_timeout_without_rewriting_driver_results() {
        use azure_data_cosmos_driver::{
            fault_injection::{
                FaultInjectionConditionBuilder, FaultInjectionResultBuilder,
                FaultInjectionRuleBuilder, FaultOperationType,
            },
            in_memory_emulator::{InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion},
            models::{AccountReference, PartitionKeyDefinition},
            options::DriverOptions,
        };
        use url::Url;

        crate::test_support::prepare_python();
        for replace in [false, true] {
            for (metadata_ms, missing) in [(1250, false), (5, false), (5, true)] {
                let url = Url::parse("https://container-deadline.emulator.local").unwrap();
                let emulator = Arc::new(InMemoryEmulatorHttpClient::new(
                    VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())])
                        .unwrap(),
                ));
                emulator.store().create_database("db");
                if !missing {
                    emulator.store().create_container(
                        "db",
                        "orders",
                        PartitionKeyDefinition::from("/pk"),
                    );
                }
                let metadata = Arc::new(
                    FaultInjectionRuleBuilder::new(
                        "container-metadata-delay",
                        FaultInjectionResultBuilder::new()
                            .with_delay(Duration::from_millis(metadata_ms))
                            .with_probability(1.0)
                            .build(),
                    )
                    .with_condition(
                        FaultInjectionConditionBuilder::new()
                            .with_operation_type(FaultOperationType::MetadataReadContainer)
                            .build(),
                    )
                    .build(),
                );
                let runtime = emulator
                    .runtime_builder_with_fault_rules(vec![metadata.clone()])
                    .build()
                    .await
                    .unwrap();
                let driver = runtime
                    .create_driver(
                        DriverOptions::builder(AccountReference::with_account_key(
                            url,
                            "ZW11bGF0b3Ita2V5",
                        ))
                        .build(),
                    )
                    .await
                    .unwrap();
                let modifiers = RequestHeadersAndOptions {
                    activity_header: None,
                    session_header: None,
                    content_response_on_write: ContentResponseOnWrite::Enabled,
                    excluded_regions_value: None,
                    configured_driver_timeout_policy: None,
                    remaining_binding_timeout: Some(Duration::from_secs(1)),
                    availability_strategy: None,
                    read_consistency_strategy: None,
                    patch_strategy: None,
                    throughput_control: None,
                    utf8_decoding_mode: None,
                    custom_headers: Default::default(),
                };
                // Each future is about 28 KB; Box::pin keeps it on the heap, not the stack.
                let result = if replace {
                    Box::pin(run_replace_container_future(
                        driver,
                        modifiers,
                        "db".into(),
                        "orders".into(),
                        serde_json::to_vec(&serde_json::json!({
                            "id": "orders",
                            "partitionKey": PartitionKeyDefinition::from("/pk"),
                        }))
                        .unwrap(),
                    ))
                    .await
                } else {
                    Box::pin(run_delete_container_future(
                        driver,
                        modifiers,
                        "db".into(),
                        "orders".into(),
                    ))
                    .await
                };
                if metadata_ms > 1000 {
                    let error = result.unwrap_err();
                    Python::with_gil(|py| assert!(error.is_instance_of::<PyTimeoutError>(py)));
                    assert!(error
                        .to_string()
                        .contains("Operation timed out during metadata resolution or execution"));
                } else if missing {
                    assert_eq!(
                        result.unwrap().unwrap_err().status().status_code(),
                        azure_core::http::StatusCode::NotFound,
                    );
                } else {
                    assert_eq!(
                        u16::from(result.unwrap().unwrap().status().status_code()),
                        if replace { 200 } else { 204 },
                    );
                }
                assert_eq!(metadata.hit_count(), 1);
            }
        }
    }

    #[tokio::test]
    async fn read_container_refreshes_driver_cache_after_recreation() {
        use azure_data_cosmos_driver::{
            in_memory_emulator::{InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion},
            models::{AccountReference, PartitionKeyDefinition},
            options::DriverOptions,
        };
        use url::Url;

        let url = Url::parse("https://container-read-refresh.emulator.local").unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap(),
        ));
        emulator.store().create_database("db");
        emulator
            .store()
            .create_container("db", "orders", PartitionKeyDefinition::from("/pk"));
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_account_key(url, "ZW11bGF0b3Ita2V5"))
                    .build(),
            )
            .await
            .unwrap();
        let old = driver
            .resolve_container("db", "orders", OperationOptions::default())
            .await
            .unwrap();

        // Same name, new RID and partition key path.
        emulator
            .store()
            .create_container("db", "orders", PartitionKeyDefinition::from("/id"));
        let stale = driver
            .resolve_container("db", "orders", OperationOptions::default())
            .await
            .unwrap();
        assert_eq!(stale.rid(), old.rid());

        let modifiers = RequestHeadersAndOptions {
            activity_header: None,
            session_header: None,
            content_response_on_write: ContentResponseOnWrite::Enabled,
            excluded_regions_value: None,
            configured_driver_timeout_policy: None,
            remaining_binding_timeout: None,
            availability_strategy: None,
            read_consistency_strategy: None,
            patch_strategy: None,
            throughput_control: None,
            utf8_decoding_mode: None,
            custom_headers: Default::default(),
        };
        Box::pin(run_read_container_future(
            driver.clone(),
            modifiers,
            "db".into(),
            "orders".into(),
            None,
        ))
        .await
        .unwrap()
        .unwrap();

        let fresh = driver
            .resolve_container("db", "orders", OperationOptions::default())
            .await
            .unwrap();
        assert_ne!(fresh.rid(), old.rid());
        assert_eq!(
            fresh.partition_key_definition(),
            &PartitionKeyDefinition::from("/id")
        );
    }

    #[tokio::test(start_paused = true)]
    async fn read_container_returns_read_when_cache_refresh_runs_out_of_time() {
        use azure_data_cosmos_driver::{
            fault_injection::{
                FaultInjectionConditionBuilder, FaultInjectionResultBuilder,
                FaultInjectionRuleBuilder, FaultOperationType,
            },
            in_memory_emulator::{InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion},
            models::{AccountReference, PartitionKeyDefinition},
            options::DriverOptions,
        };
        use url::Url;

        crate::test_support::prepare_python();
        let url = Url::parse("https://container-read-deadline.emulator.local").unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap(),
        ));
        emulator.store().create_database("db");
        emulator
            .store()
            .create_container("db", "orders", PartitionKeyDefinition::from("/pk"));
        // A cold cache makes the refresh step load partition-key ranges; slow them down.
        let slow_ranges = Arc::new(
            FaultInjectionRuleBuilder::new(
                "slow-partition-key-ranges",
                FaultInjectionResultBuilder::new()
                    .with_delay(Duration::from_secs(5))
                    .with_probability(1.0)
                    .build(),
            )
            .with_condition(
                FaultInjectionConditionBuilder::new()
                    .with_operation_type(FaultOperationType::MetadataPartitionKeyRanges)
                    .build(),
            )
            .build(),
        );
        let runtime = emulator
            .runtime_builder_with_fault_rules(vec![slow_ranges.clone()])
            .build()
            .await
            .unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_account_key(url, "ZW11bGF0b3Ita2V5"))
                    .build(),
            )
            .await
            .unwrap();
        let modifiers = RequestHeadersAndOptions {
            activity_header: None,
            session_header: None,
            content_response_on_write: ContentResponseOnWrite::Enabled,
            excluded_regions_value: None,
            configured_driver_timeout_policy: None,
            remaining_binding_timeout: None,
            availability_strategy: None,
            read_consistency_strategy: None,
            patch_strategy: None,
            throughput_control: None,
            utf8_decoding_mode: None,
            custom_headers: Default::default(),
        };
        let response = Box::pin(run_read_container_future(
            driver,
            modifiers,
            "db".into(),
            "orders".into(),
            Some(Duration::from_secs(1)),
        ))
        .await
        .unwrap()
        .unwrap();
        assert_eq!(u16::from(response.status().status_code()), 200);
        assert!(slow_ranges.hit_count() >= 1);
    }
}

// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Execute individual-item operations with shared preparation and result conversion.
//!
//! For an order read, "dbs/sales/colls/orders", "order-42", and the typed
//! "customer-17" partition key become a Rust driver ItemReference. Reads and
//! replacements can retain the resource address supplied in the item's _self field.

use super::partition_key_input::BindingPartitionKey;
use std::sync::Arc;

use pyo3::exceptions::{PyTimeoutError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{
        ActivityId, CosmosOperation, CosmosResponse, ItemReference, PartitionKey, SessionToken,
    },
};

use super::container_metadata::metadata_error;
use super::deadline::with_operation_timeout;
use super::driver_runner::{
    run_prepared_driver_operation_async, run_prepared_driver_operation_sync,
};
use super::request::{build_operation_options, parse_container_link, RequestHeadersAndOptions};
use super::response::{tuple_from_result, tuple_from_result_with_attempts};

/// Preserve whether the prepared target names an item or supplies its resource address.
pub(crate) enum ItemTarget {
    Name(String),
    SelfLink {
        database: String,
        container: String,
        item: String,
        by_rid: bool,
    },
}

impl From<String> for ItemTarget {
    fn from(id: String) -> Self {
        Self::Name(id)
    }
}

impl From<&str> for ItemTarget {
    fn from(id: &str) -> Self {
        Self::Name(id.to_owned())
    }
}

impl ItemTarget {
    pub(crate) fn from_self_link(link: &str) -> PyResult<Self> {
        let parts: Vec<_> = link.trim_matches('/').split('/').collect();
        match parts.as_slice() {
            ["dbs", database, "colls", container, "docs", item]
                if !database.is_empty() && !container.is_empty() && !item.is_empty() =>
            {
                Ok(Self::SelfLink {
                    database: (*database).to_owned(),
                    container: (*container).to_owned(),
                    item: (*item).to_owned(),
                    by_rid: azure_data_cosmos_driver::models::is_database_rid(database),
                })
            }
            _ => Err(PyValueError::new_err(
                "Item target _self must identify 'dbs/<db>/colls/<container>/docs/<item>'",
            )),
        }
    }
}

/// Run one item operation and return a binding response tuple.
/// The shared runner retains the cached CosmosDriver, prepares the operation,
/// and releases Python's global interpreter lock (GIL) while the calling thread
/// waits on the Tokio runtime. Metadata resolution and item execution share
/// the supplied binding timeout; neither gets a fresh timeout after waiting.
pub(crate) fn execute_item_operation_sync<'py>(
    py: Python<'py>,
    driver_handle: &str,
    container_link: &str,
    partition_key_input: BindingPartitionKey,
    modifiers: RequestHeadersAndOptions,
    item_target: ItemTarget,
    body_bytes: Vec<u8>,
    op_name: &str,
    honor_content_response: bool,
    build_op: impl FnOnce(ItemReference, Vec<u8>) -> CosmosOperation + Send,
) -> PyResult<Bound<'py, PyTuple>> {
    run_prepared_driver_operation_sync(
        py,
        driver_handle,
        op_name,
        move |driver| {
            let (database_name, container_name) = parse_container_link(container_link)?;
            let partition_key = partition_key_input.into_item_key()?;
            let future = with_operation_timeout(
                modifiers.operation_timeout,
                execute_item_on_driver(
                    driver,
                    database_name,
                    container_name,
                    partition_key,
                    item_target,
                    body_bytes,
                    modifiers,
                    honor_content_response,
                    build_op,
                ),
            );
            Ok(async move { future.await? })
        },
        |py, result| tuple_from_result(py, result?),
    )
}

/// Async sibling of `execute_item_operation_sync`, using the same driver future.
/// Validate inputs under the GIL, spawn driver work on the Tokio runtime,
/// and bridge its result to a Python awaitable. Result conversion reacquires the
/// GIL; credential callbacks can also re-enter Python during driver execution.
///
/// The Rust bridge future owns an `AbortOnDrop` guard so dropping that future
/// requests cancellation instead of merely detaching the task. This is not a
/// guarantee of immediate cleanup or cancellation of work already at the service backend.
pub(crate) fn execute_item_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    container_link: &str,
    partition_key_input: BindingPartitionKey,
    modifiers: RequestHeadersAndOptions,
    item_target: ItemTarget,
    body_bytes: Vec<u8>,
    op_name: &str,
    honor_content_response: bool,
    include_attempts: bool,
    build_op: impl FnOnce(ItemReference, Vec<u8>) -> CosmosOperation + Send + 'static,
) -> PyResult<Bound<'py, PyAny>> {
    run_prepared_driver_operation_async(
        py,
        driver_handle,
        op_name,
        move |driver| {
            let (database_name, container_name) = parse_container_link(container_link)?;
            let partition_key = partition_key_input.into_item_key()?;
            let future = with_operation_timeout(
                modifiers.operation_timeout,
                execute_item_on_driver(
                    driver,
                    database_name,
                    container_name,
                    partition_key,
                    item_target,
                    body_bytes,
                    modifiers,
                    honor_content_response,
                    build_op,
                ),
            );
            Ok(async move { future.await? })
        },
        if include_attempts {
            |py, result| tuple_from_result_with_attempts(py, result?)
        } else {
            |py, result| tuple_from_result(py, result?)
        },
    )
}

/// Resolve the container, obtain the partition key, and build the item operation.
/// Extract an omitted key from body bytes only when the operation permits it.
/// Then apply the request settings and execute through the Rust driver.
/// Preparation failures are Python exceptions, separate from the item result,
/// so metadata headers cannot be mistaken for an item response.
fn execute_item_on_driver(
    driver: Arc<CosmosDriver>,
    database_name: String,
    container_name: String,
    partition_key: Option<PartitionKey>,
    item_target: ItemTarget,
    body_bytes: Vec<u8>,
    modifiers: RequestHeadersAndOptions,
    honor_content_response: bool,
    build_op: impl FnOnce(ItemReference, Vec<u8>) -> CosmosOperation + Send,
) -> impl std::future::Future<Output = PyResult<Result<CosmosResponse, CosmosError>>> + Send {
    let deadline = modifiers
        .operation_timeout
        .map(|timeout| tokio::time::Instant::now() + timeout);
    async move {
        let resolution_options = build_operation_options(
            None,
            modifiers.excluded_regions_value.clone(),
            modifiers.driver_timeout_policy.clone(),
            None,
            Default::default(),
        );
        let container = match &item_target {
            ItemTarget::Name(_) => {
                driver
                    .resolve_container(&database_name, &container_name, resolution_options)
                    .await
            }
            ItemTarget::SelfLink {
                container,
                by_rid: true,
                ..
            } => {
                driver
                    .resolve_container_by_rid(container, resolution_options)
                    .await
            }
            ItemTarget::SelfLink {
                database,
                container,
                ..
            } => {
                driver
                    .resolve_container(database, container, resolution_options)
                    .await
            }
        }
        .map_err(|error| Python::with_gil(|py| metadata_error(py, error)))?;
        if let ItemTarget::SelfLink {
            database,
            by_rid: true,
            ..
        } = &item_target
        {
            if container.database_rid() != database {
                return Err(PyValueError::new_err(
                    "Item target _self has inconsistent database and container resource IDs",
                ));
            }
        }
        let partition_key = match partition_key {
            Some(key) => key,
            None => super::request::extract_partition_key_from_body(
                container.partition_key_definition(),
                &body_bytes,
            )?,
        };
        if deadline.is_some_and(|deadline| tokio::time::Instant::now() >= deadline) {
            return Err(PyTimeoutError::new_err(
                "Item budget exhausted during metadata or key extraction",
            ));
        }
        let item_ref = match item_target {
            ItemTarget::Name(id) => ItemReference::from_name(&container, partition_key, id),
            ItemTarget::SelfLink {
                item, by_rid: true, ..
            } => ItemReference::from_rid(&container, partition_key, item),
            ItemTarget::SelfLink { item, .. } => {
                ItemReference::from_name(&container, partition_key, item)
            }
        };
        let mut op = build_op(item_ref, body_bytes);

        if let Some(activity) = modifiers.activity_header.as_ref() {
            // Pass the supplied activity id to the driver without UUID parsing.
            op = op.with_activity_id(ActivityId::from(activity.clone()));
        }
        if let Some(session) = modifiers.session_header.as_ref() {
            op = op.with_session_token(SessionToken::from(session.clone()));
        }

        // no_response=True only applies to writes; delete / read pass
        // honor_content_response=false and keep the driver default.
        let content_response = if honor_content_response {
            Some(modifiers.content_response_on_write)
        } else {
            None
        };
        let read_consistency = if op.is_read_only() {
            modifiers.read_consistency()?
        } else {
            None
        };
        let mut options = build_operation_options(
            content_response,
            modifiers.excluded_regions_value,
            modifiers.driver_timeout_policy,
            modifiers.availability_strategy,
            modifiers.custom_headers,
        );
        options.read_consistency_strategy = read_consistency;

        Ok(driver.execute_singleton_operation(op, options).await)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use azure_core::http::{headers::HeaderName, headers::HeaderValue, Method, Request, Url};
    use azure_data_cosmos_driver::{
        in_memory_emulator::{
            ConsistencyLevel, ContainerConfig, InMemoryEmulatorHttpClient, RequestObserver,
            VirtualAccountConfig, VirtualRegion, WriteMode,
        },
        models::{AccountReference, FeedRange, PartitionKeyDefinition, PartitionKeyVersion, ResponseBody},
        options::{
            BinaryEncodingOptions, ContentResponseOnWrite, DriverOptions, OperationOptionsBuilder,
            Region,
        },
    };
    use pyo3::types::PyDict;
    use std::sync::Mutex;

    #[derive(Debug, Default)]
    struct MetadataRequests(Mutex<Vec<(String, String)>>);

    impl RequestObserver for MetadataRequests {
        fn on_request(&self, request: &Request) {
            let path = request.url().path();
            if request.method() == Method::Get
                && (path.ends_with("/colls/baseline") || path.ends_with("/colls/excluded"))
            {
                assert!(request
                    .headers()
                    .get_optional_str(&HeaderName::from_static("if-match"))
                    .is_none());
                self.0.lock().unwrap().push((
                    path.to_owned(),
                    request.url().host_str().unwrap().to_owned(),
                ));
            }
        }
    }

    #[derive(Debug, Default)]
    struct ReplacementPaths(Mutex<Vec<String>>);

    impl RequestObserver for ReplacementPaths {
        fn on_request(&self, request: &Request) {
            if request.method() == Method::Put && request.url().path().contains("/docs/") {
                self.0.lock().unwrap().push(request.url().path().to_owned());
            }
        }
    }

    fn modifiers() -> RequestHeadersAndOptions {
        Python::with_gil(|py| {
            let kwargs = PyDict::new_bound(py);
            kwargs.set_item("headers", PyDict::new_bound(py)).unwrap();
            kwargs.set_item("protocol_version", 3).unwrap();
            kwargs
                .set_item("settings", crate::wire::settings::test_settings(py))
                .unwrap();
            let prepared = py
                .import_bound("types")
                .unwrap()
                .getattr("SimpleNamespace")
                .unwrap()
                .call((), Some(&kwargs))
                .unwrap();
            super::super::request::extract_account_prepared_modifiers(&prepared).unwrap()
        })
    }

    #[derive(Debug, Default)]
    struct CreateSessionRequests {
        partition_map_reads: Mutex<usize>,
        item_tokens: Mutex<Vec<Option<String>>>,
    }

    impl RequestObserver for CreateSessionRequests {
        fn on_request(&self, request: &Request) {
            if request.url().path().contains("/pkranges") {
                *self.partition_map_reads.lock().unwrap() += 1;
            }
            if request.url().path().contains("/docs") {
                self.item_tokens.lock().unwrap().push(
                    request
                        .headers()
                        .get_optional_str(&HeaderName::from_static("x-ms-session-token"))
                        .map(str::to_owned),
                );
            }
        }
    }

    #[tokio::test]
    async fn create_uses_lazy_resolution_and_driver_cached_session_policy() {
        pyo3::prepare_freethreaded_python();
        for write_mode in [WriteMode::Single, WriteMode::Multi] {
            let url = Url::parse("https://create-session.emulator.local").unwrap();
            let observed = Arc::new(CreateSessionRequests::default());
            let config = VirtualAccountConfig::new(vec![
                VirtualRegion::new("East US", url.clone()),
                VirtualRegion::new(
                    "West US",
                    Url::parse("https://create-session-west.emulator.local").unwrap(),
                ),
            ])
            .unwrap()
            .with_write_mode(write_mode)
            .with_consistency(ConsistencyLevel::Session);
            let emulator = Arc::new(
                InMemoryEmulatorHttpClient::new(config).with_request_observer(observed.clone()),
            );
            emulator.store().create_database("db");
            emulator.store().create_container(
                "db",
                "orders",
                PartitionKeyDefinition::from("/customerId"),
            );
            let runtime = emulator.runtime_builder().build().await.unwrap();
            let driver = runtime
                .create_driver(
                    DriverOptions::builder(AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5"))
                        .with_partition_failover_options(
                            crate::runtime::partition_failover_options().unwrap(),
                        )
                        .build(),
                )
                .await
                .unwrap();
            driver
                .resolve_container("db", "orders", Default::default())
                .await
                .unwrap();
            assert_eq!(*observed.partition_map_reads.lock().unwrap(), 0);

            let mut saved_token = None;
            for (index, id) in ["first", "cached", "explicit"].into_iter().enumerate() {
                let mut options = modifiers();
                if index == 2 {
                    options.session_header = saved_token.clone();
                }
                let created = execute_item_on_driver(
                    driver.clone(),
                    "db".into(),
                    "orders".into(),
                    None,
                    id.into(),
                    serde_json::to_vec(&serde_json::json!({
                        "id": id, "customerId": "customer-17"
                    }))
                    .unwrap(),
                    options,
                    true,
                    |item, body| CosmosOperation::create_item(item).with_body(body),
                )
                .await
                .unwrap()
                .unwrap();
                if index == 0 {
                    saved_token = Some(
                        created
                            .headers()
                            .session_token
                            .as_ref()
                            .unwrap()
                            .to_string(),
                    );
                }
            }
            execute_item_on_driver(
                driver,
                "db".into(),
                "orders".into(),
                Some(PartitionKey::from("customer-17")),
                "first".into(),
                Vec::new(),
                modifiers(),
                false,
                |item, _| CosmosOperation::read_item(item),
            )
            .await
            .unwrap()
            .unwrap();
            let tokens = observed.item_tokens.lock().unwrap();
            assert_eq!(tokens.len(), 4);
            assert!(tokens[0].is_none());
            assert_eq!(tokens[1].is_some(), write_mode == WriteMode::Multi);
            assert_eq!(
                tokens[2], saved_token,
                "Explicit tokens remain a separate compatibility gap"
            );
            assert!(
                tokens[3].is_some(),
                "The driver must still retain tokens for reads"
            );
        }
    }

    #[tokio::test]
    async fn create_v1_keys_match_long_and_unicode_routing_vectors() {
        pyo3::prepare_freethreaded_python();
        let url = Url::parse("https://create-v1.emulator.local").unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap(),
        ));
        let definition =
            PartitionKeyDefinition::from("/customerId").with_version(PartitionKeyVersion::V1);
        emulator.store().create_database("db");
        emulator.store().create_container_with_config(
            "db",
            "orders",
            definition.clone(),
            ContainerConfig::new()
                .with_partition_count(4)
                .build()
                .unwrap(),
        );
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5"))
                    .with_partition_failover_options(
                        crate::runtime::partition_failover_options().unwrap(),
                    )
                    .with_operation_options(
                        OperationOptionsBuilder::new()
                            .with_binary_encoding(BinaryEncodingOptions::new().with_enabled(false))
                            .build(),
                    )
                    .build(),
            )
            .await
            .unwrap();
        // Expected V1 values from the driver's Java/Python production conformance vectors.
        for (index, (key, expected)) in [
            (
                "a".repeat(1024),
                format!("05C1EB5921F70608{}00", "62".repeat(100)),
            ),
            (
                "caf\u{e9} \u{6771}\u{4eac} \u{1f680}".to_owned(),
                "05C1DF0501C73008646267C4AA21E79EB2E5BBAD21F1A09B8100".to_owned(),
            ),
        ]
        .into_iter()
        .enumerate()
        {
            let id = format!("order-{index}");
            let body = serde_json::to_vec(&serde_json::json!({
                "id": id, "customerId": key
            }))
            .unwrap();
            let created = execute_item_on_driver(
                driver.clone(),
                "db".into(),
                "orders".into(),
                None,
                id.clone().into(),
                body,
                modifiers(),
                true,
                |item, body| {
                    let range = FeedRange::for_partition(item.partition_key().clone(), &definition);
                    assert_eq!(range.min_inclusive().to_hex(), expected);
                    CosmosOperation::create_item(item).with_body(body)
                },
            )
            .await
            .unwrap()
            .unwrap();
            assert_eq!(u16::from(created.status().status_code()), 201);
            let read = execute_item_on_driver(
                driver.clone(),
                "db".into(),
                "orders".into(),
                Some(PartitionKey::from(key.clone())),
                id.into(),
                Vec::new(),
                modifiers(),
                false,
                |item, _| CosmosOperation::read_item(item),
            )
            .await
            .unwrap()
            .unwrap();
            let ResponseBody::Bytes(body) = read.body() else {
                panic!("Expected order JSON");
            };
            assert_eq!(
                serde_json::from_slice::<serde_json::Value>(body).unwrap()["customerId"],
                key
            );
        }
    }

    #[derive(Debug, Default)]
    struct CreateRequests {
        metadata_reads: Mutex<usize>,
        writes: Mutex<Vec<Option<String>>>,
    }

    #[derive(Debug, Default)]
    struct SurrogateBodyRequests(Mutex<Vec<Vec<u8>>>);

    impl RequestObserver for SurrogateBodyRequests {
        fn on_request(&self, request: &Request) {
            if matches!(request.method(), Method::Post | Method::Put)
                && request.url().path().contains("/docs")
            {
                assert_eq!(
                    request
                        .headers()
                        .get_optional_str(&HeaderName::from_static("x-ms-documentdb-partitionkey"),),
                    Some("[\"customer-17\"]"),
                );
                self.0
                    .lock()
                    .unwrap()
                    .push(azure_core::Bytes::from(request.body()).to_vec());
            }
        }
    }

    #[tokio::test]
    async fn surrogate_bodies_reach_write_transport_without_reencoding() {
        pyo3::prepare_freethreaded_python();
        let url = Url::parse("https://surrogate-body.emulator.local").unwrap();
        let observed = Arc::new(SurrogateBodyRequests::default());
        let emulator = Arc::new(
            InMemoryEmulatorHttpClient::new(
                VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap(),
            )
            .with_request_observer(observed.clone()),
        );
        emulator.store().create_database("db");
        emulator
            .store()
            .create_container("db", "orders", PartitionKeyDefinition::from("/customerId"));
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5"))
                    .with_partition_failover_options(
                        crate::runtime::partition_failover_options().unwrap(),
                    )
                    .build(),
            )
            .await
            .unwrap();
        let body = br#"{"id":"order-42","customerId":"customer-17","note":"\ud800","nested":{"\udfff":"\udfff"}}"#;
        let id = super::super::request::extract_item_id(body).unwrap();
        for build in [
            CosmosOperation::create_item as fn(ItemReference) -> CosmosOperation,
            CosmosOperation::upsert_item,
            CosmosOperation::replace_item,
        ] {
            let result = execute_item_on_driver(
                driver.clone(),
                "db".into(),
                "orders".into(),
                None,
                id.clone().into(),
                body.to_vec(),
                modifiers(),
                true,
                |item, body| build(item).with_body(body),
            )
            .await
            .expect("Unrelated surrogates must not fail binding preparation");
            // The emulator's own JSON parser rejects the body. That simulated
            // service error must remain distinct from a binding preparation error.
            assert_eq!(u16::from(result.unwrap_err().status().status_code()), 400);
        }
        assert_eq!(*observed.0.lock().unwrap(), vec![body.to_vec(); 3]);
    }

    impl RequestObserver for CreateRequests {
        fn on_request(&self, request: &Request) {
            let header = |name| {
                request
                    .headers()
                    .get_optional_str(&HeaderName::from_static(name))
            };
            if request.method() == Method::Get
                && request.url().path() == "/dbs/db/colls/orders"
            {
                *self.metadata_reads.lock().unwrap() += 1;
                assert!(header("x-ms-test-create").is_none());
                assert!(header("x-ms-cosmos-priority-level").is_none());
                assert!(header("prefer").is_none());
            }
            if request.method() == Method::Post
                && request.url().path().trim_end_matches('/') == "/dbs/db/colls/orders/docs"
            {
                assert_eq!(header("x-ms-documentdb-partitionkey"), Some("[\"customer-17\"]"));
                assert_eq!(header("x-ms-test-create"), Some("orders"));
                assert_eq!(header("x-ms-cosmos-priority-level"), Some("High"));
                assert!(header("x-ms-cosmos-intended-collection-rid").is_some());
                self.writes.lock().unwrap().push(header("prefer").map(str::to_owned));
            }
        }
    }

    #[tokio::test]
    async fn create_preserves_duplicate_error_body_and_minimal_response_headers() {
        pyo3::prepare_freethreaded_python();
        let url = Url::parse("https://create-review.emulator.local").unwrap();
        let observed = Arc::new(CreateRequests::default());
        let emulator = Arc::new(
            InMemoryEmulatorHttpClient::new(
                VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())])
                    .unwrap(),
            )
            .with_request_observer(observed.clone()),
        );
        emulator.store().create_database("db");
        emulator.store().create_container(
            "db",
            "orders",
            PartitionKeyDefinition::new(vec!["/customerId".into()]),
        );
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5"))
                    .build(),
            )
            .await
            .unwrap();
        for (id, minimal, expected_status) in [
            ("order-42", false, 201),
            ("order-43", true, 201),
            ("order-42", false, 409),
        ] {
            let mut options = modifiers();
            options.content_response_on_write = if minimal {
                ContentResponseOnWrite::Disabled
            } else {
                ContentResponseOnWrite::Enabled
            };
            for (name, value) in [
                ("x-ms-test-create", "orders"),
                ("x-ms-cosmos-priority-level", "High"),
            ] {
                options.custom_headers.insert(
                    HeaderName::from_static(name),
                    HeaderValue::from_static(value),
                );
            }
            let body = serde_json::to_vec(
                &serde_json::json!({"id": id, "customerId": "customer-17"}),
            )
            .unwrap();
            let result = execute_item_on_driver(
                driver.clone(),
                "db".into(),
                "orders".into(),
                None,
                id.into(),
                body,
                options,
                true,
                |item, body| CosmosOperation::create_item(item).with_body(body),
            )
            .await
            .unwrap();
            match &result {
                Ok(response) => {
                    assert_eq!(u16::from(response.status().status_code()), expected_status);
                    assert!(response.headers().request_charge.is_some());
                    assert!(response.headers().etag.is_some());
                    assert!(response.headers().session_token.is_some());
                    if minimal {
                        assert!(matches!(response.body(), ResponseBody::NoPayload));
                    } else {
                        let ResponseBody::Bytes(body) = response.body() else {
                            panic!("Expected created item body");
                        };
                        let item: serde_json::Value = serde_json::from_slice(body).unwrap();
                        assert_eq!(item["id"], id);
                    }
                }
                Err(error) => {
                    assert_eq!(expected_status, 409);
                    assert_eq!(u16::from(error.status().status_code()), 409);
                    assert!(error.response().is_some());
                }
            }
            Python::with_gil(|py| {
                let envelope = tuple_from_result_with_attempts(py, result).unwrap();
                let response = envelope.get_item(0).unwrap();
                let response = response.downcast::<PyTuple>().unwrap();
                assert_eq!(response.get_item(0).unwrap().extract::<u16>().unwrap(), expected_status);
                let body = response.get_item(3).unwrap().extract::<Vec<u8>>().unwrap();
                if minimal {
                    assert!(body.is_empty());
                } else {
                    let body: serde_json::Value = serde_json::from_slice(&body).unwrap();
                    if expected_status == 409 {
                        assert!(body["message"].is_string() || body["Message"].is_string());
                        assert!(envelope.get_item(1).unwrap().is_none());
                    } else {
                        assert_eq!(body["id"], id);
                        assert!(!envelope.get_item(1).unwrap().is_none());
                    }
                }
            });
        }
        assert_eq!(*observed.metadata_reads.lock().unwrap(), 1);
        assert_eq!(
            *observed.writes.lock().unwrap(),
            vec![None, Some("return=minimal".into()), None],
        );
    }

    #[test]
    fn self_link_preserves_name_and_rid_targets_and_rejects_invalid_shapes() {
        pyo3::prepare_freethreaded_python();
        assert!(matches!(
            ItemTarget::from_self_link("/dbs/sales/colls/orders/docs/actual/").unwrap(),
            ItemTarget::SelfLink { database, container, item, by_rid: false }
                if database == "sales" && container == "orders" && item == "actual"
        ));
        assert!(matches!(
            ItemTarget::from_self_link(
                "dbs/AQAAAA==/colls/AQAAAIABAAA=/docs/AQAAAIABAAABAAAAAAAAAA==/"
            )
            .unwrap(),
            ItemTarget::SelfLink { by_rid: true, .. }
        ));
        for invalid in [
            "",
            "dbs/sales/colls/orders",
            "dbs/sales/colls/orders/docs/",
            "dbs//colls/orders/docs/item",
        ] {
            assert!(ItemTarget::from_self_link(invalid).is_err());
        }
    }

    #[derive(Debug, Default)]
    struct ReadRequests(Mutex<Vec<(String, Option<String>)>>);

    impl RequestObserver for ReadRequests {
        fn on_request(&self, request: &Request) {
            if request.method() != Method::Get {
                return;
            }
            let header = |name| {
                request
                    .headers()
                    .get_optional_str(&HeaderName::from_static(name))
            };
            if request.url().path().contains("/docs/") {
                assert_eq!(header("x-ms-documentdb-partitionkey"), Some("[\"customer-17\"]"));
                assert_eq!(header("x-ms-dedicatedgateway-max-age"), Some("500"));
                assert_eq!(header("x-ms-test-read"), Some("orders"));
                if request.url().path().starts_with("/dbs/db/colls/orders/") {
                    assert!(header("x-ms-cosmos-intended-collection-rid").is_some());
                }
                self.0.lock().unwrap().push((
                    request.url().path().to_owned(),
                    header("if-none-match").map(str::to_owned),
                ));
            } else {
                // Partition-map refreshes may carry their own continuation ETag.
                if !request.url().path().contains("/pkranges") {
                    assert!(header("if-none-match").is_none());
                }
                assert!(header("x-ms-dedicatedgateway-max-age").is_none());
                assert!(header("x-ms-test-read").is_none());
            }
        }
    }

    #[tokio::test]
    async fn read_consistency_override_controls_strategy_and_session_token() {
        #[derive(Debug, Default)]
        struct Requests(Mutex<Vec<(String, bool)>>);
        impl RequestObserver for Requests {
            fn on_request(&self, request: &Request) {
                if request.method() == Method::Get && request.url().path().contains("/docs/") {
                    let header = |name| {
                        request
                            .headers()
                            .get_optional_str(&HeaderName::from_static(name))
                    };
                    assert!(header("x-ms-consistency-level").is_none());
                    self.0.lock().unwrap().push((
                        header("x-ms-cosmos-read-consistency-strategy")
                            .unwrap()
                            .to_owned(),
                        header("x-ms-session-token").is_some(),
                    ));
                }
            }
        }
        pyo3::prepare_freethreaded_python();
        let url = Url::parse("https://read-consistency.emulator.local").unwrap();
        let observed = Arc::new(Requests::default());
        let emulator = Arc::new(
            InMemoryEmulatorHttpClient::new(
                VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())])
                    .unwrap()
                    .with_consistency(ConsistencyLevel::Strong),
            )
            .with_request_observer(observed.clone()),
        );
        emulator.store().create_database("db");
        emulator
            .store()
            .create_container("db", "orders", PartitionKeyDefinition::from("/customerId"));
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5"))
                    .with_partition_failover_options(
                        crate::runtime::partition_failover_options().unwrap(),
                    )
                    .with_operation_options(
                        OperationOptionsBuilder::new()
                            .with_read_consistency_strategy(
                                azure_data_cosmos_driver::options::ReadConsistencyStrategy::Session,
                            )
                            .build(),
                    )
                    .build(),
            )
            .await
            .unwrap();
        execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "orders".into(),
            None,
            "order-42".into(),
            br#"{"id":"order-42","customerId":"customer-17"}"#.to_vec(),
            modifiers(),
            true,
            |item, body| CosmosOperation::create_item(item).with_body(body),
        )
        .await
        .unwrap()
        .unwrap();
        for consistency in [Some("Eventual"), Some("Strong"), Some("Session"), None] {
            let mut settings = modifiers();
            if let Some(level) = consistency {
                settings.custom_headers.insert(
                    HeaderName::from_static("x-ms-consistency-level"),
                    HeaderValue::from_static(level),
                );
            }
            execute_item_on_driver(
                driver.clone(),
                "db".into(),
                "orders".into(),
                Some(PartitionKey::from("customer-17")),
                "order-42".into(),
                Vec::new(),
                settings,
                false,
                |item, _| CosmosOperation::read_item(item),
            )
            .await
            .unwrap()
            .unwrap();
        }
        assert_eq!(
            *observed.0.lock().unwrap(),
            vec![
                ("Eventual".into(), false),
                ("GlobalStrong".into(), false),
                ("Session".into(), true),
                ("Session".into(), true),
            ]
        );
    }

    #[tokio::test]
    async fn read_preserves_conditions_response_headers_and_resource_address() {
        pyo3::prepare_freethreaded_python();
        let url = Url::parse("https://read-review.emulator.local").unwrap();
        let observed = Arc::new(ReadRequests::default());
        let emulator = Arc::new(
            InMemoryEmulatorHttpClient::new(
                VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())])
                    .unwrap(),
            )
            .with_request_observer(observed.clone()),
        );
        emulator.store().create_database("db");
        emulator.store().create_container(
            "db",
            "orders",
            PartitionKeyDefinition::new(vec!["/customerId".into()]),
        );
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5"))
                    .with_operation_options(
                        OperationOptionsBuilder::new()
                            .with_binary_encoding(BinaryEncodingOptions::new().with_enabled(false))
                            .build(),
                    )
                    .build(),
            )
            .await
            .unwrap();
        let created = execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "orders".into(),
            None,
            "order-42".into(),
            br#"{"id":"order-42","customerId":"customer-17"}"#.to_vec(),
            modifiers(),
            true,
            |item, body| CosmosOperation::create_item(item).with_body(body),
        )
        .await
        .unwrap()
        .unwrap();
        let etag = created.headers().etag.as_ref().unwrap().to_string();
        let ResponseBody::Bytes(body) = created.body() else {
            panic!("Expected created order body");
        };
        let document: serde_json::Value = serde_json::from_slice(body).unwrap();
        let self_link = document["_self"].as_str().unwrap();

        for (target, condition, expected_status) in [
            (ItemTarget::Name("order-42".into()), None, Some(200)),
            (ItemTarget::Name("order-42".into()), Some(etag.clone()), Some(304)),
            (ItemTarget::Name("missing".into()), None, Some(404)),
            (ItemTarget::from_self_link(self_link).unwrap(), None, None),
        ] {
            let mut options = modifiers();
            for (name, value) in [
                ("x-ms-dedicatedgateway-max-age", "500"),
                ("x-ms-test-read", "orders"),
            ] {
                options.custom_headers.insert(
                    HeaderName::from_static(name),
                    HeaderValue::from_static(value),
                );
            }
            if let Some(condition) = condition {
                options.custom_headers.insert(
                    HeaderName::from_static("if-none-match"),
                    HeaderValue::from(condition),
                );
            }
            let result = execute_item_on_driver(
                driver.clone(),
                "db".into(),
                "orders".into(),
                Some(PartitionKey::from("customer-17")),
                target,
                Vec::new(),
                options,
                false,
                |item, _| CosmosOperation::read_item(item),
            )
            .await
            .unwrap();
            // The emulator does not establish live-service RID addressing semantics.
            // Preserve the actual outgoing address regardless of its simulated reply.
            if let Some(expected_status) = expected_status {
                Python::with_gil(|py| {
                    let response = tuple_from_result(py, result).unwrap();
                    assert_eq!(
                        response.get_item(0).unwrap().extract::<u16>().unwrap(),
                        expected_status,
                    );
                    let headers = response.get_item(2).unwrap();
                    assert!(headers.get_item("x-ms-request-charge").is_ok());
                    let body = response.get_item(3).unwrap().extract::<Vec<u8>>().unwrap();
                    match expected_status {
                        200 => {
                            assert_eq!(
                                serde_json::from_slice::<serde_json::Value>(&body).unwrap()["id"],
                                "order-42",
                            );
                            assert_eq!(headers.get_item("etag").unwrap().extract::<String>().unwrap(), etag);
                        }
                        304 => assert!(body.is_empty()),
                        404 => assert!(!body.is_empty()),
                        _ => unreachable!(),
                    }
                });
            }
        }
        assert_eq!(
            *observed.0.lock().unwrap(),
            vec![
                ("/dbs/db/colls/orders/docs/order-42".into(), None),
                ("/dbs/db/colls/orders/docs/order-42".into(), Some(etag)),
                ("/dbs/db/colls/orders/docs/missing".into(), None),
                (format!("/{}", self_link.trim_matches('/')), None),
            ],
        );
    }

    #[tokio::test]
    async fn item_exclusions_apply_to_cold_metadata_without_item_conditions() {
        pyo3::prepare_freethreaded_python();
        let east = Url::parse("https://eastus.emulator.local").unwrap();
        let west = Url::parse("https://westus.emulator.local").unwrap();
        let observed = Arc::new(MetadataRequests::default());
        let emulator = Arc::new(
            InMemoryEmulatorHttpClient::new(
                VirtualAccountConfig::new(vec![
                    VirtualRegion::new("East US", east.clone()),
                    VirtualRegion::new("West US", west),
                ])
                .unwrap(),
            )
            .with_request_observer(observed.clone()),
        );
        emulator.store().create_database("db");
        for name in ["baseline", "excluded"] {
            emulator.store().create_container(
                "db",
                name,
                PartitionKeyDefinition::new(vec!["/pk".into()]),
            );
        }
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_master_key(east, "ZW11bGF0b3Ita2V5"))
                    .with_preferred_regions(vec![Region::WEST_US, Region::EAST_US])
                    .build(),
            )
            .await
            .unwrap();
        for name in ["baseline", "excluded"] {
            let mut options = modifiers();
            options.custom_headers.insert(
                HeaderName::from_static("if-match"),
                HeaderValue::from("\"old\""),
            );
            if name == "excluded" {
                options.excluded_regions_value = Some([Region::WEST_US].into_iter().collect());
            }
            let error = execute_item_on_driver(
                driver.clone(),
                "db".into(),
                name.into(),
                None,
                "missing".into(),
                br#"{"id":"missing","pk":"A"}"#.to_vec(),
                options,
                true,
                |item, body| CosmosOperation::replace_item(item).with_body(body),
            )
            .await
            .unwrap()
            .unwrap_err();
            assert_eq!(u16::from(error.status().status_code()), 404);
        }
        assert_eq!(
            *observed.0.lock().unwrap(),
            vec![
                (
                    "/dbs/db/colls/baseline".into(),
                    "westus.emulator.local".into()
                ),
                (
                    "/dbs/db/colls/excluded".into(),
                    "eastus.emulator.local".into()
                ),
            ],
        );
    }

    #[tokio::test]
    async fn all_six_items_use_binding_owned_metadata_and_preserve_error_phase() {
        pyo3::prepare_freethreaded_python();
        let url = Url::parse("https://single-call.emulator.local").unwrap();
        let replacements = Arc::new(ReplacementPaths::default());
        let emulator = Arc::new(
            InMemoryEmulatorHttpClient::new(
                VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())])
                    .unwrap(),
            )
            .with_request_observer(replacements.clone()),
        );
        emulator.store().create_database("db");
        emulator.store().create_container_with_config(
            "db",
            "c",
            PartitionKeyDefinition::new(vec!["/pk".into()]),
            ContainerConfig::new()
                .with_partition_count(1)
                .build()
                .unwrap(),
        );
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let driver = runtime
            .create_driver(
                DriverOptions::builder(AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5"))
                    .with_operation_options(
                        OperationOptionsBuilder::new()
                            .with_binary_encoding(BinaryEncodingOptions::new().with_enabled(false))
                            .build(),
                    )
                    .build(),
            )
            .await
            .unwrap();
        for (build, body) in [
            (
                CosmosOperation::create_item as fn(ItemReference) -> CosmosOperation,
                br#"{"id":"item","pk":"A","n":0}"#.as_slice(),
            ),
            (
                CosmosOperation::upsert_item,
                br#"{"id":"item","pk":"A","n":0,"obsolete":true}"#.as_slice(),
            ),
            (
                CosmosOperation::replace_item,
                br#"{"id":"item","pk":"A","n":0}"#.as_slice(),
            ),
        ] {
            let result = execute_item_on_driver(
                driver.clone(),
                "db".into(),
                "c".into(),
                None,
                "item".into(),
                body.to_vec(),
                modifiers(),
                true,
                |item, body| build(item).with_body(body),
            )
            .await
            .unwrap()
            .unwrap();
            assert!(result.status().is_success());
        }
        execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            Some(PartitionKey::from("A")),
            "item".into(),
            br#"{"operations":[{"op":"incr","path":"/n","value":1}]}"#.to_vec(),
            modifiers(),
            true,
            |item, body| CosmosOperation::patch_item(item).with_body(body),
        )
        .await
        .unwrap()
        .unwrap();
        let read = execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            Some(PartitionKey::from("A")),
            "item".into(),
            Vec::new(),
            modifiers(),
            false,
            |item, _| CosmosOperation::read_item(item),
        )
        .await
        .unwrap()
        .unwrap();
        let ResponseBody::Bytes(body) = read.body() else {
            panic!("Expected JSON body");
        };
        let document: serde_json::Value = serde_json::from_slice(body).unwrap();
        assert_eq!(document["n"], 1);
        assert!(document.get("obsolete").is_none());
        let self_link = document["_self"].as_str().unwrap();

        let etag = read.headers().etag.as_ref().unwrap().to_string();
        let mut guarded = modifiers();
        guarded.custom_headers.insert(
            HeaderName::from_static("if-match"),
            HeaderValue::from(etag.clone()),
        );
        guarded.content_response_on_write = ContentResponseOnWrite::Disabled;
        let replaced = execute_item_on_driver(
            driver.clone(),
            "unused-database".into(),
            "unused-container".into(),
            None,
            ItemTarget::from_self_link("dbs/db/colls/c/docs/item/").unwrap(),
            br#"{"id":"item","pk":"A","n":2}"#.to_vec(),
            guarded,
            true,
            |item, body| CosmosOperation::replace_item(item).with_body(body),
        )
        .await
        .unwrap()
        .unwrap();
        assert!(replaced.status().is_success());
        assert!(matches!(replaced.body(), ResponseBody::NoPayload));
        assert!(replaced.headers().request_charge.is_some());
        assert_ne!(replaced.headers().etag.as_ref().unwrap().to_string(), etag);

        let mut stale = modifiers();
        stale
            .custom_headers
            .insert(HeaderName::from_static("if-match"), HeaderValue::from(etag));
        let rejected = execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            None,
            "item".into(),
            br#"{"id":"item","pk":"A","n":3}"#.to_vec(),
            stale,
            true,
            |item, body| CosmosOperation::replace_item(item).with_body(body),
        )
        .await
        .unwrap()
        .unwrap_err();
        assert_eq!(u16::from(rejected.status().status_code()), 412);
        assert!(rejected.response().is_some());

        // Keep the explicit key; the emulator now rejects the mismatched body.
        let mismatched_key = execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            Some(PartitionKey::from("B")),
            "other".into(),
            br#"{"id":"other","pk":"A"}"#.to_vec(),
            modifiers(),
            true,
            |item, body| {
                assert_eq!(item.partition_key(), &PartitionKey::from("B"));
                CosmosOperation::create_item(item).with_body(body)
            },
        )
        .await
        .unwrap()
        .unwrap_err();
        assert_eq!(u16::from(mismatched_key.status().status_code()), 400);
        assert!(mismatched_key.response().is_some());

        let mut timed = modifiers();
        timed.operation_timeout = Some(std::time::Duration::from_millis(1));
        let pending = execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            None,
            "expired".into(),
            br#"{"id":"expired","pk":"A"}"#.to_vec(),
            timed,
            true,
            |_, _| panic!("Expired preparation must not construct an item"),
        );
        tokio::time::sleep(std::time::Duration::from_millis(5)).await;
        let expired = pending.await.unwrap_err();
        Python::with_gil(|py| assert!(expired.is_instance_of::<PyTimeoutError>(py)));

        execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            Some(PartitionKey::from("A")),
            "item".into(),
            Vec::new(),
            modifiers(),
            false,
            |item, _| CosmosOperation::delete_item(item),
        )
        .await
        .unwrap()
        .unwrap();
        let missing_item = execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            Some(PartitionKey::from("A")),
            "item".into(),
            Vec::new(),
            modifiers(),
            false,
            |item, _| CosmosOperation::read_item(item),
        )
        .await
        .unwrap()
        .unwrap_err();
        assert_eq!(u16::from(missing_item.status().status_code()), 404);
        execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            None,
            "item".into(),
            br#"{"id":"item","pk":"A","n":7}"#.to_vec(),
            modifiers(),
            true,
            |item, body| CosmosOperation::create_item(item).with_body(body),
        )
        .await
        .unwrap()
        .unwrap();
        replacements.0.lock().unwrap().clear();
        let stale_target = execute_item_on_driver(
            driver.clone(),
            "unused-database".into(),
            "unused-container".into(),
            None,
            ItemTarget::from_self_link(self_link).unwrap(),
            br#"{"id":"item","pk":"A","n":8}"#.to_vec(),
            modifiers(),
            true,
            |item, body| CosmosOperation::replace_item(item).with_body(body),
        )
        .await
        .unwrap()
        .unwrap_err();
        // A recreated name must not retarget the original resource address.
        assert_eq!(u16::from(stale_target.status().status_code()), 404);
        assert_eq!(
            *replacements.0.lock().unwrap(),
            vec![format!("/{}", self_link.trim_matches('/'))],
        );
        let recreated = execute_item_on_driver(
            driver.clone(),
            "db".into(),
            "c".into(),
            Some(PartitionKey::from("A")),
            "item".into(),
            Vec::new(),
            modifiers(),
            false,
            |item, _| CosmosOperation::read_item(item),
        )
        .await
        .unwrap()
        .unwrap();
        let ResponseBody::Bytes(recreated_body) = recreated.body() else {
            panic!("Expected recreated document");
        };
        assert_eq!(
            serde_json::from_slice::<serde_json::Value>(recreated_body).unwrap()["n"],
            7
        );

        let missing_container = execute_item_on_driver(
            driver,
            "db".into(),
            "missing".into(),
            None,
            "item".into(),
            br#"{"id":"item","pk":"A"}"#.to_vec(),
            modifiers(),
            true,
            |_, _| panic!("Metadata failure must not construct or execute an item"),
        )
        .await
        .unwrap_err();
        Python::with_gil(|py| {
            assert!(
                missing_container.is_instance_of::<super::super::errors::_DriverResponseError>(py)
            );
            let response = missing_container
                .value_bound(py)
                .getattr("args")
                .unwrap()
                .get_item(0)
                .unwrap();
            assert_eq!(response.get_item(0).unwrap().extract::<u16>().unwrap(), 404);
        });
    }
}

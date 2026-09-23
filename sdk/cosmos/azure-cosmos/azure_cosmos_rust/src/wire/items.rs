// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Execute individual-item operations with shared preparation and result conversion.
//!
//! For an order read, "dbs/sales/colls/orders", "order-42", and the typed
//! "customer-17" partition key become a Rust driver ItemReference. A replacement
//! can instead retain the resource address supplied in the item's _self field.

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
use super::response::tuple_from_result;

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
                "replace_item target _self must identify 'dbs/<db>/colls/<container>/docs/<item>'",
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
        |py, result| tuple_from_result(py, result?),
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
                    "replace_item target _self has inconsistent database and container resource IDs",
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
        let options = build_operation_options(
            content_response,
            modifiers.excluded_regions_value,
            modifiers.driver_timeout_policy,
            modifiers.availability_strategy,
            modifiers.custom_headers,
        );

        Ok(driver.execute_singleton_operation(op, options).await)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use azure_core::http::{headers::HeaderName, headers::HeaderValue, Method, Request, Url};
    use azure_data_cosmos_driver::{
        in_memory_emulator::{
            ContainerConfig, InMemoryEmulatorHttpClient, RequestObserver, VirtualAccountConfig,
            VirtualRegion,
        },
        models::{AccountReference, PartitionKeyDefinition, ResponseBody},
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

        // Check selection before execution: the single-partition emulator
        // does not model every service-side header/body mismatch rejection.
        execute_item_on_driver(
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
        .unwrap();

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
        // The emulator compares the body ID to the URI leaf even for RID
        // addresses. Verify the actual wire target, not simulated RID semantics.
        assert_eq!(u16::from(stale_target.status().status_code()), 400);
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

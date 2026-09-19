// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Retained cursors for item queries, read-all feeds and change feeds.

use std::{future::Future, sync::Arc, time::Duration};

use azure_data_cosmos_driver::{
    driver::{CosmosDriver, OperationPlan},
    error::{CosmosError, CosmosStatus},
    models::{
        ActivityId, ChangeFeedStartFrom, ContainerReference, ContinuationToken, CosmosOperation,
        CosmosResponse, FeedRange, PartitionKey, SessionToken,
    },
    options::PlanOptions,
};
use pyo3::{
    exceptions::{PyNotImplementedError, PyRuntimeError, PyTimeoutError, PyValueError},
    prelude::*,
    types::{PyDict, PyTuple},
};
use serde::Deserialize;
use tokio::sync::Mutex;

#[cfg(test)]
use super::legacy_partition_key::legacy_partition_key_header;
use super::{
    deadline::{parse_remaining_timeout, with_timeout},
    diagnostics::BINDING_OP_COUNT,
    lookup_driver,
    request::{
        build_operation_options, extract_common_prepared_inputs, parse_container_link,
        RequestHeadersAndOptions,
    },
    response::tuple_from_feed_result,
    AbortOnDrop,
};
use super::{partition_key::PartitionKeyInput, query::QueryTarget};
use crate::runtime::require_runtime_context;

struct Progress {
    plan: OperationPlan,
    container: ContainerReference,
    identity: (String, String),
    continuation: Option<String>,
    request: FeedRequest,
}

#[derive(Clone, PartialEq)]
enum FeedRequest {
    ReadAll,
    ChangeFeed(ChangeFeedRequest),
    Query(QueryRequest),
}

#[derive(Clone, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
struct QueryRequest {
    query: serde_json::Value,
    #[serde(skip)]
    partition_key: Option<PartitionKey>,
    feed_range: Option<(String, String)>,
    allow_cross_partition: bool,
}

impl QueryRequest {
    fn operation(&self, container: ContainerReference) -> PyResult<CosmosOperation> {
        let range = match (&self.partition_key, &self.feed_range) {
            (Some(key), None) => {
                if key.is_empty() {
                    return Err(PyValueError::new_err("Query partition key cannot be empty"));
                }
                if key.len() > container.partition_key_definition().paths().len() {
                    return Err(PyValueError::new_err(
                        "Query partition key has too many components for this container",
                    ));
                }
                FeedRange::for_partition(key.clone(), container.partition_key_definition())
            }
            (None, Some((min, max))) => FeedRange::new(min.clone().into(), max.clone().into())
                .map_err(|error| PyValueError::new_err(error.to_string()))?,
            (None, None) => FeedRange::full(),
            _ => {
                return Err(PyValueError::new_err(
                    "partition_key and feed_range are exclusive",
                ))
            }
        };
        let operation = CosmosOperation::query_items(container, Some(range)).with_body(
            serde_json::to_vec(&self.query)
                .map_err(|error| PyValueError::new_err(error.to_string()))?,
        );
        if !self.allow_cross_partition && !operation.is_trivial() {
            return Err(PyNotImplementedError::new_err(
                "Rust query_items requires a complete partition_key when cross-partition execution \
                 is disabled; SQL predicate inference is not used. No fallback was performed.",
            ));
        }
        Ok(operation)
    }
}

#[derive(Clone, Deserialize, PartialEq)]
#[serde(deny_unknown_fields)]
struct ChangeFeedRequest {
    mode: String,
    start: String,
    #[serde(skip)]
    partition_key: Option<PartitionKey>,
    feed_range: Option<(String, String)>,
}

impl ChangeFeedRequest {
    async fn scope_width(
        &self,
        driver: &CosmosDriver,
        container: &ContainerReference,
    ) -> PyResult<Result<Option<usize>, CosmosError>> {
        if let Some(key) = &self.partition_key {
            return Ok(driver
                .resolve_partition_key_ranges_for_key(container, key, false)
                .await
                .map(|ranges| ranges.map(|ranges| ranges.len())));
        }
        let scope = match &self.feed_range {
            Some((min, max)) => FeedRange::new(min.clone().into(), max.clone().into())
                .map_err(|error| PyValueError::new_err(error.to_string()))?,
            None => FeedRange::full(),
        };
        Ok(driver
            .resolve_all_partition_key_ranges(container, false)
            .await
            .map(|ranges| {
                ranges.map(|ranges| {
                    ranges
                        .iter()
                        .filter(|range| {
                            range.max_exclusive > *scope.min_inclusive()
                                && range.min_inclusive < *scope.max_exclusive()
                        })
                        .count()
                })
            }))
    }

    fn validate_width(width: Option<usize>) -> PyResult<()> {
        match width {
            Some(1) => Ok(()),
            None | Some(0) => Err(PyRuntimeError::new_err("Could not resolve the change-feed scope")),
            Some(_) => Err(PyNotImplementedError::new_err(
                "Rust change feed across multiple physical partitions is blocked by driver polling gap 12; \
                 use an explicit legacy backend or a single-partition scope. No fallback was performed.",
            )),
        }
    }

    fn operation(&self, container: ContainerReference) -> PyResult<CosmosOperation> {
        let range = match (&self.partition_key, &self.feed_range) {
            (Some(key), None) => {
                FeedRange::for_partition(key.clone(), container.partition_key_definition())
            }
            (None, Some((min, max))) => FeedRange::new(min.clone().into(), max.clone().into())
                .map_err(|error| PyValueError::new_err(error.to_string()))?,
            (None, None) => FeedRange::full(),
            _ => {
                return Err(PyValueError::new_err(
                    "partition_key and feed_range are exclusive",
                ))
            }
        };
        let operation = match self.mode.as_str() {
            "LatestVersion" => CosmosOperation::change_feed(container, Some(range)),
            "AllVersionsAndDeletes" => {
                CosmosOperation::change_feed_all_versions_and_deletes(container, Some(range))
            }
            _ => return Err(PyValueError::new_err("Invalid change-feed mode")),
        };
        let start = match self.start.as_str() {
            "Now" => ChangeFeedStartFrom::Now,
            "Beginning" => ChangeFeedStartFrom::Beginning,
            timestamp => serde_json::from_value(
                serde_json::json!({"kind":"point_in_time","value":timestamp}),
            )
            .map_err(|error| {
                PyValueError::new_err(format!("Invalid change-feed start time: {error}"))
            })?,
        };
        Ok(operation.with_change_feed_start(start))
    }
}

#[derive(Default)]
struct CursorState {
    started: bool,
    progress: Option<Progress>,
    has_more: bool,
    continuation_unsupported: bool,
}

/// Retained state for a Python page iterator. In-flight fetches clone the state
/// Arc, so dropping the Python cursor need not immediately release its plan.
#[pyclass]
#[derive(Default)]
pub(crate) struct ItemFeedCursor {
    state: Arc<Mutex<CursorState>>,
}

#[pymethods]
impl ItemFeedCursor {
    #[new]
    fn new() -> Self {
        Self::default()
    }

    #[getter]
    fn has_more(&self) -> PyResult<bool> {
        Ok(self
            .state
            .try_lock()
            .map_err(|_| PyRuntimeError::new_err("Cursor is in use"))?
            .has_more)
    }

    #[getter]
    fn continuation_supported(&self) -> PyResult<bool> {
        Ok(!self
            .state
            .try_lock()
            .map_err(|_| PyRuntimeError::new_err("Cursor is in use"))?
            .continuation_unsupported)
    }
}

type PageResult = (Result<Option<CosmosResponse>, CosmosError>, Option<String>);

fn page_timeout<T>(
    timeout: Option<Duration>,
    operation: impl Future<Output = T>,
) -> impl Future<Output = PyResult<T>> {
    let timed = with_timeout(timeout, operation);
    async move {
        timed.await.map_err(|error| {
            PyTimeoutError::new_err(format!(
                "Feed page timed out during metadata, planning, or execution: {error}"
            ))
        })
    }
}

#[cfg(test)]
async fn next_page(
    driver: Arc<CosmosDriver>,
    state: Arc<Mutex<CursorState>>,
    identity: (String, String),
    continuation: Option<String>,
    modifiers: RequestHeadersAndOptions,
) -> PyResult<PageResult> {
    next_plan_page(
        driver,
        state,
        identity,
        continuation,
        modifiers,
        FeedRequest::ReadAll,
    )
    .await
}

async fn next_plan_page(
    driver: Arc<CosmosDriver>,
    state: Arc<Mutex<CursorState>>,
    identity: (String, String),
    continuation: Option<String>,
    mut modifiers: RequestHeadersAndOptions,
    request: FeedRequest,
) -> PyResult<PageResult> {
    let mut state = state
        .try_lock()
        .map_err(|_| PyRuntimeError::new_err("Concurrent use of a retained feed cursor"))?;
    // Take ownership before awaiting. A cancelled/failed fetch must not leave a
    // partly advanced plan available for another fetch to skip undelivered rows.
    let progress = state.progress.take();
    if state.started && progress.is_none() {
        return Err(PyRuntimeError::new_err(
            "Feed cursor failed; resume using the last delivered continuation token",
        ));
    }
    state.started = true;
    modifiers
        .custom_headers
        .retain(|name, _| name.as_str() != "x-ms-continuation");
    let options = build_operation_options(
        None,
        modifiers.excluded_regions_value,
        modifiers.end_to_end_timeout,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    let mut progress = if let Some(progress) = progress {
        if progress.identity != identity
            || progress.continuation != continuation
            || progress.request != request
        {
            return Err(PyValueError::new_err(
                "Feed cursor does not match the client, container, query, scope, or continuation",
            ));
        }
        progress
    } else {
        let (database, name) = parse_container_link(&identity.1)?;
        let container = match driver
            .resolve_container(&database, &name, Default::default())
            .await
        {
            Ok(container) => container,
            Err(error) => return Ok((Err(error), None)),
        };
        if let FeedRequest::ChangeFeed(request) = &request {
            let width = match request.scope_width(&driver, &container).await? {
                Ok(width) => width,
                Err(error) => return Ok((Err(error), None)),
            };
            ChangeFeedRequest::validate_width(width)?;
        }
        let mut operation = match &request {
            FeedRequest::ChangeFeed(request) => request.operation(container.clone())?,
            FeedRequest::Query(request) => request.operation(container.clone())?,
            FeedRequest::ReadAll => {
                CosmosOperation::query_items(container.clone(), Some(FeedRange::full()))
                    .with_body(br#"{"query":"SELECT * FROM root r"}"#.to_vec())
            }
        };
        if let Some(activity) = modifiers.activity_header {
            operation = operation.with_activity_id(ActivityId::from(activity));
        }
        if let Some(session) = modifiers.session_header {
            operation = operation.with_session_token(SessionToken::from(session));
        }
        let token = continuation.map(ContinuationToken::from_string);
        let plan = match driver
            .plan_operation(operation, &options, token.as_ref(), &PlanOptions::default())
            .await
        {
            Ok(plan) => plan,
            Err(error) => return Ok((Err(error), None)),
        };
        Progress {
            plan,
            container,
            identity,
            continuation: None,
            request,
        }
    };
    let response = match driver
        .execute_plan(
            &mut progress.plan,
            Some(progress.container.clone()),
            options,
        )
        .await
    {
        Ok(response) => response,
        Err(error) => return Ok((Err(error), None)),
    };
    // Split recovery may expand a previously safe scope. Do not publish a
    // checkpoint or an empty poll that now covers only one of its children.
    if let FeedRequest::ChangeFeed(request) = &progress.request {
        let width = match request.scope_width(&driver, &progress.container).await? {
            Ok(width) => width,
            Err(error) => return Ok((Err(error), None)),
        };
        ChangeFeedRequest::validate_width(width)?;
    }
    let token = if response.is_some() && !state.continuation_unsupported {
        match progress.plan.to_continuation_token() {
            Ok(token) => Some(token.as_str().to_owned()),
            Err(error)
                if matches!(progress.request, FeedRequest::Query(_))
                    && (error.status()
                        == CosmosStatus::CLIENT_NON_STREAMING_ORDER_BY_CONTINUATION_UNSUPPORTED
                        || error.status()
                            == CosmosStatus::CLIENT_DISTINCT_CONTINUATION_UNSUPPORTED) =>
            {
                state.continuation_unsupported = true;
                None
            }
            Err(error) => return Ok((Err(error), None)),
        }
    } else {
        None
    };
    progress.continuation = token.clone();
    state.has_more = response.is_some();
    state.progress = if response.is_some() {
        Some(progress)
    } else {
        None
    };
    Ok((Ok(response), token))
}

fn feed_inputs(prepared: &Bound<'_, PyAny>, scope: PartitionKeyInput) -> PyResult<FeedRequest> {
    let op: String = prepared.getattr("op")?.extract()?;
    let key = match scope.into_query_target()? {
        QueryTarget::CrossPartition => None,
        QueryTarget::Partition(key) => Some(key),
    };
    if op == "read_all_items" {
        if key.is_some() {
            return Err(PyValueError::new_err(
                "read_all_items cursor requires whole-container scope",
            ));
        }
        return Ok(FeedRequest::ReadAll);
    }
    let body: Vec<u8> = prepared.getattr("body_bytes")?.extract()?;
    match op.as_str() {
        "query_items_change_feed" => {
            serde_json::from_slice::<ChangeFeedRequest>(&body).map(|mut request| {
                request.partition_key = key;
                FeedRequest::ChangeFeed(request)
            })
        }
        "query_items" => serde_json::from_slice::<QueryRequest>(&body).map(|mut request| {
            request.partition_key = key;
            FeedRequest::Query(request)
        }),
        _ => return Err(PyValueError::new_err("Unsupported retained feed operation")),
    }
    .map_err(|error| PyValueError::new_err(format!("Invalid retained feed request: {error}")))
}

fn finish_page<'py>(py: Python<'py>, result: PageResult) -> PyResult<Bound<'py, PyTuple>> {
    let (result, continuation) = result;
    let tuple = tuple_from_feed_result(py, result)?;
    let headers = tuple.get_item(2)?;
    let headers = headers.downcast::<PyDict>()?;
    if let Some(token) = continuation {
        headers.set_item("x-ms-continuation", token)?;
    } else if headers.contains("x-ms-continuation")? {
        headers.del_item("x-ms-continuation")?;
    }
    Ok(tuple)
}

fn inputs(
    prepared: &Bound<'_, PyAny>,
) -> PyResult<(
    String,
    RequestHeadersAndOptions,
    Option<String>,
    PartitionKeyInput,
)> {
    let (link, scope, modifiers) = extract_common_prepared_inputs(prepared)?;
    let continuation: Option<String> = prepared
        .getattr("settings")?
        .getattr("query")?
        .getattr("continuation")?
        .extract()?;
    if continuation
        .as_ref()
        .is_some_and(|token| !token.starts_with("c1."))
    {
        return Err(PyValueError::new_err(
            "read_all_items requires a Rust driver continuation token, not a legacy bookmark",
        ));
    }
    Ok((link, modifiers, continuation, scope))
}

#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, cursor, *, timeout_seconds=None))]
pub(crate) fn fetch_page_with_cursor<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    cursor: PyRef<'py, ItemFeedCursor>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyTuple>> {
    let (link, modifiers, token, scope) = inputs(prepared)?;
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    let request = feed_inputs(prepared, scope)?;
    BINDING_OP_COUNT.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let state = cursor.state.clone();
    let identity = (driver_handle.to_owned(), link);
    let runtime = require_runtime_context("fetch_page_with_cursor")?;
    let future = page_timeout(
        timeout,
        next_plan_page(driver, state, identity, token, modifiers, request),
    );
    let result = py.allow_threads(|| runtime.tokio_rt.block_on(future))??;
    finish_page(py, result)
}

#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, cursor, *, timeout_seconds=None))]
pub(crate) fn fetch_page_with_cursor_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    prepared: &Bound<'py, PyAny>,
    cursor: PyRef<'py, ItemFeedCursor>,
    timeout_seconds: Option<f64>,
) -> PyResult<Bound<'py, PyAny>> {
    let (link, modifiers, token, scope) = inputs(prepared)?;
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    let request = feed_inputs(prepared, scope)?;
    BINDING_OP_COUNT.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let state = cursor.state.clone();
    let identity = (driver_handle.to_owned(), link);
    let runtime = require_runtime_context("fetch_page_with_cursor_async")?;
    let future = page_timeout(
        timeout,
        next_plan_page(driver, state, identity, token, modifiers, request),
    );
    let join = runtime.tokio_rt.spawn(future);
    let abort = AbortOnDrop(join.abort_handle());
    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort = abort;
        let result = join
            .await
            .map_err(|error| PyRuntimeError::new_err(error.to_string()))???;
        Python::with_gil(|py| finish_page(py, result).map(|value| value.into_any().unbind()))
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use azure_core::http::{
        headers::{HeaderName, HeaderValue},
        Url,
    };
    use azure_data_cosmos_driver::{
        in_memory_emulator::{
            ContainerConfig, InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion,
        },
        models::{AccountReference, ItemReference, PartitionKey, PartitionKeyDefinition},
        options::{
            ContentResponseOnWrite, DriverOptions, EndToEndOperationLatencyPolicy,
            OperationOptionsBuilder, QueryPlanMode,
        },
    };
    use std::{
        borrow::Cow,
        collections::{BTreeSet, HashMap},
        time::Duration,
    };

    async fn setup(count: usize) -> (Arc<InMemoryEmulatorHttpClient>, Arc<CosmosDriver>) {
        setup_with_definition(
            count,
            PartitionKeyDefinition::new(vec![Cow::Borrowed("/pk")]),
        )
        .await
    }

    async fn setup_with_definition(
        count: usize,
        definition: PartitionKeyDefinition,
    ) -> (Arc<InMemoryEmulatorHttpClient>, Arc<CosmosDriver>) {
        pyo3::prepare_freethreaded_python();
        let url = Url::parse("https://read-all.emulator.local").unwrap();
        let config =
            VirtualAccountConfig::new(vec![VirtualRegion::new("East US", url.clone())]).unwrap();
        let emulator = Arc::new(InMemoryEmulatorHttpClient::new(config));
        emulator.store().create_database("db");
        for name in ["c", "other"] {
            emulator.store().create_container_with_config(
                "db",
                name,
                definition.clone(),
                ContainerConfig::new()
                    .with_partition_count(3)
                    .build()
                    .unwrap(),
            );
        }
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let account = AccountReference::with_master_key(url, "ZW11bGF0b3Ita2V5");
        let driver = runtime
            .create_driver(
                DriverOptions::builder(account)
                    .with_operation_options(
                        OperationOptionsBuilder::new()
                            .with_query_plan_mode(QueryPlanMode::GatewayOnly)
                            .build(),
                    )
                    .build(),
            )
            .await
            .unwrap();
        let container = driver
            .resolve_container("db", "c", Default::default())
            .await
            .unwrap();
        for i in 0..count {
            let key = format!("key-{i}");
            let mut body = serde_json::json!({"id": i.to_string(), "pk": key});
            let partition_key = if definition.paths().len() == 2 {
                let tenant = format!("tenant-{}", i % 2);
                body["tenant"] = serde_json::json!(tenant);
                legacy_partition_key_header(&serde_json::json!([tenant, key]).to_string()).unwrap()
            } else {
                PartitionKey::from(key)
            };
            driver
                .execute_operation(
                    CosmosOperation::create_item(ItemReference::from_name(
                        &container,
                        partition_key,
                        i.to_string(),
                    ))
                    .with_body(serde_json::to_vec(&body).unwrap()),
                    Default::default(),
                )
                .await
                .unwrap();
        }
        (emulator, driver)
    }

    fn modifiers() -> RequestHeadersAndOptions {
        RequestHeadersAndOptions {
            activity_header: None,
            session_header: None,
            content_response_on_write: ContentResponseOnWrite::Enabled,
            excluded_regions_value: None,
            end_to_end_timeout: Some(EndToEndOperationLatencyPolicy::new(Duration::from_secs(1))),
            item_timeout: None,
            availability_strategy: None,
            custom_headers: HashMap::from([(
                HeaderName::from_static("x-ms-max-item-count"),
                HeaderValue::from_static("2"),
            )]),
        }
    }

    async fn fetch(
        driver: &Arc<CosmosDriver>,
        state: &Arc<Mutex<CursorState>>,
        token: Option<String>,
    ) -> (Option<Vec<String>>, Option<String>) {
        let (response, token) = next_page(
            driver.clone(),
            state.clone(),
            ("test".into(), "dbs/db/colls/c".into()),
            token,
            modifiers(),
        )
        .await
        .unwrap();
        let rows = response.unwrap().map(|response| {
            let documents = match response.body().clone() {
                azure_data_cosmos_driver::models::ResponseBody::Bytes(bytes) => {
                    let envelope: serde_json::Value = serde_json::from_slice(&bytes).unwrap();
                    envelope["Documents"].as_array().unwrap().clone()
                }
                body => body.into_items::<serde_json::Value>().unwrap(),
            };
            documents
                .iter()
                .map(|row| row["id"].as_str().unwrap().to_owned())
                .collect()
        });
        (rows, token)
    }

    async fn drain(
        driver: &Arc<CosmosDriver>,
        state: &Arc<Mutex<CursorState>>,
        mut token: Option<String>,
    ) -> Vec<String> {
        let mut rows = Vec::new();
        for _ in 0..100 {
            let (page, next) = fetch(driver, state, token).await;
            token = next;
            match page {
                Some(page) => rows.extend(page),
                None => return rows,
            }
        }
        panic!("read-all did not drain");
    }

    fn change_request(mode: &str, start: &str) -> ChangeFeedRequest {
        ChangeFeedRequest {
            mode: mode.into(),
            start: start.into(),
            partition_key: None,
            feed_range: None,
        }
    }

    fn query_request(sql: &str) -> FeedRequest {
        FeedRequest::Query(QueryRequest {
            query: serde_json::json!({"query": sql}),
            partition_key: None,
            feed_range: None,
            allow_cross_partition: true,
        })
    }

    async fn query_page(
        driver: &Arc<CosmosDriver>,
        state: &Arc<Mutex<CursorState>>,
        request: &FeedRequest,
        token: Option<String>,
    ) -> (Option<Vec<serde_json::Value>>, Option<String>) {
        let (response, token) = next_plan_page(
            driver.clone(),
            state.clone(),
            ("query-test".into(), "dbs/db/colls/c".into()),
            token,
            modifiers(),
            request.clone(),
        )
        .await
        .unwrap();
        let rows = response
            .unwrap()
            .map(|response| match response.body().clone() {
                azure_data_cosmos_driver::models::ResponseBody::Bytes(bytes) => {
                    let envelope: serde_json::Value = serde_json::from_slice(&bytes).unwrap();
                    envelope["Documents"].as_array().unwrap().clone()
                }
                body => body.into_items::<serde_json::Value>().unwrap(),
            });
        (rows, token)
    }

    async fn query_drain(
        driver: &Arc<CosmosDriver>,
        request: &FeedRequest,
        mut token: Option<String>,
    ) -> Vec<serde_json::Value> {
        let state = Arc::new(Mutex::new(CursorState::default()));
        let mut all = Vec::new();
        for _ in 0..100 {
            let (rows, next) = query_page(driver, &state, request, token).await;
            token = next;
            match rows {
                Some(rows) => all.extend(rows),
                None => {
                    assert!(!state.lock().await.has_more);
                    return all;
                }
            }
        }
        panic!("query did not drain");
    }

    #[tokio::test]
    async fn queries_retain_order_limits_parameters_and_every_bookmark() {
        let (_emulator, driver) = setup(23).await;
        for sql in [
            "SELECT * FROM c",
            "SELECT c.id FROM c ORDER BY c.id",
            "SELECT TOP 7 c.id FROM c ORDER BY c.id DESC",
            "SELECT c.id FROM c ORDER BY c.id OFFSET 3 LIMIT 7",
        ] {
            let request = query_request(sql);
            let expected = query_drain(&driver, &request, None).await;
            assert_eq!(
                expected.len(),
                if sql.contains('7') { 7 } else { 23 },
                "{sql}"
            );
            if sql.contains("ORDER BY") {
                let mut ids: Vec<_> = (0..23).map(|i| i.to_string()).collect();
                ids.sort();
                if sql.contains("DESC") {
                    ids.reverse();
                }
                let offset = if sql.contains("OFFSET") { 3 } else { 0 };
                let count = if sql.contains('7') { 7 } else { 23 };
                assert_eq!(
                    expected,
                    ids.into_iter()
                        .skip(offset)
                        .take(count)
                        .map(|id| serde_json::json!({"id":id}))
                        .collect::<Vec<_>>(),
                    "{sql}"
                );
            }
            let state = Arc::new(Mutex::new(CursorState::default()));
            let mut all = Vec::new();
            let mut token = None;
            for _ in 0..100 {
                let (page, next) = query_page(&driver, &state, &request, token).await;
                token = next;
                let Some(page) = page else { break };
                all.extend(page);
                assert_eq!(
                    query_drain(&driver, &request, token.clone()).await,
                    expected[all.len()..],
                    "{sql}"
                );
            }
            assert_eq!(all, expected, "{sql}");
        }
        let mut request = query_request("SELECT * FROM c WHERE c.id = @id");
        if let FeedRequest::Query(ref mut query) = request {
            query.query["parameters"] = serde_json::json!([{"name":"@id","value":"5"}]);
        }
        let rows = query_drain(&driver, &request, None).await;
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0]["id"], "5");
    }

    #[tokio::test]
    async fn query_scopes_and_disabled_cross_partition_are_not_ignored() {
        let (_emulator, driver) = setup(12).await;
        let container = driver
            .resolve_container("db", "c", Default::default())
            .await
            .unwrap();
        let mut request = QueryRequest {
            query: serde_json::json!({"query":"SELECT * FROM c"}),
            partition_key: Some(legacy_partition_key_header(r#"["key-5"]"#).unwrap()),
            feed_range: None,
            allow_cross_partition: false,
        };
        let rows = query_drain(&driver, &FeedRequest::Query(request.clone()), None).await;
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0]["id"], "5");
        request.partition_key = None;
        assert!(request.operation(container.clone()).is_err());
        request.allow_cross_partition = true;
        let ranges = driver
            .resolve_all_partition_key_ranges(&container, false)
            .await
            .unwrap()
            .unwrap();
        let mut all = Vec::new();
        for range in ranges {
            request.feed_range = Some((range.min_inclusive.to_hex(), range.max_exclusive.to_hex()));
            all.extend(query_drain(&driver, &FeedRequest::Query(request.clone()), None).await);
        }
        assert_eq!(all.len(), 12);
        let ids: BTreeSet<_> = all.iter().map(|row| row["id"].as_str().unwrap()).collect();
        assert_eq!(ids.len(), 12);
    }

    #[tokio::test]
    async fn unordered_distinct_enumerates_without_a_resumable_token() {
        let (_emulator, driver) = setup(12).await;
        let request = query_request("SELECT DISTINCT VALUE c.id FROM c");
        let state = Arc::new(Mutex::new(CursorState::default()));
        let mut all = Vec::new();
        let mut token = None;
        for _ in 0..100 {
            let (page, next) = query_page(&driver, &state, &request, token).await;
            token = next;
            let Some(page) = page else { break };
            all.extend(page);
        }
        assert_eq!(all.len(), 12);
        let state = state.lock().await;
        assert!(state.continuation_unsupported);
        assert!(!state.has_more);
    }

    #[tokio::test]
    async fn hierarchical_prefix_query_only_returns_matching_logical_partitions() {
        let definition = serde_json::from_value(serde_json::json!({
            "paths": ["/tenant", "/pk"], "kind": "MultiHash", "version": 2
        }))
        .unwrap();
        let (_emulator, driver) = setup_with_definition(18, definition).await;
        let mut request = QueryRequest {
            query: serde_json::json!({"query":"SELECT * FROM c"}),
            partition_key: Some(legacy_partition_key_header(r#"["tenant-1"]"#).unwrap()),
            feed_range: None,
            allow_cross_partition: true,
        };
        let rows = query_drain(&driver, &FeedRequest::Query(request.clone()), None).await;
        assert_eq!(rows.len(), 9);
        assert!(rows.iter().all(|row| row["tenant"] == "tenant-1"));
        request.partition_key =
            Some(legacy_partition_key_header(r#"["tenant-1","key-5"]"#).unwrap());
        request.allow_cross_partition = false;
        let rows = query_drain(&driver, &FeedRequest::Query(request.clone()), None).await;
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0]["id"], "5");
        request.partition_key =
            Some(legacy_partition_key_header(r#"["tenant-1","key-5","extra"]"#).unwrap());
        let container = driver
            .resolve_container("db", "c", Default::default())
            .await
            .unwrap();
        assert!(request.operation(container).is_err());
    }

    #[tokio::test]
    async fn change_feed_multi_partition_scope_fails_closed_in_both_modes() {
        let (_emulator, driver) = setup(0).await;
        for mode in ["LatestVersion", "AllVersionsAndDeletes"] {
            let request = change_request(mode, "Now");
            let state = Arc::new(Mutex::new(CursorState::default()));
            let error = next_plan_page(
                driver.clone(),
                state.clone(),
                ("test".into(), "dbs/db/colls/c".into()),
                None,
                modifiers(),
                FeedRequest::ChangeFeed(request),
            )
            .await;
            assert!(matches!(error, Err(ref error) if error.to_string().contains("gap 12")));
            assert!(state.lock().await.progress.is_none());
        }
    }

    #[tokio::test]
    async fn change_feed_factories_preserve_scope_mode_and_start() {
        let (_emulator, driver) = setup(0).await;
        let container = driver
            .resolve_container("db", "c", Default::default())
            .await
            .unwrap();
        for mode in ["LatestVersion", "AllVersionsAndDeletes"] {
            for start in ["Now", "Beginning", "2020-01-01T00:00:00+00:00"] {
                let mut request = change_request(mode, start);
                request.partition_key = Some(legacy_partition_key_header(r#"["key-5"]"#).unwrap());
                assert_eq!(
                    request
                        .scope_width(&driver, &container)
                        .await
                        .unwrap()
                        .unwrap(),
                    Some(1)
                );
                let operation = request.operation(container.clone()).unwrap();
                assert!(operation.is_change_feed());
                assert_eq!(
                    operation.request_headers().full_fidelity_feed,
                    mode == "AllVersionsAndDeletes"
                );
                assert_eq!(
                    operation.request_headers().incremental_feed,
                    mode == "LatestVersion"
                );
                assert!(operation.request_headers().changefeed_wire_format_version);
                assert!(operation.change_feed_start().is_some());
                match start {
                    "Now" => assert!(matches!(
                        operation.change_feed_start(),
                        Some(ChangeFeedStartFrom::Now)
                    )),
                    "Beginning" => assert!(matches!(
                        operation.change_feed_start(),
                        Some(ChangeFeedStartFrom::Beginning)
                    )),
                    _ => assert!(matches!(
                        operation.change_feed_start(),
                        Some(ChangeFeedStartFrom::PointInTime(_))
                    )),
                }
            }
        }
    }

    #[tokio::test]
    async fn change_feed_range_gate_detects_split_and_full_key_stays_single() {
        let (emulator, driver) = setup(0).await;
        let container = driver
            .resolve_container("db", "c", Default::default())
            .await
            .unwrap();
        let ranges = driver
            .resolve_all_partition_key_ranges(&container, false)
            .await
            .unwrap()
            .unwrap();
        let parent = &ranges[0];
        let mut request = change_request("LatestVersion", "Beginning");
        request.feed_range = Some((parent.min_inclusive.to_hex(), parent.max_exclusive.to_hex()));
        assert_eq!(
            request
                .scope_width(&driver, &container)
                .await
                .unwrap()
                .unwrap(),
            Some(1)
        );
        emulator
            .store()
            .split_partition("db", "c", parent.id.parse().unwrap(), Duration::ZERO);
        emulator.store().drain_pending_control_plane().await;
        driver
            .resolve_all_partition_key_ranges(&container, true)
            .await
            .unwrap();
        let width = request
            .scope_width(&driver, &container)
            .await
            .unwrap()
            .unwrap();
        assert_eq!(width, Some(2));
        assert!(ChangeFeedRequest::validate_width(width).is_err());
        request.feed_range = None;
        request.partition_key = Some(legacy_partition_key_header(r#"["key-5"]"#).unwrap());
        assert_eq!(
            request
                .scope_width(&driver, &container)
                .await
                .unwrap()
                .unwrap(),
            Some(1)
        );
    }

    #[tokio::test]
    async fn retained_plan_covers_three_partitions_and_every_bookmark_resumes_exactly() {
        let (_emulator, driver) = setup(23).await;
        let state = Arc::new(Mutex::new(CursorState::default()));
        let mut token = None;
        let mut all = Vec::new();
        let mut checkpoints = Vec::new();
        for _ in 0..100 {
            let (page, next) = fetch(&driver, &state, token).await;
            token = next;
            if let Some(page) = page {
                assert!(page.len() <= 2);
                all.extend(page);
                checkpoints.push((all.len(), token.clone()));
            } else {
                break;
            }
        }
        assert_eq!(all.len(), 23);
        assert_eq!(
            all.iter().cloned().collect::<BTreeSet<_>>(),
            (0..23).map(|i| i.to_string()).collect()
        );
        assert!(checkpoints.len() > 3);
        for (offset, token) in checkpoints {
            assert!(token.as_ref().unwrap().starts_with("c1."));
            let resumed = Arc::new(Mutex::new(CursorState::default()));
            assert_eq!(drain(&driver, &resumed, token).await, all[offset..]);
        }
    }

    #[tokio::test]
    async fn customer_processing_time_does_not_expire_retained_plan() {
        let (_emulator, driver) = setup(12).await;
        let state = Arc::new(Mutex::new(CursorState::default()));
        let (first, token) = fetch(&driver, &state, None).await;
        tokio::time::sleep(Duration::from_millis(1100)).await;
        let rest = drain(&driver, &state, token).await;
        assert_eq!(first.unwrap().len() + rest.len(), 12);
    }

    #[tokio::test]
    async fn empty_container_and_invalid_or_wrong_container_tokens() {
        let (_emulator, driver) = setup(0).await;
        let empty = Arc::new(Mutex::new(CursorState::default()));
        assert!(drain(&driver, &empty, None).await.is_empty());
        let (_rows, token) =
            fetch(&driver, &Arc::new(Mutex::new(CursorState::default())), None).await;
        for (link, token) in [
            ("dbs/db/colls/c", Some("c1.invalid".into())),
            ("dbs/db/colls/other", token),
        ] {
            let state = Arc::new(Mutex::new(CursorState::default()));
            let (result, _) = next_page(
                driver.clone(),
                state,
                ("test".into(), link.into()),
                token,
                modifiers(),
            )
            .await
            .unwrap();
            assert!(
                result.is_err(),
                "invalid/wrong-container bookmark was accepted"
            );
        }
    }

    #[tokio::test]
    async fn partition_split_preserves_remaining_rows_and_bookmarks() {
        let (emulator, driver) = setup(31).await;
        let state = Arc::new(Mutex::new(CursorState::default()));
        let (first, token) = fetch(&driver, &state, None).await;
        emulator
            .store()
            .split_partition("db", "c", 0, Duration::ZERO);
        emulator.store().drain_pending_control_plane().await;
        assert_eq!(
            emulator.store().child_partition_ids("db", "c", &[0]).len(),
            2
        );
        let resumed = Arc::new(Mutex::new(CursorState::default()));
        let restored = drain(&driver, &resumed, token.clone()).await;
        let rest = drain(&driver, &state, token).await;
        assert_eq!(rest, restored);
        let all: Vec<_> = first.unwrap().into_iter().chain(rest).collect();
        assert_eq!(all.len(), 31);
        assert_eq!(
            all.into_iter().collect::<BTreeSet<_>>(),
            (0..31).map(|i| i.to_string()).collect()
        );
    }

    #[tokio::test]
    async fn cursor_rejects_concurrent_use_and_cannot_skip_a_failed_page() {
        let (_emulator, driver) = setup(9).await;
        let state = Arc::new(Mutex::new(CursorState::default()));
        let guard = state.lock().await;
        assert!(next_page(
            driver.clone(),
            state.clone(),
            ("test".into(), "dbs/db/colls/c".into()),
            None,
            modifiers()
        )
        .await
        .is_err());
        drop(guard);
        let (_first, token) = fetch(&driver, &state, None).await;
        assert!(next_page(
            driver.clone(),
            state.clone(),
            ("other-client".into(), "dbs/db/colls/c".into()),
            token.clone(),
            modifiers()
        )
        .await
        .is_err());
        assert!(next_page(
            driver.clone(),
            state.clone(),
            ("test".into(), "dbs/db/colls/c".into()),
            token.clone(),
            modifiers()
        )
        .await
        .is_err());
        let resumed = Arc::new(Mutex::new(CursorState::default()));
        assert!(!drain(&driver, &resumed, token).await.is_empty());
    }
}

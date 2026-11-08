// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

//! Retain feed cursors across item-query, read-all, and change-feed pages.
//!
//! A Python page iterator passes the same feed cursor for successive pages of
//! orders. The binding retains the Rust driver's plan rather than planning
//! again for each page. A continuation token, when supported, is a separate
//! value that can be used to resume with a new feed cursor.

use std::{
    future::Future,
    num::NonZeroU32,
    sync::{
        atomic::{AtomicU8, Ordering},
        Arc,
    },
    time::Duration,
};

use azure_data_cosmos_driver::{
    driver::{CosmosDriver, OperationPlan},
    error::{status_codes, CosmosError},
    models::{
        ActivityId, ChangeFeedStartFrom, ContainerReference, ContinuationToken, CosmosOperation,
        CosmosResponse, FeedRange, MaxItemCountHint, PartitionKey, ResponseBody, SessionToken,
    },
    options::{FullTextScoreScope, OperationOptions, PlanOptions},
};
use pyo3::{
    exceptions::{
        PyNotImplementedError, PyRuntimeError, PyTimeoutError, PyTypeError, PyValueError,
    },
    prelude::*,
    types::{PyDict, PyInt, PyTuple},
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
    response::{tuple_from_feed_result, with_attempt_diagnostics},
    AbortOnDrop,
};
use super::{partition_key_input::BindingPartitionKey, query::QueryTarget};
use crate::runtime::require_runtime_context;

struct Progress {
    plan: OperationPlan,
    container: ContainerReference,
    identity: (String, String),
    continuation: Option<String>,
    request: FeedRequest,
    service_continuation: bool,
}

#[derive(Clone, PartialEq)]
enum FeedRequest {
    ReadAll,
    ChangeFeed(ChangeFeedRequest),
    Query(QueryRequest),
}

#[derive(Clone, PartialEq)]
struct QueryRequest {
    body: Vec<u8>,
    partition_key: Option<PartitionKey>,
    feed_range: Option<(String, String)>,
    allow_cross_partition: bool,
    continuation_limit_kb: Option<i64>,
    max_buffered_query_window: Option<u64>,
    full_text_score_scope: FullTextScoreScope,
    max_item_count: Option<MaxItemCountHint>,
    hybrid_search_max_items: Option<String>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct QueryAdmissionPlan {
    hybrid_search_query_info: Option<HybridLimitWindow>,
    query_info: Option<QueryAggregateInfo>,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct QueryAggregateInfo {
    #[serde(default, deserialize_with = "query_plan_bool")]
    has_select_value: bool,
    #[serde(default)]
    aggregates: Vec<String>,
    #[serde(default)]
    group_by_expressions: Vec<String>,
}

fn query_plan_bool<'de, D: serde::Deserializer<'de>>(deserializer: D) -> Result<bool, D::Error> {
    // Gateway plans use booleans; native query-plan metadata uses 0/1.
    #[derive(Deserialize)]
    #[serde(untagged)]
    enum Value {
        Bool(bool),
        Integer(i64),
    }
    Ok(match Value::deserialize(deserializer)? {
        Value::Bool(value) => value,
        Value::Integer(value) => value != 0,
    })
}

impl QueryAdmissionPlan {
    fn is_value_average(&self) -> bool {
        self.query_info.as_ref().is_some_and(|info| {
            info.has_select_value
                && matches!(info.aggregates.as_slice(), [aggregate] if aggregate == "Average" || aggregate == "Avg")
                && info.group_by_expressions.is_empty()
        })
    }
}

#[derive(Deserialize)]
struct HybridLimitWindow {
    skip: Option<u64>,
    take: Option<u64>,
}

impl HybridLimitWindow {
    fn admitted_window(&self, maximum: &str) -> PyResult<u64> {
        let take = self.take.filter(|take| *take != 0).ok_or_else(|| {
            PyValueError::new_err(
                "Executing a hybrid search query without TOP or LIMIT can consume many \
                 RUs very fast and have long runtimes. Please ensure you are using one \
                 of the two filters with your hybrid search query.",
            )
        })?;
        Python::with_gil(|py| {
            let maximum = py.get_type_bound::<PyInt>().call1((maximum,))?;
            if maximum.lt(take)? {
                return Err(PyValueError::new_err(
                    "Executing a hybrid search query with more items than the max is not allowed. \
                     Please ensure you are using a limit smaller than the max, or change the max.",
                ));
            }
            Ok(())
        })?;
        self.skip
            .unwrap_or(0)
            .checked_add(take)
            .ok_or_else(|| PyValueError::new_err("Hybrid search OFFSET plus take exceeds u64."))
    }
}

fn decode_query_admission_plan(body: &[u8]) -> Result<QueryAdmissionPlan, CosmosError> {
    serde_json::from_slice::<QueryAdmissionPlan>(body).map_err(|error| {
        CosmosError::builder()
            .with_status(status_codes::SERIALIZATION_RESPONSE_BODY_INVALID)
            .with_message("Invalid query plan while checking query admission")
            .with_source(error)
            .build()
    })
}

async fn query_admission_plan(
    driver: &CosmosDriver,
    container: ContainerReference,
    operation: &CosmosOperation,
    options: &OperationOptions,
) -> Result<QueryAdmissionPlan, CosmosError> {
    // Match the pinned driver's production feature set. The public driver
    // interface does not expose the resolved plan's hybrid metadata.
    let plan_operation = CosmosOperation::query_plan(
        container,
        std::borrow::Cow::Borrowed(
            "Distinct,HybridSearch,MultipleOrderBy,NonStreamingOrderBy,OffsetAndLimit,OrderBy,Top,WeightedRankFusion",
        ),
    )
    .with_body(operation.body().unwrap_or_default().to_vec());
    let response = driver
        .execute_operation(plan_operation, options.clone())
        .await?;
    match response.as_ref().map(CosmosResponse::body) {
        Some(ResponseBody::Bytes(body)) => decode_query_admission_plan(body),
        _ => Err(CosmosError::builder()
            .with_status(status_codes::SERIALIZATION_RESPONSE_BODY_INVALID)
            .with_message("Missing query plan body while checking query admission")
            .build()),
    }
}

fn query_page_size(value: Option<i64>) -> PyResult<Option<MaxItemCountHint>> {
    match value {
        None => Ok(None),
        Some(-1) => Ok(Some(MaxItemCountHint::ServerDecides)),
        Some(value) => u32::try_from(value)
            .ok()
            .and_then(NonZeroU32::new)
            .map(|count| Some(MaxItemCountHint::Limit(count)))
            .ok_or_else(|| PyValueError::new_err("max_item_count must be -1 or a positive u32.")),
    }
}

fn query_planning_error(error: CosmosError, maximum: Option<u64>) -> PyResult<CosmosError> {
    if maximum.is_some()
        && error.status() == status_codes::CLIENT_BUFFERED_QUERY_REQUIRES_FINITE_WINDOW
    {
        return Err(PyValueError::new_err(
            "Executing a vector search query with more items than the max is not allowed. \
             Please ensure you are using a limit smaller than the max, or change the max.",
        ));
    }
    Ok(error)
}

fn feed_range_from_bounds(min: &str, max: &str) -> Result<FeedRange, CosmosError> {
    FeedRange::new(min.try_into()?, max.try_into()?)
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
            (None, Some((min, max))) => feed_range_from_bounds(min, max)
                .map_err(|error| PyValueError::new_err(error.to_string()))?,
            (None, None) => FeedRange::full(),
            _ => {
                return Err(PyValueError::new_err(
                    "partition_key and feed_range are exclusive",
                ))
            }
        };
        let mut operation =
            CosmosOperation::query_items(container, Some(range)).with_body(self.body.clone());
        if let Some(count) = self.max_item_count {
            operation = operation.with_max_item_count(count);
        }
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
            Some((min, max)) => feed_range_from_bounds(min, max)
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
            None | Some(0) => Err(PyRuntimeError::new_err(
                "Could not resolve the change-feed scope",
            )),
            Some(_) => Err(PyNotImplementedError::new_err(
                "The Python Rust binding does not support multi-partition change-feed scopes: \
                 complete polling and checkpoint guarantees are not implemented here. \
                 Use a single-partition scope. No fallback was performed.",
            )),
        }
    }

    fn operation(&self, container: ContainerReference) -> PyResult<CosmosOperation> {
        let range = match (&self.partition_key, &self.feed_range) {
            (Some(key), None) => {
                FeedRange::for_partition(key.clone(), container.partition_key_definition())
            }
            (None, Some((min, max))) => feed_range_from_bounds(min, max)
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
    published_status: Arc<AtomicU8>,
}

/// Binding feed cursor retained by a Python page iterator.
/// In-flight fetches retain their own reference to its state, so dropping the
/// Python reference need not immediately release the Rust driver's plan.
#[pyclass(name = "_ItemFeedCursor", module = "azure.cosmos._rust")]
pub(crate) struct ItemFeedCursor {
    state: Arc<Mutex<CursorState>>,
    published_status: Arc<AtomicU8>,
}

impl Default for ItemFeedCursor {
    fn default() -> Self {
        let state = CursorState::default();
        Self {
            published_status: state.published_status.clone(),
            state: Arc::new(Mutex::new(state)),
        }
    }
}

#[pymethods]
impl ItemFeedCursor {
    #[new]
    fn new() -> Self {
        Self::default()
    }

    #[getter]
    fn has_more(&self) -> bool {
        self.published_status.load(Ordering::Acquire) & 1 != 0
    }

    #[getter]
    fn continuation_supported(&self) -> bool {
        self.published_status.load(Ordering::Acquire) & 2 == 0
    }

    #[getter]
    /// Whether execution has not started and the state is currently available.
    /// The Python wrapper applies additional retry checks; this is not permission
    /// to retry every timeout or cancellation.
    fn can_retry_setup(&self) -> bool {
        self.state.try_lock().is_ok_and(|state| !state.started)
    }
}

type PageResult = (
    Result<Option<CosmosResponse>, CosmosError>,
    Option<String>,
    bool,
);

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
        PlanOptions::default()
            .with_query_plan_mode(azure_data_cosmos_driver::options::QueryPlanMode::GatewayOnly),
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
    plan_options: PlanOptions,
) -> PyResult<PageResult> {
    let mut state = state
        .try_lock()
        .map_err(|_| PyRuntimeError::new_err("Concurrent use of a retained feed cursor"))?;
    // Take ownership before awaiting. A cancelled/failed fetch must not leave a
    // partly advanced plan available for another fetch to skip undelivered rows.
    let progress = state.progress.take();
    // Successful resolution and planning do not return diagnostics through this
    // path, so the first execution cannot describe the complete fetch.
    // Change-feed scope checks also omit diagnostics on later fetches.
    let diagnostics_complete =
        progress.is_some() && !matches!(&request, FeedRequest::ChangeFeed(_));
    if state.started && progress.is_none() {
        return Err(PyRuntimeError::new_err(
            "Feed cursor failed; resume using the last delivered continuation token",
        ));
    }
    modifiers
        .custom_headers
        .retain(|name, _| name.as_str() != "x-ms-continuation");
    let options = build_operation_options(
        None,
        modifiers.excluded_regions_value,
        modifiers.driver_timeout_policy,
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
            Err(error) => return Ok((Err(error), None, false)),
        };
        if let FeedRequest::ChangeFeed(request) = &request {
            let width = match request.scope_width(&driver, &container).await? {
                Ok(width) => width,
                Err(error) => return Ok((Err(error), None, false)),
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
        let service_continuation =
            matches!(request, FeedRequest::Query(_)) && operation.is_trivial();
        let mut maximum = match &request {
            FeedRequest::Query(query) => query.max_buffered_query_window,
            _ => None,
        };
        let mut hybrid_limit_applied = false;
        let mut range_average = false;
        if let FeedRequest::Query(query) = &request {
            if !operation.is_trivial()
                && (query.hybrid_search_max_items.is_some() || query.feed_range.is_some())
            {
                let admission =
                    match query_admission_plan(&driver, container.clone(), &operation, &options)
                        .await
                    {
                        Ok(plan) => plan,
                        Err(error) => return Ok((Err(error), None, false)),
                    };
                range_average = query.feed_range.is_some() && admission.is_value_average();
                if let (Some(window), Some(limit)) = (
                    admission.hybrid_search_query_info,
                    query.hybrid_search_max_items.as_deref(),
                ) {
                    maximum = Some(window.admitted_window(limit)?);
                    hybrid_limit_applied = true;
                }
            }
        }
        let plan_options = match maximum {
            Some(maximum) => plan_options.with_max_buffered_query_window(maximum),
            None => plan_options,
        };
        let plan_options = match &request {
            FeedRequest::Query(query) => {
                // Legacy Python has no query fan-out cap; keep that policy in the binding.
                plan_options
                    .with_max_fan_out(u32::MAX)
                    .with_full_text_score_scope(query.full_text_score_scope)
            }
            _ => plan_options,
        };
        let token = continuation.map(ContinuationToken::from_string);
        let plan = match driver
            .plan_operation(operation, &options, token.as_ref(), &plan_options)
            .await
        {
            Ok(plan) => plan,
            Err(error) => {
                if range_average && error.status() == status_codes::CLIENT_UNSUPPORTED_QUERY_FEATURE
                {
                    if let FeedRequest::Query(query) = &request {
                        if let Some((min, max)) = &query.feed_range {
                            let scope = feed_range_from_bounds(min, max)
                                .map_err(|error| PyValueError::new_err(error.to_string()))?;
                            let ranges = match driver
                                .resolve_all_partition_key_ranges(&container, false)
                                .await
                            {
                                Ok(Some(ranges)) => ranges,
                                Ok(None) => {
                                    return Err(PyRuntimeError::new_err(
                                        "Could not resolve the query scope",
                                    ))
                                }
                                Err(error) => return Ok((Err(error), None, false)),
                            };
                            let width = ranges
                                .iter()
                                .filter(|range| {
                                    range.max_exclusive > *scope.min_inclusive()
                                        && range.min_inclusive < *scope.max_exclusive()
                                })
                                .count();
                            if width > 1 {
                                return Err(PyValueError::new_err(
                                    "Unsupported query shape for range-scoped pagination: \
                                     SELECT VALUE AVG(...) cannot be merged client-side when the query \
                                     scope spans multiple physical partitions.",
                                ));
                            }
                        }
                    }
                }
                let vector_maximum = if hybrid_limit_applied { None } else { maximum };
                return Ok((
                    Err(query_planning_error(error, vector_maximum)?),
                    None,
                    false,
                ));
            }
        };
        Progress {
            plan,
            container,
            identity,
            continuation: None,
            request,
            service_continuation,
        }
    };
    // Before execution starts, a later fetch can repeat setup. Execution may
    // advance the Rust driver's plan even on failure or cancellation; do not
    // restore that potentially advanced plan for another fetch.
    state.started = true;
    let response = match driver
        .execute_plan(
            &mut progress.plan,
            Some(progress.container.clone()),
            options,
        )
        .await
    {
        Ok(response) => response,
        Err(error) => return Ok((Err(error), None, diagnostics_complete)),
    };
    // Split recovery may expand a previously safe scope. Do not publish a
    // continuation token or an empty poll covering only one of its children.
    if let FeedRequest::ChangeFeed(request) = &progress.request {
        let width = match request.scope_width(&driver, &progress.container).await? {
            Ok(width) => width,
            Err(error) => return Ok((Err(error), None, false)),
        };
        ChangeFeedRequest::validate_width(width)?;
    }
    let token = if response.is_some() && !state.continuation_unsupported {
        match progress.plan.to_continuation_token() {
            Ok(_) if progress.service_continuation => response
                .as_ref()
                .and_then(|page| page.headers().continuation.clone()),
            Ok(token) => Some(token.as_str().to_owned()),
            Err(error)
                if matches!(progress.request, FeedRequest::Query(_))
                    && error.status()
                        == status_codes::CLIENT_BUFFERED_QUERY_CONTINUATION_UNSUPPORTED =>
            {
                state.continuation_unsupported = true;
                // Ranked queries can buffer results even with a complete partition key.
                progress.service_continuation = false;
                None
            }
            Err(error) => return Ok((Err(error), None, false)),
        }
    } else {
        None
    };
    progress.continuation = token.clone();
    state.has_more = response.is_some() && (!progress.service_continuation || token.is_some());
    state.progress = if response.is_some() {
        Some(progress)
    } else {
        None
    };
    // Properties describe the last completed page, even during another fetch.
    state.published_status.store(
        u8::from(state.has_more) | (u8::from(state.continuation_unsupported) << 1),
        Ordering::Release,
    );
    Ok((Ok(response), token, diagnostics_complete))
}

fn feed_inputs(prepared: &Bound<'_, PyAny>, scope: BindingPartitionKey) -> PyResult<FeedRequest> {
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
    let body = super::request::extract_body_bytes(prepared)?;
    if op == "query_items" {
        let scope = prepared.getattr("query_scope")?;
        if scope.is_none() {
            return Err(PyTypeError::new_err(
                "Retained queries require typed query_scope",
            ));
        }
        let query_settings = prepared.getattr("settings")?.getattr("query")?;
        let full_text_score_scope = match query_settings
            .getattr("full_text_score_scope")?
            .extract::<Option<String>>()?
            .as_deref()
        {
            None | Some("Global") => FullTextScoreScope::Global,
            Some("Local") => FullTextScoreScope::Local,
            _ => {
                return Err(PyValueError::new_err(
                    "full_text_score_scope must be 'Local' or 'Global'.",
                ))
            }
        };
        return Ok(FeedRequest::Query(QueryRequest {
            body,
            partition_key: key,
            feed_range: scope.getattr("feed_range")?.extract()?,
            allow_cross_partition: scope.getattr("allow_cross_partition")?.extract()?,
            continuation_limit_kb: prepared
                .getattr("settings")?
                .getattr("query")?
                .getattr("continuation_limit_kb")?
                .extract()?,
            max_buffered_query_window: prepared
                .getattr("settings")?
                .getattr("query")?
                .getattr("max_buffered_query_window")?
                .extract()?,
            full_text_score_scope,
            max_item_count: query_page_size(query_settings.getattr("max_item_count")?.extract()?)?,
            hybrid_search_max_items: query_settings
                .getattr("hybrid_search_max_items")?
                .extract()?,
        }));
    }
    match op.as_str() {
        "query_items_change_feed" => {
            serde_json::from_slice::<ChangeFeedRequest>(&body).map(|mut request| {
                request.partition_key = key;
                FeedRequest::ChangeFeed(request)
            })
        }
        _ => return Err(PyValueError::new_err("Unsupported retained feed operation")),
    }
    .map_err(|error| PyValueError::new_err(format!("Invalid retained feed request: {error}")))
}

fn finish_page<'py>(
    py: Python<'py>,
    result: PageResult,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    let (result, continuation, complete) = result;
    let diagnostics = if include_attempts {
        match &result {
            Ok(Some(response)) => Some(response.diagnostics()),
            Err(error) => error.diagnostics(),
            Ok(None) => None,
        }
    } else {
        None
    };
    let response = (|| {
        let tuple = tuple_from_feed_result(py, result)?;
        let headers = tuple.get_item(2)?;
        let headers = headers.downcast::<PyDict>()?;
        if let Some(token) = continuation {
            headers.set_item("x-ms-continuation", token)?;
        } else if headers.contains("x-ms-continuation")? {
            headers.del_item("x-ms-continuation")?;
        }
        Ok(tuple)
    })();
    if include_attempts {
        let coverage = if complete {
            super::response::AttemptCoverage::Complete
        } else {
            super::response::AttemptCoverage::Incomplete("feed_preparation_diagnostics_unavailable")
        };
        with_attempt_diagnostics(py, response, diagnostics, coverage)
    } else {
        response
    }
}

fn inputs(
    prepared: &Bound<'_, PyAny>,
) -> PyResult<(
    String,
    RequestHeadersAndOptions,
    Option<String>,
    BindingPartitionKey,
)> {
    let (link, scope, modifiers) = extract_common_prepared_inputs(prepared)?;
    let continuation: Option<String> = prepared
        .getattr("settings")?
        .getattr("query")?
        .getattr("continuation")?
        .extract()?;
    let op: String = prepared.getattr("op")?.extract()?;
    if op != "query_items"
        && continuation
            .as_ref()
            .is_some_and(|token| !token.starts_with("c1.") && !token.starts_with("c2."))
    {
        return Err(PyValueError::new_err(
            "read_all_items requires a Rust driver continuation token, not a legacy bookmark",
        ));
    }
    Ok((link, modifiers, continuation, scope))
}

#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, cursor, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn fetch_page_with_cursor<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    prepared: &Bound<'py, PyAny>,
    cursor: PyRef<'py, ItemFeedCursor>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyTuple>> {
    let (link, modifiers, token, scope) = inputs(prepared)?;
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    let request = feed_inputs(prepared, scope)?;
    BINDING_OP_COUNT.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let state = cursor.state.clone();
    let identity = (driver_handle.cache_key().to_owned(), link);
    let runtime = require_runtime_context("fetch_page_with_cursor")?;
    let future = page_timeout(
        timeout,
        next_plan_page(
            driver,
            state,
            identity,
            token,
            modifiers,
            request,
            PlanOptions::default(),
        ),
    );
    let result = py.allow_threads(|| runtime.tokio_rt.block_on(future))??;
    finish_page(py, result, include_attempts)
}

#[pyfunction]
#[pyo3(signature = (driver_handle, prepared, cursor, *, timeout_seconds=None, include_attempts=false))]
pub(crate) fn fetch_page_with_cursor_async<'py>(
    py: Python<'py>,
    driver_handle: &crate::runtime::DriverHandle,
    prepared: &Bound<'py, PyAny>,
    cursor: PyRef<'py, ItemFeedCursor>,
    timeout_seconds: Option<f64>,
    include_attempts: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let (link, modifiers, token, scope) = inputs(prepared)?;
    let timeout = parse_remaining_timeout(timeout_seconds)?;
    let request = feed_inputs(prepared, scope)?;
    BINDING_OP_COUNT.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let state = cursor.state.clone();
    let identity = (driver_handle.cache_key().to_owned(), link);
    let runtime = require_runtime_context("fetch_page_with_cursor_async")?;
    let future = page_timeout(
        timeout,
        next_plan_page(
            driver,
            state,
            identity,
            token,
            modifiers,
            request,
            PlanOptions::default(),
        ),
    );
    let join = runtime.tokio_rt.spawn(future);
    let abort = AbortOnDrop(join.abort_handle());
    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort = abort;
        let result = join
            .await
            .map_err(|error| PyRuntimeError::new_err(error.to_string()))???;
        Python::with_gil(|py| {
            finish_page(py, result, include_attempts).map(|value| value.into_any().unbind())
        })
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
        fault_injection::{
            CustomResponseBuilder, FaultInjectionConditionBuilder, FaultInjectionResultBuilder,
            FaultInjectionRule, FaultInjectionRuleBuilder,
        },
        in_memory_emulator::{
            ContainerConfig, InMemoryEmulatorHttpClient, VirtualAccountConfig, VirtualRegion,
        },
        models::{AccountReference, ItemReference, PartitionKey, PartitionKeyDefinition},
        options::{
            ContentResponseOnWrite, DriverOptions, EndToEndOperationLatencyPolicy, QueryPlanMode,
        },
    };
    use std::{
        borrow::Cow,
        collections::{BTreeSet, HashMap},
        time::Duration,
    };

    #[test]
    fn explicit_feed_bounds_preserve_valid_hex_and_reject_invalid_values() {
        let full = feed_range_from_bounds("", "ff").unwrap();
        assert_eq!(full, FeedRange::full());
        let range = feed_range_from_bounds("3f00", "7f00").unwrap();
        assert_eq!(range.min_inclusive().to_hex(), "3F00");
        assert_eq!(range.max_exclusive().to_hex(), "7F00");
        for (min, max) in [
            ("3", "7F"),
            ("GG", "7F"),
            ("3F", "7"),
            ("3F", "GG"),
            ("7F", "3F"),
        ] {
            assert!(feed_range_from_bounds(min, max).is_err());
        }
    }

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
        setup_with_fault_rules(count, definition, Vec::new()).await
    }

    async fn setup_with_fault_rules(
        count: usize,
        definition: PartitionKeyDefinition,
        rules: Vec<Arc<FaultInjectionRule>>,
    ) -> (Arc<InMemoryEmulatorHttpClient>, Arc<CosmosDriver>) {
        setup_with_partition_count(count, definition, rules, 3).await
    }

    async fn setup_with_partition_count(
        count: usize,
        definition: PartitionKeyDefinition,
        rules: Vec<Arc<FaultInjectionRule>>,
        partition_count: u32,
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
                    .with_partition_count(partition_count)
                    .build()
                    .unwrap(),
            );
        }
        let runtime = emulator.runtime_builder().build().await.unwrap();
        let account = AccountReference::with_account_key(url, "ZW11bGF0b3Ita2V5");
        let driver = runtime
            .create_driver(
                DriverOptions::builder(account)
                    .with_partition_failover_options(
                        crate::runtime::partition_failover_options().unwrap(),
                    )
                    .with_fault_injection_rules(rules)
                    .unwrap()
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
            driver_timeout_policy: Some(EndToEndOperationLatencyPolicy::new(Duration::from_secs(
                1,
            ))),
            operation_timeout: None,
            availability_strategy: None,
            read_consistency_strategy: None,
            patch_strategy: None,
            custom_headers: HashMap::from([(
                HeaderName::from_static("x-ms-max-item-count"),
                HeaderValue::from_static("2"),
            )]),
        }
    }

    #[tokio::test]
    async fn retained_fetch_diagnostics_preserve_pages_and_mark_initial_setup_incomplete() {
        let (_emulator, driver) = setup(7).await;
        let cursor = ItemFeedCursor::default();
        let mut token = None;
        let mut fetches = 0;
        loop {
            let result = next_page(
                driver.clone(),
                cursor.state.clone(),
                ("test".into(), "dbs/db/colls/c".into()),
                token,
                modifiers(),
            )
            .await
            .unwrap();
            assert_eq!(result.2, fetches != 0);
            let exhausted = result.0.as_ref().unwrap().is_none();
            token = result.1.clone();
            Python::with_gil(|py| {
                let ordinary = finish_page(py, result.clone(), false).unwrap();
                let envelope = finish_page(py, result, true).unwrap();
                assert_eq!(envelope.len(), 2);
                assert!(envelope.get_item(0).unwrap().eq(&ordinary).unwrap());
                let payload = envelope.get_item(1).unwrap();
                assert_eq!(payload.is_none(), exhausted);
                if !exhausted {
                    if fetches == 0 {
                        assert!(!payload
                            .get_item("complete")
                            .unwrap()
                            .extract::<bool>()
                            .unwrap());
                    } else {
                        assert!(payload
                            .get_item("complete")
                            .unwrap()
                            .extract::<bool>()
                            .unwrap());
                        assert!(payload
                            .get_item("incomplete_reasons")
                            .unwrap()
                            .extract::<Vec<String>>()
                            .unwrap()
                            .is_empty());
                    }
                    let headers = ordinary.get_item(2).unwrap();
                    assert_eq!(
                        headers
                            .get_item("x-ms-continuation")
                            .unwrap()
                            .extract::<String>()
                            .unwrap(),
                        token.clone().unwrap()
                    );
                } else {
                    assert!(!ordinary
                        .get_item(2)
                        .unwrap()
                        .contains("x-ms-continuation")
                        .unwrap());
                }
            });
            fetches += 1;
            if exhausted {
                break;
            }
            assert!(fetches < 100);
        }
        assert!(fetches > 2);
    }

    #[tokio::test]
    async fn retained_fetch_attempt_envelope_preserves_errors() {
        let (_emulator, driver) = setup(1).await;
        let first = next_page(
            driver,
            ItemFeedCursor::default().state,
            ("test".into(), "dbs/db/colls/c".into()),
            None,
            modifiers(),
        )
        .await
        .unwrap();
        let diagnostics = first.0.unwrap().unwrap().diagnostics();
        Python::with_gil(|py| {
            for status in [
                status_codes::CLIENT_UNSUPPORTED_QUERY_FEATURE,
                azure_data_cosmos_driver::error::CosmosStatus::new(
                    azure_core::http::StatusCode::RequestTimeout,
                ),
                azure_data_cosmos_driver::error::CosmosStatus::new(
                    azure_core::http::StatusCode::RequestTimeout,
                )
                .with_sub_status(status_codes::substatus::CLIENT_OPERATION_TIMEOUT.value()),
            ] {
                for complete in [false, true] {
                    for include_diagnostics in [false, true] {
                        let mut builder = CosmosError::builder().with_status(status);
                        if include_diagnostics {
                            builder = builder.with_diagnostics(diagnostics.clone());
                        }
                        let error = builder.build();
                        let ordinary = finish_page(py, (Err(error.clone()), None, complete), false)
                            .unwrap_err();
                        let recorded =
                            finish_page(py, (Err(error), None, complete), true).unwrap_err();
                        assert!(ordinary.get_type_bound(py).is(&recorded.get_type_bound(py)));
                        assert_eq!(ordinary.to_string(), recorded.to_string());
                        let payload = recorded.value_bound(py).getattr("_cosmos_attempt_payload");
                        if include_diagnostics {
                            let payload = payload.unwrap();
                            assert_eq!(
                                payload
                                    .get_item("request_count")
                                    .unwrap()
                                    .extract::<usize>()
                                    .unwrap(),
                                diagnostics.request_count()
                            );
                            if !complete {
                                assert!(!payload
                                    .get_item("complete")
                                    .unwrap()
                                    .extract::<bool>()
                                    .unwrap());
                            }
                        } else {
                            assert!(payload.is_err());
                        }
                    }
                }
            }
        });
    }

    #[tokio::test]
    async fn cursor_properties_remain_readable_during_a_fetch() {
        let (_emulator, driver) = setup(3).await;
        let cursor = ItemFeedCursor::default();
        assert!(!cursor.has_more());
        assert!(cursor.continuation_supported());
        assert!(cursor.can_retry_setup());
        {
            let _setup_in_flight = cursor.state.lock().await;
            assert!(!cursor.can_retry_setup());
        }
        let (rows, _) = fetch(&driver, &cursor.state, None).await;
        assert!(rows.is_some());
        assert!(!cursor.can_retry_setup());
        let _in_flight = cursor.state.lock().await;
        assert!(cursor.has_more());
        assert!(cursor.continuation_supported());
    }

    #[test]
    fn cursor_status_is_local_to_each_pager_and_reports_unsupported_continuations() {
        let first = ItemFeedCursor::default();
        let second = ItemFeedCursor::default();
        first.published_status.store(3, Ordering::Release);
        let _in_flight = first.state.try_lock().unwrap();
        assert!(first.has_more());
        assert!(!first.continuation_supported());
        assert!(!second.has_more());
        assert!(second.continuation_supported());
        assert!(!first.can_retry_setup());
        assert!(second.can_retry_setup());
    }

    async fn setup_fault(
        operation: &str,
        delay: Duration,
    ) -> (Arc<CosmosDriver>, Arc<FaultInjectionRule>) {
        let rule = Arc::new(
            FaultInjectionRuleBuilder::new(
                "cursor-phase",
                FaultInjectionResultBuilder::new()
                    .with_custom_response(
                        CustomResponseBuilder::new(azure_core::http::StatusCode::BadRequest)
                            .build(),
                    )
                    .with_delay(delay)
                    .build(),
            )
            .with_condition(
                FaultInjectionConditionBuilder::new()
                    .with_operation_type(operation.parse().unwrap())
                    .build(),
            )
            .build(),
        );
        rule.disable();
        let (_emulator, driver) = setup_with_fault_rules(
            0,
            PartitionKeyDefinition::new(vec![Cow::Borrowed("/pk")]),
            vec![rule.clone()],
        )
        .await;
        rule.enable();
        (driver, rule)
    }

    #[tokio::test]
    async fn setup_errors_can_retry_but_execution_errors_invalidate() {
        for operation in ["MetadataReadContainer", "MetadataQueryPlan", "QueryItem"] {
            let (driver, rule) = setup_fault(operation, Duration::ZERO).await;
            let cursor = ItemFeedCursor::default();
            let identity = ("test".into(), "dbs/db/colls/other".into());
            let (result, token, complete) = next_page(
                driver.clone(),
                cursor.state.clone(),
                identity.clone(),
                None,
                modifiers(),
            )
            .await
            .unwrap();
            assert!(result.is_err(), "{operation}");
            assert!(!complete, "{operation}");
            assert!(token.is_none(), "{operation}");
            assert!(rule.hit_count() > 0, "{operation}");
            let setup_failed = operation != "QueryItem";
            assert_eq!(cursor.can_retry_setup(), setup_failed, "{operation}");
            {
                let state = cursor.state.lock().await;
                assert_eq!(state.started, !setup_failed, "{operation}");
                assert!(state.progress.is_none(), "{operation}");
            }
            rule.disable();
            let retry = next_page(driver, cursor.state.clone(), identity, None, modifiers()).await;
            if setup_failed {
                assert!(retry.unwrap().0.is_ok(), "{operation}");
                assert!(!cursor.can_retry_setup(), "{operation}");
            } else {
                let error = retry.err().expect("execution failure must remain terminal");
                assert!(error.to_string().contains("Feed cursor failed"));
            }
        }
    }

    #[tokio::test]
    async fn cancellation_before_execution_does_not_start_cursor() {
        for operation in ["MetadataReadContainer", "MetadataQueryPlan", "QueryItem"] {
            let (driver, rule) = setup_fault(operation, Duration::from_secs(60)).await;
            let cursor = ItemFeedCursor::default();
            let mut options = modifiers();
            options.driver_timeout_policy = None;
            let fetch = tokio::spawn(next_page(
                driver.clone(),
                cursor.state.clone(),
                ("test".into(), "dbs/db/colls/other".into()),
                None,
                options,
            ));
            tokio::time::timeout(Duration::from_secs(5), async {
                while rule.hit_count() == 0 {
                    tokio::task::yield_now().await;
                }
            })
            .await
            .expect("fetch did not reach the injected delay");
            assert!(!cursor.can_retry_setup());
            fetch.abort();
            assert!(fetch.await.unwrap_err().is_cancelled());
            let setup_cancelled = operation != "QueryItem";
            assert_eq!(cursor.can_retry_setup(), setup_cancelled, "{operation}");
            assert_eq!(cursor.state.lock().await.started, !setup_cancelled);
            rule.disable();
            let retry = next_page(
                driver,
                cursor.state.clone(),
                ("test".into(), "dbs/db/colls/other".into()),
                None,
                modifiers(),
            )
            .await;
            if setup_cancelled {
                assert!(retry.unwrap().0.is_ok(), "{operation}");
            } else {
                assert!(retry
                    .err()
                    .unwrap()
                    .to_string()
                    .contains("Feed cursor failed"));
            }
        }
    }

    async fn fetch(
        driver: &Arc<CosmosDriver>,
        state: &Arc<Mutex<CursorState>>,
        token: Option<String>,
    ) -> (Option<Vec<String>>, Option<String>) {
        let (response, token, _) = next_page(
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
            body: serde_json::to_vec(&serde_json::json!({"query": sql})).unwrap(),
            partition_key: None,
            feed_range: None,
            allow_cross_partition: true,
            continuation_limit_kb: None,
            max_buffered_query_window: None,
            full_text_score_scope: FullTextScoreScope::Global,
            max_item_count: None,
            hybrid_search_max_items: None,
        })
    }

    #[tokio::test]
    async fn queries_cover_more_than_one_hundred_partitions() {
        let expected: BTreeSet<_> = (0..150).map(|i| i.to_string()).collect();
        for partition_count in [100, 101, 150] {
            let (_emulator, driver) = setup_with_partition_count(
                expected.len(),
                PartitionKeyDefinition::new(vec![Cow::Borrowed("/pk")]),
                Vec::new(),
                partition_count,
            )
            .await;
            let container = driver
                .resolve_container("db", "c", Default::default())
                .await
                .unwrap();
            let ranges = driver
                .resolve_all_partition_key_ranges(&container, false)
                .await
                .unwrap()
                .unwrap();
            assert_eq!(ranges.len(), partition_count as usize);
            let plan_options =
                PlanOptions::default().with_query_plan_mode(QueryPlanMode::GatewayOnly);
            let direct = driver
                .plan_operation(
                    CosmosOperation::query_items(container, Some(FeedRange::full()))
                        .with_body(br#"{"query":"SELECT * FROM c"}"#.to_vec()),
                    &Default::default(),
                    None,
                    &plan_options,
                )
                .await;
            if partition_count == 100 {
                assert!(direct.is_ok());
            } else {
                assert_eq!(
                    direct
                        .err()
                        .expect("driver default must retain its cap")
                        .status(),
                    status_codes::CLIENT_CROSS_PARTITION_FAN_OUT_EXCEEDED,
                );
                let (response, _, _) = next_plan_page(
                    driver.clone(),
                    Arc::new(Mutex::new(CursorState::default())),
                    ("test".into(), "dbs/db/colls/c".into()),
                    None,
                    modifiers(),
                    FeedRequest::ReadAll,
                    plan_options,
                )
                .await
                .unwrap();
                assert_eq!(
                    response.unwrap_err().status(),
                    status_codes::CLIENT_CROSS_PARTITION_FAN_OUT_EXCEEDED,
                    "the query override must not change read-all policy",
                );
            }

            for explicit_range in [false, true] {
                let mut request = query_request("SELECT * FROM c");
                if let FeedRequest::Query(ref mut query) = request {
                    if explicit_range {
                        query.feed_range = Some(("".into(), "FF".into()));
                    }
                }
                let mut state = Arc::new(Mutex::new(CursorState::default()));
                let mut token = None;
                let mut ids = Vec::new();
                let mut responses = 0;
                let mut exhausted = false;
                for _ in 0..partition_count as usize + expected.len() + 1 {
                    let (rows, next) = query_page(&driver, &state, &request, token).await;
                    token = next;
                    let Some(rows) = rows else {
                        exhausted = true;
                        assert!(!state.lock().await.has_more);
                        break;
                    };
                    responses += 1;
                    ids.extend(
                        rows.iter()
                            .map(|row| row["id"].as_str().unwrap().to_owned()),
                    );
                    if explicit_range && responses == 10 {
                        assert!(token.is_some(), "resuming must not restart the query");
                        state = Arc::new(Mutex::new(CursorState::default()));
                    }
                }
                assert!(
                    exhausted,
                    "{partition_count}, explicit_range={explicit_range}"
                );
                assert!(responses >= partition_count as usize);
                assert_eq!(ids.len(), expected.len(), "no missing or duplicate items");
                assert_eq!(ids.into_iter().collect::<BTreeSet<_>>(), expected);
            }
        }
    }

    #[test]
    fn configured_buffer_guard_maps_only_its_typed_planning_error() {
        pyo3::prepare_freethreaded_python();
        for maximum in [None, Some(0), Some(1), Some(50_000)] {
            for status in [
                status_codes::CLIENT_BUFFERED_QUERY_REQUIRES_FINITE_WINDOW,
                status_codes::CLIENT_BUFFERED_QUERY_CONTINUATION_UNSUPPORTED,
            ] {
                let error = CosmosError::builder()
                    .with_status(status)
                    .with_message("original driver message")
                    .build();
                let result = query_planning_error(error, maximum);
                if maximum.is_some()
                    && status == status_codes::CLIENT_BUFFERED_QUERY_REQUIRES_FINITE_WINDOW
                {
                    let error = result.unwrap_err();
                    Python::with_gil(|py| {
                        assert!(error.is_instance_of::<PyValueError>(py));
                        assert_eq!(
                            error.value_bound(py).getattr("args").unwrap().get_item(0).unwrap().extract::<String>().unwrap(),
                            "Executing a vector search query with more items than the max is not allowed. \
                             Please ensure you are using a limit smaller than the max, or change the max."
                        );
                    });
                } else {
                    assert_eq!(result.unwrap().status(), status);
                }
            }
        }
    }

    #[test]
    fn range_average_uses_plan_shape_not_sql_text() {
        let average = decode_query_admission_plan(
            br#"{"queryInfo":{"hasSelectValue":true,"aggregates":["Average"],"groupByExpressions":[]}}"#,
        ).unwrap();
        assert!(average.is_value_average());
        assert!(decode_query_admission_plan(
            br#"{"queryInfo":{"hasSelectValue":1,"aggregates":["Average"],"groupByExpressions":[]}}"#,
        ).unwrap().is_value_average());
        assert!(decode_query_admission_plan(
            br#"{"queryInfo":{"hasSelectValue":true,"aggregates":["Avg"]}}"#,
        )
        .unwrap()
        .is_value_average());
        for body in [
            br#"{"queryInfo":{"hasSelectValue":true,"aggregates":["Count"]}}"#.as_slice(),
            br#"{"queryInfo":{"hasSelectValue":false,"aggregates":["Average"]}}"#,
            br#"{"queryInfo":{"hasSelectValue":0,"aggregates":["Average"]}}"#,
            br#"{"queryInfo":{"hasSelectValue":true,"aggregates":["Average","Sum"]}}"#,
            br#"{"queryInfo":{"hasSelectValue":true,"aggregates":["Average"],"groupByExpressions":["c.pk"]}}"#,
            br#"{"queryInfo":{"hasSelectValue":true,"aggregates":[]}}"#,
            br#"{}"#,
        ] {
            assert!(!decode_query_admission_plan(body).unwrap().is_value_average());
        }
    }

    #[tokio::test]
    async fn average_error_contract_is_limited_to_multi_partition_feed_ranges() {
        let (_emulator, driver) = setup(12).await;
        let container = driver
            .resolve_container("db", "c", Default::default())
            .await
            .unwrap();
        let ranges = driver
            .resolve_all_partition_key_ranges(&container, false)
            .await
            .unwrap()
            .unwrap();
        let single = &ranges[0];
        for (scope, sql, legacy_error) in [
            (
                Some(("".into(), "FF".into())),
                "SELECT VALUE AVG(c.value) FROM c",
                true,
            ),
            (
                Some((single.min_inclusive.to_hex(), single.max_exclusive.to_hex())),
                "SELECT VALUE AVG(c.value) FROM c",
                false,
            ),
            (None, "SELECT VALUE AVG(c.value) FROM c", false),
            (
                Some(("".into(), "FF".into())),
                "SELECT VALUE SUM(c.value) FROM c",
                false,
            ),
        ] {
            let mut request = query_request(sql);
            if let FeedRequest::Query(ref mut query) = request {
                query.feed_range = scope;
            }
            let result = next_plan_page(
                driver.clone(),
                Arc::new(Mutex::new(CursorState::default())),
                ("test".into(), "dbs/db/colls/c".into()),
                None,
                modifiers(),
                request,
                PlanOptions::default(),
            )
            .await;
            if legacy_error {
                let error = result.unwrap_err();
                Python::with_gil(|py| assert!(error.is_instance_of::<PyValueError>(py)));
                assert!(error
                    .to_string()
                    .contains("SELECT VALUE AVG(...) cannot be merged"));
            } else {
                let (result, _, _) = result.unwrap();
                assert_eq!(
                    result.unwrap_err().status(),
                    status_codes::CLIENT_UNSUPPORTED_QUERY_FEATURE
                );
            }
        }
    }

    #[test]
    fn hybrid_limit_uses_plan_metadata_and_legacy_take_not_offset_window() {
        pyo3::prepare_freethreaded_python();
        for body in [
            br#"{"queryInfo":{"top":1}}"#.as_slice(),
            br#"{"queryInfo":{"top":1,"hasNonStreamingOrderBy":true}}"#,
            br#"{"hybridSearchQueryInfo":null}"#,
        ] {
            assert!(decode_query_admission_plan(body)
                .unwrap()
                .hybrid_search_query_info
                .is_none());
        }
        let plan =
            decode_query_admission_plan(br#"{"hybridSearchQueryInfo":{"skip":1000,"take":5}}"#)
                .unwrap()
                .hybrid_search_query_info
                .unwrap();
        for maximum in ["5", "  +5 ", "5_000", "1267650600228229401496703205376"] {
            assert_eq!(plan.admitted_window(maximum).unwrap(), 1005);
        }
        for maximum in ["0", "4", "-1"] {
            let error = plan.admitted_window(maximum).unwrap_err();
            Python::with_gil(|py| {
                assert!(error.is_instance_of::<PyValueError>(py));
                assert_eq!(
                    error
                        .value_bound(py)
                        .getattr("args")
                        .unwrap()
                        .get_item(0)
                        .unwrap()
                        .extract::<String>()
                        .unwrap(),
                    "Executing a hybrid search query with more items than the max is not allowed. \
                     Please ensure you are using a limit smaller than the max, or change the max."
                );
            });
        }
        for maximum in ["", "invalid", "1.5"] {
            let error = plan.admitted_window(maximum).unwrap_err();
            Python::with_gil(|py| assert!(error.is_instance_of::<PyValueError>(py)));
        }
        for take in [None, Some(0)] {
            let error = HybridLimitWindow { skip: None, take }
                .admitted_window("10")
                .unwrap_err();
            assert!(error.to_string().contains("without TOP or LIMIT"));
        }
        assert!(HybridLimitWindow {
            skip: Some(u64::MAX),
            take: Some(1)
        }
        .admitted_window("1")
        .unwrap_err()
        .to_string()
        .contains("exceeds u64"));
        for body in [
            b"not json".as_slice(),
            br#"{"hybridSearchQueryInfo":{"take":"5"}}"#,
        ] {
            assert_eq!(
                decode_query_admission_plan(body).err().unwrap().status(),
                status_codes::SERIALIZATION_RESPONSE_BODY_INVALID,
            );
        }
    }

    #[tokio::test]
    async fn hybrid_limit_does_not_restrict_other_queries_or_replace_their_buffer_guard() {
        let (_emulator, driver) = setup(12).await;
        for maximum in ["0", "invalid"] {
            let mut request = query_request("SELECT * FROM c");
            if let FeedRequest::Query(ref mut query) = request {
                query.hybrid_search_max_items = Some(maximum.into());
            }
            assert_eq!(query_drain(&driver, &request, None).await.len(), 12);
        }
        let mut request = query_request("SELECT TOP 2 c.pk FROM c ORDER BY c.pk");
        if let FeedRequest::Query(ref mut query) = request {
            query.hybrid_search_max_items = Some("0".into());
        }
        assert_eq!(query_drain(&driver, &request, None).await.len(), 2);

        let mut request = query_request("SELECT DISTINCT TOP 2 c.pk FROM c");
        if let FeedRequest::Query(ref mut query) = request {
            query.hybrid_search_max_items = Some("invalid".into());
            query.max_buffered_query_window = Some(1);
        }
        let error = next_plan_page(
            driver,
            Arc::new(Mutex::new(CursorState::default())),
            ("test".into(), "dbs/db/colls/c".into()),
            None,
            modifiers(),
            request,
            PlanOptions::default(),
        )
        .await
        .unwrap_err();
        assert!(error
            .to_string()
            .contains("Executing a vector search query with more items"));
    }

    #[tokio::test]
    async fn complete_key_bypasses_hybrid_limit_metadata_request() {
        let (driver, rule) = setup_fault("MetadataQueryPlan", Duration::ZERO).await;
        let mut request = query_request("SELECT * FROM c");
        if let FeedRequest::Query(ref mut query) = request {
            query.partition_key = Some(PartitionKey::from("customer-501"));
            query.hybrid_search_max_items = Some("0".into());
        }
        let (result, _, _) = next_plan_page(
            driver,
            Arc::new(Mutex::new(CursorState::default())),
            ("test".into(), "dbs/db/colls/c".into()),
            None,
            modifiers(),
            request,
            PlanOptions::default(),
        )
        .await
        .unwrap();
        assert!(result.is_ok());
        assert_eq!(rule.hit_count(), 0);
    }

    #[tokio::test]
    async fn hybrid_limit_plan_failure_is_not_ignored_and_can_retry_setup() {
        let (driver, rule) = setup_fault("MetadataQueryPlan", Duration::ZERO).await;
        let cursor = ItemFeedCursor::default();
        let mut request = query_request("SELECT * FROM c");
        if let FeedRequest::Query(ref mut query) = request {
            query.hybrid_search_max_items = Some("0".into());
        }
        let (result, token, complete) = next_plan_page(
            driver.clone(),
            cursor.state.clone(),
            ("test".into(), "dbs/db/colls/c".into()),
            None,
            modifiers(),
            request.clone(),
            PlanOptions::default(),
        )
        .await
        .unwrap();
        assert!(result.is_err());
        assert!(token.is_none());
        assert!(!complete);
        assert!(rule.hit_count() > 0);
        assert!(cursor.can_retry_setup());
        rule.disable();
        assert!(query_page(&driver, &cursor.state, &request, None)
            .await
            .0
            .unwrap()
            .is_empty());
    }

    #[test]
    fn query_page_size_preserves_server_choice_and_checks_typed_limit() {
        pyo3::prepare_freethreaded_python();
        assert_eq!(query_page_size(None).unwrap(), None);
        assert_eq!(
            query_page_size(Some(-1)).unwrap(),
            Some(MaxItemCountHint::ServerDecides)
        );
        assert_eq!(
            query_page_size(Some(5)).unwrap(),
            Some(MaxItemCountHint::Limit(NonZeroU32::new(5).unwrap()))
        );
        for value in [0, -2, i64::from(u32::MAX) + 1] {
            assert!(query_page_size(Some(value)).is_err());
        }
    }

    #[test]
    fn query_inputs_preserve_body_bytes_and_read_scope_separately() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let namespace = py
                .import_bound("types")
                .unwrap()
                .getattr("SimpleNamespace")
                .unwrap();
            let prepared = namespace.call0().unwrap();
            let scope = namespace.call0().unwrap();
            let body = br#"{ "parameters": [{"name":"@p","value":[null,true,9007199254740993,1e+02,"\u0041"]}], "query": "SELECT VALUE @p" }"#;
            prepared.setattr("op", "query_items").unwrap();
            prepared
                .setattr("body_bytes", pyo3::types::PyBytes::new_bound(py, body))
                .unwrap();
            prepared.setattr("query_scope", &scope).unwrap();
            let settings = super::super::settings::test_settings(py);
            settings
                .getattr("query")
                .unwrap()
                .setattr("max_buffered_query_window", 1u64)
                .unwrap();
            settings
                .getattr("query")
                .unwrap()
                .setattr("full_text_score_scope", "Local")
                .unwrap();
            settings
                .getattr("query")
                .unwrap()
                .setattr("hybrid_search_max_items", "0")
                .unwrap();
            settings
                .getattr("query")
                .unwrap()
                .setattr("max_item_count", 5)
                .unwrap();
            prepared.setattr("settings", settings).unwrap();
            scope.setattr("feed_range", ("00", "AA")).unwrap();
            scope.setattr("allow_cross_partition", false).unwrap();
            let FeedRequest::Query(query) =
                feed_inputs(&prepared, BindingPartitionKey::CrossPartition).unwrap()
            else {
                panic!("expected retained query");
            };
            assert_eq!(query.body, body);
            assert_eq!(query.feed_range, Some(("00".into(), "AA".into())));
            assert!(!query.allow_cross_partition);
            assert!(query.partition_key.is_none());
            assert_eq!(query.max_buffered_query_window, Some(1));
            assert_eq!(query.full_text_score_scope, FullTextScoreScope::Local);
            assert_eq!(query.hybrid_search_max_items.as_deref(), Some("0"));
            assert_eq!(
                query.max_item_count,
                Some(MaxItemCountHint::Limit(NonZeroU32::new(5).unwrap()))
            );

            prepared.setattr("query_scope", py.None()).unwrap();
            let error = match feed_inputs(&prepared, BindingPartitionKey::CrossPartition) {
                Err(error) => error,
                Ok(_) => panic!("query without typed scope was accepted"),
            };
            assert!(error.is_instance_of::<PyTypeError>(py));
            assert!(error.to_string().contains("query_scope"));
        });
    }

    #[tokio::test]
    async fn retained_query_rejects_changed_body_or_scope_and_cannot_be_reused_afterward() {
        let (_emulator, driver) = setup(12).await;
        let original = query_request("SELECT * FROM c");
        for change in [
            "body",
            "feed_range",
            "allow_cross_partition",
            "partition_key",
            "full_text_score_scope",
            "max_item_count",
            "hybrid_search_max_items",
        ] {
            let state = Arc::new(Mutex::new(CursorState::default()));
            let (page, token) = query_page(&driver, &state, &original, None).await;
            assert!(page.is_some());
            let mut changed = original.clone();
            let FeedRequest::Query(ref mut query) = changed else {
                unreachable!();
            };
            match change {
                "body" => query.body = br#"{"query":"SELECT c.id FROM c"}"#.to_vec(),
                "feed_range" => query.feed_range = Some(("00".into(), "AA".into())),
                "allow_cross_partition" => query.allow_cross_partition = false,
                "partition_key" => query.partition_key = Some(PartitionKey::from("key-5")),
                "full_text_score_scope" => query.full_text_score_scope = FullTextScoreScope::Local,
                "hybrid_search_max_items" => query.hybrid_search_max_items = Some("0".into()),
                "max_item_count" => query.max_item_count = Some(MaxItemCountHint::ServerDecides),
                _ => unreachable!(),
            }
            let error = next_plan_page(
                driver.clone(),
                state.clone(),
                ("query-test".into(), "dbs/db/colls/c".into()),
                token.clone(),
                modifiers(),
                changed,
                PlanOptions::default().with_query_plan_mode(QueryPlanMode::GatewayOnly),
            )
            .await
            .err()
            .expect("changed query must be rejected");
            assert!(
                error.to_string().contains("does not match"),
                "{change}: {error}"
            );
            assert!(state.lock().await.progress.is_none());
            let error = next_plan_page(
                driver.clone(),
                state.clone(),
                ("query-test".into(), "dbs/db/colls/c".into()),
                token,
                modifiers(),
                original.clone(),
                PlanOptions::default().with_query_plan_mode(QueryPlanMode::GatewayOnly),
            )
            .await
            .err()
            .expect("failed cursor must not be reused");
            assert!(
                error.to_string().contains("Feed cursor failed"),
                "{change}: {error}"
            );
        }
    }

    async fn query_page(
        driver: &Arc<CosmosDriver>,
        state: &Arc<Mutex<CursorState>>,
        request: &FeedRequest,
        token: Option<String>,
    ) -> (Option<Vec<serde_json::Value>>, Option<String>) {
        let mut options = modifiers();
        if let FeedRequest::Query(query) = request {
            if let Some(limit) = query.continuation_limit_kb.filter(|limit| *limit > 0) {
                options.custom_headers.insert(
                    HeaderName::from_static("x-ms-documentdb-responsecontinuationtokenlimitinkb"),
                    HeaderValue::from(limit.to_string()),
                );
            }
        }
        let (response, token, _) = next_plan_page(
            driver.clone(),
            state.clone(),
            ("query-test".into(), "dbs/db/colls/c".into()),
            token,
            options,
            request.clone(),
            PlanOptions::default().with_query_plan_mode(QueryPlanMode::GatewayOnly),
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
            query.body = serde_json::to_vec(&serde_json::json!({
                "query": "SELECT * FROM c WHERE c.id = @id",
                "parameters": [{"name":"@id","value":"5"}]
            }))
            .unwrap();
        }
        let rows = query_drain(&driver, &request, None).await;
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0]["id"], "5");
    }

    #[tokio::test]
    async fn complete_key_query_preserves_service_token_and_resumes_with_size_limit() {
        let (_emulator, driver) = setup(0).await;
        let container = driver
            .resolve_container("db", "c", Default::default())
            .await
            .unwrap();
        for i in 0..7 {
            driver
                .execute_operation(
                    CosmosOperation::create_item(ItemReference::from_name(
                        &container,
                        PartitionKey::from("customer-501"),
                        i.to_string(),
                    ))
                    .with_body(
                        serde_json::to_vec(
                            &serde_json::json!({"id": i.to_string(), "pk": "customer-501"}),
                        )
                        .unwrap(),
                    ),
                    Default::default(),
                )
                .await
                .unwrap();
        }
        let request = FeedRequest::Query(QueryRequest {
            body: br#"{"query":"SELECT * FROM c ORDER BY c.id"}"#.to_vec(),
            partition_key: Some(PartitionKey::from("customer-501")),
            feed_range: None,
            allow_cross_partition: true,
            continuation_limit_kb: Some(1),
            max_buffered_query_window: None,
            full_text_score_scope: FullTextScoreScope::Global,
            max_item_count: None,
            hybrid_search_max_items: None,
        });
        let mut options = modifiers();
        options.custom_headers.insert(
            HeaderName::from_static("x-ms-documentdb-responsecontinuationtokenlimitinkb"),
            HeaderValue::from_static("1"),
        );
        let state = Arc::new(Mutex::new(CursorState::default()));
        let (response, token, _) = next_plan_page(
            driver.clone(),
            state.clone(),
            ("query-test".into(), "dbs/db/colls/c".into()),
            None,
            options,
            request.clone(),
            PlanOptions::default(),
        )
        .await
        .unwrap();
        let response = response.unwrap().unwrap();
        assert_eq!(token, response.headers().continuation);
        let token = token.unwrap();
        assert!(!token.starts_with("c1.") && !token.starts_with("c2."));
        assert!(token.len() <= 1024);
        let first = match response.body().clone() {
            azure_data_cosmos_driver::models::ResponseBody::Bytes(bytes) => {
                let envelope: serde_json::Value = serde_json::from_slice(&bytes).unwrap();
                envelope["Documents"].as_array().unwrap().clone()
            }
            body => body.into_items::<serde_json::Value>().unwrap(),
        };
        let remaining = query_drain(&driver, &request, Some(token)).await;
        let ids: Vec<_> = first
            .iter()
            .chain(&remaining)
            .map(|row| row["id"].as_str().unwrap())
            .collect();
        assert_eq!(ids, vec!["0", "1", "2", "3", "4", "5", "6"]);
    }

    #[tokio::test]
    async fn query_preserves_service_token_larger_than_requested_limit() {
        let expected_token = "opaque-service-token-".repeat(100);
        let rule = Arc::new(
            FaultInjectionRuleBuilder::new(
                "oversized-query-token",
                FaultInjectionResultBuilder::new()
                    .with_custom_response(
                        CustomResponseBuilder::new(azure_core::http::StatusCode::Ok)
                            .with_header("x-ms-continuation", expected_token.clone())
                            .with_header("content-type", "application/json")
                            .with_body(br#"{"Documents":[{"id":"order-1"}],"_count":1}"#.to_vec())
                            .build(),
                    )
                    .build(),
            )
            .with_condition(
                FaultInjectionConditionBuilder::new()
                    .with_operation_type("QueryItem".parse().unwrap())
                    .build(),
            )
            .build(),
        );
        let (_emulator, driver) = setup_with_fault_rules(
            0,
            PartitionKeyDefinition::new(vec![Cow::Borrowed("/pk")]),
            vec![rule.clone()],
        )
        .await;
        let mut request = query_request("SELECT * FROM c");
        if let FeedRequest::Query(ref mut query) = request {
            query.partition_key = Some(PartitionKey::from("customer-501"));
            query.continuation_limit_kb = Some(1);
        }
        let (rows, token) = query_page(
            &driver,
            &Arc::new(Mutex::new(CursorState::default())),
            &request,
            None,
        )
        .await;
        assert!(expected_token.len() > 1024);
        assert_eq!(token.as_deref(), Some(expected_token.as_str()));
        assert_eq!(rows.unwrap(), vec![serde_json::json!({"id":"order-1"})]);
        assert_eq!(rule.hit_count(), 1);
    }

    #[tokio::test]
    async fn query_scopes_and_disabled_cross_partition_are_not_ignored() {
        let (_emulator, driver) = setup(12).await;
        let container = driver
            .resolve_container("db", "c", Default::default())
            .await
            .unwrap();
        let mut request = QueryRequest {
            body: br#"{"query":"SELECT * FROM c"}"#.to_vec(),
            partition_key: Some(legacy_partition_key_header(r#"["key-5"]"#).unwrap()),
            feed_range: None,
            allow_cross_partition: false,
            continuation_limit_kb: None,
            max_buffered_query_window: None,
            full_text_score_scope: FullTextScoreScope::Global,
            max_item_count: Some(MaxItemCountHint::Limit(NonZeroU32::new(5).unwrap())),
            hybrid_search_max_items: None,
        };
        let rows = query_drain(&driver, &FeedRequest::Query(request.clone()), None).await;
        assert_eq!(
            request
                .operation(container.clone())
                .unwrap()
                .request_headers()
                .max_item_count,
            request.max_item_count
        );
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0]["id"], "5");
        request.partition_key = None;
        assert!(request.operation(container.clone()).is_err());
        request.allow_cross_partition = true;
        request.continuation_limit_kb = Some(1);
        let rows = query_drain(&driver, &FeedRequest::Query(request.clone()), None).await;
        assert_eq!(rows.len(), 12);
        request.feed_range = Some(("".into(), "FF".into()));
        let ranged_rows = query_drain(&driver, &FeedRequest::Query(request.clone()), None).await;
        assert_eq!(ranged_rows, rows);
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
    async fn bounded_unordered_distinct_enumerates_without_a_resumable_token() {
        let (_emulator, driver) = setup(12).await;
        for limit in [12, 1000] {
            let request = query_request(&format!("SELECT DISTINCT TOP {limit} VALUE c.id FROM c"));
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
    }

    #[tokio::test]
    async fn unbounded_unordered_distinct_preserves_driver_planning_error() {
        let (_emulator, driver) = setup(12).await;
        for query in [
            "SELECT DISTINCT VALUE c.id FROM c",
            "SELECT DISTINCT TOP 1001 VALUE c.id FROM c",
            "SELECT DISTINCT VALUE c.id FROM c OFFSET 1000 LIMIT 1",
        ] {
            let cursor = ItemFeedCursor::default();
            let (result, token, _) = next_plan_page(
                driver.clone(),
                cursor.state.clone(),
                ("test".into(), "dbs/db/colls/c".into()),
                None,
                modifiers(),
                query_request(query),
                PlanOptions::default().with_query_plan_mode(QueryPlanMode::GatewayOnly),
            )
            .await
            .unwrap();
            assert_eq!(
                result.unwrap_err().status(),
                status_codes::CLIENT_BUFFERED_QUERY_REQUIRES_FINITE_WINDOW,
            );
            assert!(token.is_none());
            assert!(cursor.can_retry_setup());
        }
    }

    #[tokio::test]
    async fn hierarchical_prefix_query_only_returns_matching_logical_partitions() {
        let definition = serde_json::from_value(serde_json::json!({
            "paths": ["/tenant", "/pk"], "kind": "MultiHash", "version": 2
        }))
        .unwrap();
        let (_emulator, driver) = setup_with_definition(18, definition).await;
        let mut request = QueryRequest {
            body: br#"{"query":"SELECT * FROM c"}"#.to_vec(),
            partition_key: Some(legacy_partition_key_header(r#"["tenant-1"]"#).unwrap()),
            feed_range: None,
            allow_cross_partition: true,
            continuation_limit_kb: None,
            max_buffered_query_window: None,
            full_text_score_scope: FullTextScoreScope::Global,
            max_item_count: None,
            hybrid_search_max_items: None,
        };
        let rows = query_drain(&driver, &FeedRequest::Query(request.clone()), None).await;
        assert_eq!(rows.len(), 9);
        assert!(rows.iter().all(|row| row["tenant"] == "tenant-1"));
        request.continuation_limit_kb = Some(1);
        let limited_rows = query_drain(&driver, &FeedRequest::Query(request.clone()), None).await;
        assert_eq!(limited_rows, rows);
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
                PlanOptions::default().with_query_plan_mode(QueryPlanMode::GatewayOnly),
            )
            .await;
            assert!(
                matches!(error, Err(ref error) if error.to_string().contains("binding does not support multi-partition"))
            );
            assert!(state.lock().await.progress.is_none());
        }
    }

    #[tokio::test]
    async fn change_feed_fetches_keep_scope_diagnostics_incomplete() {
        let (_emulator, driver) = setup(7).await;
        for mode in ["LatestVersion", "AllVersionsAndDeletes"] {
            let mut request = change_request(mode, "Now");
            request.partition_key = Some(legacy_partition_key_header(r#"["key-5"]"#).unwrap());
            let state = Arc::new(Mutex::new(CursorState::default()));
            let mut token = None;
            for _ in 0..2 {
                let result = next_plan_page(
                    driver.clone(),
                    state.clone(),
                    ("test".into(), "dbs/db/colls/c".into()),
                    token,
                    modifiers(),
                    FeedRequest::ChangeFeed(request.clone()),
                    PlanOptions::default().with_query_plan_mode(QueryPlanMode::GatewayOnly),
                )
                .await
                .unwrap();
                assert!(!result.2);
                assert!(result.0.as_ref().unwrap().is_some());
                token = result.1.clone();
                assert!(token.is_some());
                assert!(state.lock().await.progress.is_some());
                Python::with_gil(|py| {
                    let ordinary = finish_page(py, result.clone(), false).unwrap();
                    let envelope = finish_page(py, result, true).unwrap();
                    assert!(envelope.get_item(0).unwrap().eq(&ordinary).unwrap());
                    assert!(!envelope
                        .get_item(1)
                        .unwrap()
                        .get_item("complete")
                        .unwrap()
                        .extract::<bool>()
                        .unwrap());
                });
            }
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
            assert!(token.as_ref().unwrap().starts_with("c2."));
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
            let (result, _, _) = next_page(
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

// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use std::sync::atomic::Ordering;
use std::sync::Arc;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_core::http::headers::{HeaderName, HeaderValue};
use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{ActivityId, CosmosOperation, CosmosResponse, SessionToken},
    options::ContentResponseOnWrite,
};

use super::diagnostics::BINDING_OP_COUNT;
use super::request::{build_operation_options, RequestHeadersAndOptions};
use super::response::{tuple_from_offer_feed_result, tuple_from_result};
use super::{lookup_driver, AbortOnDrop};
use crate::runtime::require_runtime_context;

/// Entry point the binding calls to run one container's offer/throughput read and
/// wait for it (sync). Offers are an account-level, non-partitioned resource, so --
/// unlike `run_query_operation` -- there is no container to resolve and no partition
/// to target: it builds `CosmosOperation::query_offers` against the account carrying
/// the same offer query JSON the legacy path sends, and returns the page in the
/// `{"Offers":[...]}` envelope the Python offer parser reads.
pub(crate) fn run_read_offer_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let response_result: Result<Option<CosmosResponse>, CosmosError> = py.allow_threads(|| {
        runtime_ctx
            .tokio_rt
            .block_on(run_read_offer_future(driver, modifiers, body_bytes))
    });

    tuple_from_offer_feed_result(py, response_result)
}

/// Async sibling of `run_read_offer_operation`.
pub(crate) fn run_read_offer_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let join = runtime_ctx
        .tokio_rt
        .spawn(run_read_offer_future(driver, modifiers, body_bytes));
    let abort_guard = AbortOnDrop(join.abort_handle());

    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let response_result = join.await.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err("cosmos async operation was cancelled before it completed")
            } else {
                PyRuntimeError::new_err(format!("cosmos async operation task failed: {join_error}"))
            }
        })?;
        Python::with_gil(|py| {
            tuple_from_offer_feed_result(py, response_result).map(|tuple| tuple.into_any().unbind())
        })
    })
}

/// Entry point the binding calls to run one container's offer/throughput replace and
/// wait for it (sync). Offers are account-level and non-partitioned, so -- like
/// `run_read_offer_operation` -- there is no container to resolve: it builds
/// `CosmosOperation::replace_offer` for the given offer RID carrying the mutated
/// offer document, and returns the single updated offer via `tuple_from_result` (the
/// single-document shape, not the offer-feed envelope the read uses).
pub(crate) fn run_replace_offer_operation<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    offer_id: String,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let response_result: Result<CosmosResponse, CosmosError> = py.allow_threads(|| {
        runtime_ctx.tokio_rt.block_on(run_replace_offer_future(
            driver, modifiers, offer_id, body_bytes,
        ))
    });

    tuple_from_result(py, response_result)
}

/// Async sibling of `run_replace_offer_operation`.
pub(crate) fn run_replace_offer_operation_async<'py>(
    py: Python<'py>,
    driver_handle: &str,
    modifiers: RequestHeadersAndOptions,
    offer_id: String,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(driver_handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let join = runtime_ctx.tokio_rt.spawn(run_replace_offer_future(
        driver, modifiers, offer_id, body_bytes,
    ));
    let abort_guard = AbortOnDrop(join.abort_handle());

    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        let _abort_guard = abort_guard;
        let response_result = join.await.map_err(|join_error| {
            if join_error.is_cancelled() {
                PyRuntimeError::new_err("cosmos async operation was cancelled before it completed")
            } else {
                PyRuntimeError::new_err(format!("cosmos async operation task failed: {join_error}"))
            }
        })?;
        Python::with_gil(|py| {
            tuple_from_result(py, response_result).map(|tuple| tuple.into_any().unbind())
        })
    })
}
/// Driver work for an offer/throughput read. Offers live at the account level and
/// are not partitioned, so this resolves no container and targets no partition: it
/// builds `query_offers` against the account and attaches the prepared query JSON.
/// Add default query `Content-Type` and `x-ms-documentdb-isquery` markers only if
/// absent from custom headers. The prepared container-recreate guard header is
/// also supplied through those custom headers; this helper does not enforce it.
async fn run_read_offer_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    body_bytes: Vec<u8>,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let account = driver.account().clone();
    let mut op = CosmosOperation::query_offers(account).with_body(body_bytes);

    if let Some(activity) = modifiers.activity_header.as_ref() {
        op = op.with_activity_id(ActivityId::from(activity.clone()));
    }
    if let Some(session) = modifiers.session_header.as_ref() {
        op = op.with_session_token(SessionToken::from(session.clone()));
    }

    let mut custom_headers = modifiers.custom_headers;
    custom_headers
        .entry(HeaderName::from_static("content-type"))
        .or_insert_with(|| HeaderValue::from("application/query+json".to_string()));
    custom_headers
        .entry(HeaderName::from_static("x-ms-documentdb-isquery"))
        .or_insert_with(|| HeaderValue::from("true".to_string()));

    let options = build_operation_options(
        None,
        modifiers.excluded_regions_value,
        modifiers.driver_timeout_policy,
        modifiers.availability_strategy,
        custom_headers,
    );
    driver.execute_operation(op, options).await
}

/// Driver work for an offer/throughput replace. Like `run_read_offer_future`, offers
/// are an account-level, non-partitioned resource, so this resolves no container and
/// targets no partition: it builds `CosmosOperation::replace_offer(account, offer_id)`
/// using the offer's RID and the prepared replacement document. Signing and
/// transport header defaults are left to the driver. Custom headers include any
/// prepared container-recreate guard. `execute_singleton_operation` returns one
/// response, converted with `tuple_from_result` rather than the offer-feed envelope.
async fn run_replace_offer_future(
    driver: Arc<CosmosDriver>,
    modifiers: RequestHeadersAndOptions,
    offer_id: String,
    body_bytes: Vec<u8>,
) -> Result<CosmosResponse, CosmosError> {
    let account = driver.account().clone();
    let mut op = CosmosOperation::replace_offer(account, offer_id).with_body(body_bytes);

    if let Some(activity) = modifiers.activity_header.as_ref() {
        op = op.with_activity_id(ActivityId::from(activity.clone()));
    }
    if let Some(session) = modifiers.session_header.as_ref() {
        op = op.with_session_token(SessionToken::from(session.clone()));
    }

    // Request response content because replace_throughput reads the returned
    // offer. Override the extracted no-response setting here; this option alone
    // does not guarantee that a service response contains a body.
    let content_response = Some(ContentResponseOnWrite::Enabled);
    let options = build_operation_options(
        content_response,
        modifiers.excluded_regions_value,
        modifiers.driver_timeout_policy,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    driver.execute_singleton_operation(op, options).await
}

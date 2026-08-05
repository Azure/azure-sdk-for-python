// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use std::future::Future;
use std::sync::atomic::Ordering;
use std::sync::Arc;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{ActivityId, CosmosOperation, CosmosResponse, DatabaseReference, SessionToken},
    options::ContentResponseOnWrite,
};

use super::diagnostics::BINDING_OP_COUNT;
use super::request::{build_operation_options, OpModifiers};
use super::response::{tuple_from_database_feed_result, tuple_from_result};
use super::{lookup_driver, AbortOnDrop};
use crate::runtime::require_runtime_context;

type ResponseTupleConverter<R> = for<'py> fn(Python<'py>, R) -> PyResult<Bound<'py, PyTuple>>;

fn run_database_sync<'py, R, F, Fut>(
    py: Python<'py>,
    handle: &str,
    operation_name: &str,
    operation_future_factory: F,
    convert_response: ResponseTupleConverter<R>,
) -> PyResult<Bound<'py, PyTuple>>
where
    F: FnOnce(Arc<CosmosDriver>) -> Fut + Send,
    Fut: Future<Output = R>,
    R: Send,
{
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let runtime_ctx = require_runtime_context(operation_name)?;
    let response_result = py.allow_threads(|| {
        runtime_ctx
            .tokio_rt
            .block_on(operation_future_factory(driver))
    });
    convert_response(py, response_result)
}

fn run_database_async<'py, R, F, Fut>(
    py: Python<'py>,
    handle: &str,
    operation_name: &str,
    operation_future_factory: F,
    convert_response: ResponseTupleConverter<R>,
) -> PyResult<Bound<'py, PyAny>>
where
    F: FnOnce(Arc<CosmosDriver>) -> Fut + Send + 'static,
    Fut: Future<Output = R> + Send + 'static,
    R: Send + 'static,
{
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let runtime_ctx = require_runtime_context(operation_name)?;
    let join = runtime_ctx.tokio_rt.spawn(operation_future_factory(driver));
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
            convert_response(py, response_result).map(|tuple| tuple.into_any().unbind())
        })
    })
}

pub(crate) fn run_create_database_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_database_sync(
        py,
        handle,
        operation_name,
        move |driver| run_create_database_future(driver, modifiers, body_bytes),
        tuple_from_result,
    )
}

pub(crate) fn run_create_database_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    body_bytes: Vec<u8>,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_database_async(
        py,
        handle,
        operation_name,
        move |driver| run_create_database_future(driver, modifiers, body_bytes),
        tuple_from_result,
    )
}

pub(crate) fn run_read_database_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_database_sync(
        py,
        handle,
        operation_name,
        move |driver| run_read_database_future(driver, modifiers, database_id),
        tuple_from_result,
    )
}

pub(crate) fn run_read_database_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_database_async(
        py,
        handle,
        operation_name,
        move |driver| run_read_database_future(driver, modifiers, database_id),
        tuple_from_result,
    )
}

/// Run one `list_databases` page and return the reply as a Python tuple.
///
/// Finds the caller's driver, runs the request to completion on this thread, and
/// converts whatever comes back -- a page, a service error, or a transport
/// failure -- into the tuple shape Python expects. Without it the entry point
/// above would have to do driver lookup, blocking, and error conversion itself,
/// and so would every other operation in this file.
pub(crate) fn run_list_databases_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    operation_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_database_sync(
        py,
        handle,
        operation_name,
        move |driver| run_list_databases_future(driver, modifiers),
        tuple_from_database_feed_result,
    )
}

/// Async counterpart of [`run_list_databases_operation`]: returns an awaitable
/// instead of blocking, so an async caller's event loop keeps running while the
/// page is in flight.
pub(crate) fn run_list_databases_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    operation_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_database_async(
        py,
        handle,
        operation_name,
        move |driver| run_list_databases_future(driver, modifiers),
        tuple_from_database_feed_result,
    )
}

async fn run_create_database_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    body_bytes: Vec<u8>,
) -> Result<CosmosResponse, CosmosError> {
    let account = driver.account().clone();
    let mut op = CosmosOperation::create_database(account).with_body(body_bytes);

    if let Some(activity) = modifiers.activity_header {
        op = op.with_activity_id(ActivityId::from(activity));
    }
    if let Some(session) = modifiers.session_header {
        op = op.with_session_token(SessionToken::from(session));
    }

    let options = build_operation_options(
        Some(ContentResponseOnWrite::Enabled),
        modifiers.excluded_regions_value,
        modifiers.end_to_end_timeout,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    driver.execute_singleton_operation(op, options).await
}

async fn run_read_database_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    database_id: String,
) -> Result<CosmosResponse, CosmosError> {
    let database = DatabaseReference::from_name(driver.account().clone(), database_id);
    let mut op = CosmosOperation::read_database(database);

    if let Some(activity) = modifiers.activity_header {
        op = op.with_activity_id(ActivityId::from(activity));
    }
    if let Some(session) = modifiers.session_header {
        op = op.with_session_token(SessionToken::from(session));
    }

    let options = build_operation_options(
        None,
        modifiers.excluded_regions_value,
        modifiers.end_to_end_timeout,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    driver.execute_singleton_operation(op, options).await
}

/// Ask the driver for one page of databases.
///
/// Note the return type. `create_database` and `read_database` above call
/// `execute_singleton_operation`, which always yields exactly one response. A
/// feed can run out of pages, so this calls `execute_operation` and gets back an
/// `Option`, where `None` means "no page left". It is the only operation in this
/// file on the feed-shaped driver call.
async fn run_list_databases_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
) -> Result<Option<CosmosResponse>, CosmosError> {
    let mut op = CosmosOperation::read_all_databases(driver.account().clone());
    if let Some(activity) = modifiers.activity_header {
        op = op.with_activity_id(ActivityId::from(activity));
    }
    if let Some(session) = modifiers.session_header {
        op = op.with_session_token(SessionToken::from(session));
    }
    let options = build_operation_options(
        None,
        modifiers.excluded_regions_value,
        modifiers.end_to_end_timeout,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    driver.execute_operation(op, options).await
}

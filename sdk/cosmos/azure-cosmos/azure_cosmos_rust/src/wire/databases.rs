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
use super::response::tuple_from_result;
use super::{lookup_driver, AbortOnDrop};
use crate::runtime::require_runtime_context;

fn run_database_sync<'py, F, Fut>(
    py: Python<'py>,
    handle: &str,
    op_name: &str,
    make_future: F,
) -> PyResult<Bound<'py, PyTuple>>
where
    F: FnOnce(Arc<CosmosDriver>) -> Fut + Send,
    Fut: Future<Output = Result<CosmosResponse, CosmosError>>,
{
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;
    let response_result: Result<CosmosResponse, CosmosError> =
        py.allow_threads(|| runtime_ctx.tokio_rt.block_on(make_future(driver)));
    tuple_from_result(py, response_result)
}

fn run_database_async<'py, F, Fut>(
    py: Python<'py>,
    handle: &str,
    op_name: &str,
    make_future: F,
) -> PyResult<Bound<'py, PyAny>>
where
    F: FnOnce(Arc<CosmosDriver>) -> Fut + Send + 'static,
    Fut: Future<Output = Result<CosmosResponse, CosmosError>> + Send + 'static,
{
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;
    let join = runtime_ctx.tokio_rt.spawn(make_future(driver));
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

pub(crate) fn run_create_database_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_database_sync(py, handle, op_name, move |driver| {
        run_create_database_future(driver, modifiers, body_bytes)
    })
}

pub(crate) fn run_create_database_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_database_async(py, handle, op_name, move |driver| {
        run_create_database_future(driver, modifiers, body_bytes)
    })
}

pub(crate) fn run_read_database_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_database_sync(py, handle, op_name, move |driver| {
        run_read_database_future(driver, modifiers, database_id)
    })
}

pub(crate) fn run_read_database_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_database_async(py, handle, op_name, move |driver| {
        run_read_database_future(driver, modifiers, database_id)
    })
}

async fn run_create_database_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    body_bytes: Vec<u8>,
) -> Result<CosmosResponse, CosmosError> {
    let account = driver.account().clone();
    let mut op = CosmosOperation::create_database(account).with_body(body_bytes);

    if let Some(activity) = modifiers.activity_header.as_ref() {
        op = op.with_activity_id(ActivityId::from(activity.clone()));
    }
    if let Some(session) = modifiers.session_header.as_ref() {
        op = op.with_session_token(SessionToken::from(session.clone()));
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

    if let Some(activity) = modifiers.activity_header.as_ref() {
        op = op.with_activity_id(ActivityId::from(activity.clone()));
    }
    if let Some(session) = modifiers.session_header.as_ref() {
        op = op.with_session_token(SessionToken::from(session.clone()));
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

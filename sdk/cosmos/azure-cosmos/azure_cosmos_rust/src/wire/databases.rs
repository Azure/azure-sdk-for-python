// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use super::*;

/// Sync runner for the account-level `create_database` operation (the sync entry
/// in `documents/databases.rs`). Bumps the binding-invocation counter, looks up
/// the rust driver by handle, then -- with the GIL released -- blocks the calling
/// thread on the shared Tokio runtime until the driver signs, sends, and resolves
/// the create, and turns the driver's response into the `BackendResponse` tuple
/// the Python parser reads. Unlike an item write there is no container to resolve
/// and no partition to target: a database is an account-level resource.
pub(crate) fn run_create_database_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let response_result: Result<CosmosResponse, CosmosError> = py.allow_threads(|| {
        runtime_ctx
            .tokio_rt
            .block_on(run_create_database_future(driver, modifiers, body_bytes))
    });

    tuple_from_result(py, response_result)
}

/// Async twin of `run_create_database_operation`: spawns the create on the shared
/// Tokio runtime and returns an awaitable. An abort guard cancels the spawned task
/// if the Python awaitable is dropped first (for example, a cancelled `await`), so
/// no work is left running detached.
pub(crate) fn run_create_database_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    BINDING_OP_COUNT.fetch_add(1, Ordering::Relaxed);
    let driver = lookup_driver(handle)?;
    let runtime_ctx = require_runtime_context(op_name)?;

    let join = runtime_ctx
        .tokio_rt
        .spawn(run_create_database_future(driver, modifiers, body_bytes));
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

    // Python constructs DatabaseProxy from the returned document, so this must
    // override the driver's write default of return=minimal.
    let options = build_operation_options(
        Some(ContentResponseOnWrite::Enabled),
        modifiers.excluded_regions_value,
        modifiers.end_to_end_timeout,
        modifiers.availability_strategy,
        modifiers.custom_headers,
    );
    driver.execute_singleton_operation(op, options).await
}

// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use std::future::Future;
use std::sync::atomic::Ordering;
use std::sync::Arc;
use std::time::Instant;

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use azure_core::http::StatusCode;
use azure_data_cosmos_driver::{
    driver::CosmosDriver,
    error::CosmosError,
    models::{ActivityId, CosmosOperation, CosmosResponse, DatabaseReference, SessionToken},
    options::{ContentResponseOnWrite, EndToEndOperationLatencyPolicy},
};

use super::diagnostics::BINDING_OP_COUNT;
use super::request::{build_operation_options, OpModifiers};
use super::response::tuple_from_result;
use super::{lookup_driver, AbortOnDrop};
use crate::runtime::require_runtime_context;

/// Shared scaffolding for a sync database operation:
/// bump the binding counter, look up the driver, block on the future.
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

/// Shared scaffolding for an async database operation:
/// bump the binding counter, spawn the future, wrap in an abort guard.
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
    run_database_sync(py, handle, op_name, move |driver| {
        run_create_database_future(driver, modifiers, body_bytes)
    })
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
    run_database_async(py, handle, op_name, move |driver| {
        run_create_database_future(driver, modifiers, body_bytes)
    })
}

/// Run the database existence read and conditional create as one sync binding operation.
pub(crate) fn run_create_database_if_not_exists_operation<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyTuple>> {
    run_database_sync(py, handle, op_name, move |driver| {
        run_create_database_if_not_exists_future(driver, modifiers, database_id, body_bytes)
    })
}

/// Async twin of [`run_create_database_if_not_exists_operation`].
pub(crate) fn run_create_database_if_not_exists_operation_async<'py>(
    py: Python<'py>,
    handle: &str,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
    op_name: &str,
) -> PyResult<Bound<'py, PyAny>> {
    run_database_async(py, handle, op_name, move |driver| {
        run_create_database_if_not_exists_future(driver, modifiers, database_id, body_bytes)
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

/// Run the retry-safe "create database if not exists" as one driver operation.
///
/// Reads the named database first; only if that read comes back "not found"
/// (404) does it send the create. An existing database is returned as-is with
/// no create sent, so re-running setup for a name that already exists is safe
/// instead of failing with a 409 "already exists". A create that loses a
/// concurrent race still surfaces its 409 -- the binding never hides it behind
/// a second read. Both legs share one absolute deadline (computed once, below)
/// so the read-plus-create pair can't outlive the customer's timeout, and the
/// throughput provisioning headers ride only the create leg. Being native here
/// is what lets this operation run on the rust driver at all; without it every
/// such call would fall back to the legacy Python read/404/create path.
async fn run_create_database_if_not_exists_future(
    driver: Arc<CosmosDriver>,
    modifiers: OpModifiers,
    database_id: String,
    body_bytes: Vec<u8>,
) -> Result<CosmosResponse, CosmosError> {
    let OpModifiers {
        activity_header,
        session_header,
        content_response_on_write: _,
        excluded_regions_value,
        end_to_end_timeout,
        availability_strategy,
        custom_headers,
    } = modifiers;

    // Provisioning headers belong only on the create request, never the read.
    let mut read_headers = custom_headers.clone();
    read_headers.retain(|name, _| {
        !matches!(
            name.as_str(),
            "x-ms-offer-throughput" | "x-ms-cosmos-offer-autopilot-settings"
        )
    });

    // Establish one absolute deadline before the read.  Both legs enforce this
    // exact deadline so no wall-clock time is extended between computing the
    // remaining duration and entering the driver pipeline.
    let deadline = end_to_end_timeout
        .as_ref()
        .map(|p| Instant::now() + p.timeout());

    // Read leg: full configured timeout drives the hedging threshold; the
    // shared deadline is carried so the pipeline enforces it directly.
    let read_timeout = build_policy_with_deadline(&end_to_end_timeout, &deadline);
    let read_options = build_operation_options(
        None,
        excluded_regions_value.clone(),
        read_timeout,
        availability_strategy.clone(),
        read_headers,
    );

    let database_reference = DatabaseReference::from_name(driver.account().clone(), database_id);
    let mut read_op = CosmosOperation::read_database(database_reference);
    if let Some(activity) = activity_header.as_ref() {
        read_op = read_op.with_activity_id(ActivityId::from(activity.clone()));
    }
    if let Some(session) = session_header.as_ref() {
        read_op = read_op.with_session_token(SessionToken::from(session.clone()));
    }

    let create_driver = Arc::clone(&driver);
    read_then_create(
        driver.execute_singleton_operation(read_op, read_options),
        move || async move {
            // Create leg: remaining budget at this point drives the hedging
            // threshold; the same shared deadline is enforced by the pipeline.
            let create_timeout = remaining_policy_with_deadline(&end_to_end_timeout, &deadline);
            let create_options = build_operation_options(
                Some(ContentResponseOnWrite::Enabled),
                excluded_regions_value,
                create_timeout,
                availability_strategy,
                custom_headers,
            );
            let mut create_op = CosmosOperation::create_database(create_driver.account().clone())
                .with_body(body_bytes);
            if let Some(activity) = activity_header {
                create_op = create_op.with_activity_id(ActivityId::from(activity));
            }
            if let Some(session) = session_header {
                create_op = create_op.with_session_token(SessionToken::from(session));
            }
            create_driver
                .execute_singleton_operation(create_op, create_options)
                .await
        },
        |error| error.status().status_code() == StatusCode::NotFound,
        |create_result, read_error| {
            let prior_diagnostics: Vec<_> = read_error.diagnostics().into_iter().collect();
            match create_result {
                Ok(response) => {
                    Ok(response.__with_aggregated_prior_diagnostics(&prior_diagnostics))
                }
                Err(error) => Err(error.__with_aggregated_prior_diagnostics(&prior_diagnostics)),
            }
        },
    )
    .await
}

/// Build the read-leg policy for a composite operation.
///
/// The read leg keeps the full configured timeout as `policy.timeout()` so the
/// hedging threshold is stable across retries.  When an absolute deadline is
/// present it is carried into the policy so the pipeline enforces the shared
/// deadline rather than computing a fresh one from `Instant::now()`.
fn build_policy_with_deadline(
    original: &Option<EndToEndOperationLatencyPolicy>,
    deadline: &Option<Instant>,
) -> Option<EndToEndOperationLatencyPolicy> {
    match (original.as_ref(), *deadline) {
        (Some(p), Some(dl)) => Some(EndToEndOperationLatencyPolicy::__new_with_deadline(
            p.timeout(),
            dl,
        )),
        _ => original.clone(),
    }
}

/// Build the create-leg policy for a composite operation.
///
/// `policy.timeout()` is set to the wall-clock time remaining before `deadline`
/// at the moment the create begins, so the hedging threshold reflects actual
/// remaining budget.  The same `deadline` is carried so the pipeline enforces
/// the exact shared deadline — no additional time is granted between computing
/// the remaining duration and entering the pipeline.
///
/// Returns `None` when no budget was set, preserving the driver default (no
/// timeout).
fn remaining_policy_with_deadline(
    original: &Option<EndToEndOperationLatencyPolicy>,
    deadline: &Option<Instant>,
) -> Option<EndToEndOperationLatencyPolicy> {
    match (original.as_ref(), *deadline) {
        (Some(_), Some(dl)) => {
            let remaining = dl.saturating_duration_since(Instant::now());
            Some(EndToEndOperationLatencyPolicy::__new_with_deadline(
                remaining, dl,
            ))
        }
        _ => None,
    }
}

/// Generic read-then-create rule, kept in one tested place.
///
/// Runs `read_future`; if it fails the `is_not_found` check, runs `create` and
/// `merge`s its outcome with the read error so the read's diagnostics are kept.
/// Any other read error is returned unchanged, and a create error (such as a
/// concurrent-create 409) is propagated, never swallowed. Sharing this keeps
/// the "existing wins, 404 creates, everything else propagates" behavior
/// identical for every operation that needs it.
async fn read_then_create<T, E, ReadFuture, Create, CreateFuture, IsNotFound, Merge>(
    read_future: ReadFuture,
    create: Create,
    is_not_found: IsNotFound,
    merge: Merge,
) -> Result<T, E>
where
    ReadFuture: Future<Output = Result<T, E>>,
    Create: FnOnce() -> CreateFuture,
    CreateFuture: Future<Output = Result<T, E>>,
    IsNotFound: FnOnce(&E) -> bool,
    Merge: FnOnce(Result<T, E>, &E) -> Result<T, E>,
{
    match read_future.await {
        Ok(response) => Ok(response),
        Err(read_error) if is_not_found(&read_error) => merge(create().await, &read_error),
        Err(error) => Err(error),
    }
}

#[cfg(test)]
mod tests {
    //! Locks in the read-then-create rule and the shared-deadline math behind
    //! "create database if not exists": existing database wins with no create,
    //! a 404 read triggers the create, any other read error stops, and a
    //! concurrent-create 409 is propagated (never swallowed).
    use super::{build_policy_with_deadline, read_then_create, remaining_policy_with_deadline};
    use azure_data_cosmos_driver::options::EndToEndOperationLatencyPolicy;
    use std::sync::{
        atomic::{AtomicUsize, Ordering},
        Arc,
    };
    use std::time::{Duration, Instant};

    #[derive(Debug, PartialEq)]
    enum TestError {
        NotFound,
        Forbidden,
        Conflict,
    }

    async fn execute(
        read_result: Result<&'static str, TestError>,
        create_result: Result<&'static str, TestError>,
        create_count: Arc<AtomicUsize>,
    ) -> Result<&'static str, TestError> {
        read_then_create(
            async move { read_result },
            move || async move {
                create_count.fetch_add(1, Ordering::Relaxed);
                create_result
            },
            |error| *error == TestError::NotFound,
            |result, _read_error| result,
        )
        .await
    }

    #[tokio::test]
    async fn existing_database_skips_create() {
        // Database already there: the read succeeds, so no create is sent.
        let create_count = Arc::new(AtomicUsize::new(0));
        let result = execute(Ok("existing"), Ok("created"), Arc::clone(&create_count)).await;

        assert_eq!(result, Ok("existing"));
        assert_eq!(create_count.load(Ordering::Relaxed), 0);
    }

    #[tokio::test]
    async fn not_found_read_creates_database() {
        // Database missing (404): the create runs exactly once.
        let create_count = Arc::new(AtomicUsize::new(0));
        let result = execute(
            Err(TestError::NotFound),
            Ok("created"),
            Arc::clone(&create_count),
        )
        .await;

        assert_eq!(result, Ok("created"));
        assert_eq!(create_count.load(Ordering::Relaxed), 1);
    }

    #[tokio::test]
    async fn non_not_found_read_error_skips_create() {
        // A read error that isn't 404 (here Forbidden) stops the operation and
        // no create is attempted.
        let create_count = Arc::new(AtomicUsize::new(0));
        let result = execute(
            Err(TestError::Forbidden),
            Ok("created"),
            Arc::clone(&create_count),
        )
        .await;

        assert_eq!(result, Err(TestError::Forbidden));
        assert_eq!(create_count.load(Ordering::Relaxed), 0);
    }

    #[tokio::test]
    async fn create_conflict_is_propagated() {
        // Concurrent-create race: read is 404, but another caller wins so the
        // create returns 409 -- that 409 is surfaced, not hidden.
        let create_count = Arc::new(AtomicUsize::new(0));
        let result = execute(
            Err(TestError::NotFound),
            Err(TestError::Conflict),
            Arc::clone(&create_count),
        )
        .await;

        assert_eq!(result, Err(TestError::Conflict));
        assert_eq!(create_count.load(Ordering::Relaxed), 1);
    }

    // ── build_policy_with_deadline tests ─────────────────────────────────────

    #[test]
    fn build_policy_with_deadline_returns_none_when_no_timeout_set() {
        let dl = Some(Instant::now() + Duration::from_secs(10));
        assert!(build_policy_with_deadline(&None, &dl).is_none());
    }

    #[test]
    fn build_policy_with_deadline_returns_none_when_no_timeout_or_deadline() {
        assert!(build_policy_with_deadline(&None, &None).is_none());
    }

    #[test]
    fn build_policy_with_deadline_preserves_timeout_and_binds_deadline() {
        let dl = Instant::now() + Duration::from_secs(10);
        let original = Some(EndToEndOperationLatencyPolicy::new(Duration::from_secs(5)));
        let result = build_policy_with_deadline(&original, &Some(dl));
        let policy = result.expect("should produce a policy when timeout and deadline are set");
        assert_eq!(policy.timeout(), Duration::from_secs(5));
        // Verify the exact deadline is embedded by comparing with an equivalent construction.
        let expected =
            EndToEndOperationLatencyPolicy::__new_with_deadline(Duration::from_secs(5), dl);
        assert_eq!(policy, expected);
    }

    #[test]
    fn build_policy_with_deadline_passes_through_when_no_deadline() {
        let original = Some(EndToEndOperationLatencyPolicy::new(Duration::from_secs(5)));
        let result = build_policy_with_deadline(&original, &None);
        let policy = result.expect("should produce a policy when timeout is set");
        assert_eq!(policy.timeout(), Duration::from_secs(5));
        // No deadline means the policy is identical to the original (no deadline bound).
        let expected = EndToEndOperationLatencyPolicy::new(Duration::from_secs(5));
        assert_eq!(policy, expected);
    }

    // ── remaining_policy_with_deadline tests ──────────────────────────────────

    #[test]
    fn remaining_policy_with_deadline_returns_none_when_no_timeout_set() {
        let dl = Some(Instant::now() + Duration::from_secs(10));
        assert!(remaining_policy_with_deadline(&None, &dl).is_none());
    }

    #[test]
    fn remaining_policy_with_deadline_returns_none_when_no_deadline() {
        let original = Some(EndToEndOperationLatencyPolicy::new(Duration::from_secs(30)));
        assert!(remaining_policy_with_deadline(&original, &None).is_none());
    }

    #[test]
    fn remaining_policy_with_deadline_saturates_to_zero_for_past_deadline() {
        // `dl` is set to the current instant; any subsequent `Instant::now()` call
        // inside `remaining_policy_with_deadline` will be >= `dl`, so
        // `saturating_duration_since` returns `Duration::ZERO`.
        let dl = Instant::now();
        let original = Some(EndToEndOperationLatencyPolicy::new(Duration::from_secs(30)));
        let result = remaining_policy_with_deadline(&original, &Some(dl));
        let policy = result.expect("should produce a policy when timeout and deadline are set");
        assert_eq!(policy.timeout(), Duration::ZERO);
        // The exact deadline is preserved even when remaining is zero.
        let expected = EndToEndOperationLatencyPolicy::__new_with_deadline(Duration::ZERO, dl);
        assert_eq!(policy, expected);
    }

    #[test]
    fn remaining_policy_with_deadline_returns_remaining_for_future_deadline() {
        let dl = Instant::now() + Duration::from_secs(100);
        let original = Some(EndToEndOperationLatencyPolicy::new(Duration::from_secs(30)));
        let result = remaining_policy_with_deadline(&original, &Some(dl));
        let policy = result.expect("should produce a policy when timeout and deadline are set");
        // With 100 seconds remaining, the timeout must be close to 100s (any code
        // running in-process is far faster than 1 second).
        assert!(policy.timeout() <= Duration::from_secs(100));
        assert!(policy.timeout() > Duration::from_millis(99_900));
        // Verify the exact deadline is embedded.
        let expected = EndToEndOperationLatencyPolicy::__new_with_deadline(policy.timeout(), dl);
        assert_eq!(policy, expected);
    }
}

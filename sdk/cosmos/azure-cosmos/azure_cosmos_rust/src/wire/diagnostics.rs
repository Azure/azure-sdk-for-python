// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

use azure_data_cosmos_driver::diagnostics::DiagnosticsContext;
use pyo3::prelude::*;

// ---------------------------------------------------------------------------
// Binding-invocation counter (a check for the perf drill, not part of serving
// requests)
// ---------------------------------------------------------------------------
//
// A plain running count, in this process, of how many times the rust binding
// actually ran an item operation. It exists only so the perf drill can catch its
// single biggest risk: trusting the COSMOS_BACKEND label. A results row tagged
// "rust" that actually ran the core-python path would mislabel every number on
// it. This counter answers "did the rust binding really run this?" from INSIDE
// the binding: every item operation, sync or async, bumps it on entry to the
// driver runner below. The perf harness reads it through `_rust.operation_count()`
// and stamps the per-window delta on each row; a core-python process never calls
// the binding, so for it this number never moves. Nothing in the request path
// ever reads it to change behavior -- remove it and customer requests behave
// identically; you just lose the check. `Relaxed` ordering is enough: we only
// need a correct running total, not ordering against other memory.
pub(crate) static BINDING_OP_COUNT: AtomicU64 = AtomicU64::new(0);

/// Per-attempt wire diagnostics counters (tail-latency root-cause investigation).
///
/// `BINDING_OP_COUNT` counts *operations the caller asked for*; these two count
/// *wire attempts the driver actually made* for them. The driver surfaces every
/// attempt on the response as structured diagnostics
/// (`CosmosResponse::diagnostics()` -> `DiagnosticsContext`): one
/// `RequestDiagnostics` per attempt, each tagged with an `execution_context`
/// (`initial` for a first try, or `retry` / `transport_retry` / `hedging` /
/// `region_failover` / `circuit_breaker_probe` for anything the driver
/// re-issued). We fold those records into two process-wide totals so the perf
/// harness can prove, from inside the binding, how many round trips a run really
/// made -- the thing a raw operation count hides:
///   * `BINDING_ATTEMPT_COUNT` -- total attempts (`request_count()` summed).
///     ~1 per clean create/read; ~2 per PATCH, because the driver runs PATCH as a
///     client-side Read-Modify-Write (an internal Read plus an ETag-guarded
///     Replace), so one PATCH op costs two wire round trips.
///   * `BINDING_RETRY_COUNT` -- attempts whose `execution_context` is NOT
///     `initial`, i.e. genuine driver-issued retries / failovers / hedges. Stays
///     0 unless the retry machinery actually fired (a write retried on 503/429
///     then succeeding records 0 terminal errors but a nonzero retry here).
/// Both are read-only observability, `Relaxed` like `BINDING_OP_COUNT`; nothing
/// in the request path reads them to change behavior. Reading the already-built
/// `DiagnosticsContext` is a cheap in-memory walk (no I/O, no logging), so folding
/// it in is safe even during a latency measurement without perturbing the tail.
pub(crate) static BINDING_ATTEMPT_COUNT: AtomicU64 = AtomicU64::new(0);
pub(crate) static BINDING_RETRY_COUNT: AtomicU64 = AtomicU64::new(0);

/// Total item operations that have entered the rust binding's driver runner in
/// this process (see `BINDING_OP_COUNT`). Exposed to Python as
/// `_rust.operation_count()` so the perf harness can confirm, from a counter
/// bumped inside the binding, that the rust path really ran the work a row claims.
#[pyfunction]
pub(crate) fn operation_count() -> u64 {
    BINDING_OP_COUNT.load(Ordering::Relaxed)
}

/// Total wire attempts recorded across every completed operation in this process
/// (see `BINDING_ATTEMPT_COUNT`). Exposed to Python as `_rust.attempt_count()`.
#[pyfunction]
pub(crate) fn attempt_count() -> u64 {
    BINDING_ATTEMPT_COUNT.load(Ordering::Relaxed)
}

/// Total non-`initial` wire attempts -- driver-issued retries / failovers /
/// hedges -- recorded across every completed operation in this process (see
/// `BINDING_RETRY_COUNT`). Exposed to Python as `_rust.retry_count()`.
#[pyfunction]
pub(crate) fn retry_count() -> u64 {
    BINDING_RETRY_COUNT.load(Ordering::Relaxed)
}

/// Fold one completed operation's diagnostics into the process-wide attempt and
/// retry counters and return the diagnostics string.
///
/// Call once per completed driver operation (success **or** error-with-response).
/// The caller should hold the `DiagnosticsContext` only long enough to call this
/// function; the `Arc` clone inside `diagnostics()` is cheap (no I/O).
///
/// Returns the `Display` string of the diagnostics so the caller can hand it
/// directly to `backend_response_tuple` without an extra `to_string()` call.
pub(super) fn record_diagnostics(diag: Arc<DiagnosticsContext>) -> String {
    BINDING_ATTEMPT_COUNT.fetch_add(diag.request_count() as u64, Ordering::Relaxed);
    let retries = diag
        .requests()
        .iter()
        .filter(|req| req.execution_context().as_str() != "initial")
        .count() as u64;
    BINDING_RETRY_COUNT.fetch_add(retries, Ordering::Relaxed);
    diag.to_string()
}

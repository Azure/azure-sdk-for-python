// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::{Instant, SystemTime, UNIX_EPOCH};

use azure_data_cosmos_driver::diagnostics::DiagnosticsContext;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

fn epoch_nanos(
    instant: Instant,
    reference_instant: Instant,
    reference_system: SystemTime,
) -> Result<u64, &'static str> {
    let elapsed = reference_instant
        .checked_duration_since(instant)
        .ok_or("attempt timestamp is after the clock reference")?;
    let absolute = reference_system
        .checked_sub(elapsed)
        .ok_or("attempt timestamp subtraction overflowed")?;
    let nanos = absolute
        .duration_since(UNIX_EPOCH)
        .map_err(|_| "attempt timestamp precedes the Unix epoch")?
        .as_nanos();
    u64::try_from(nanos).map_err(|_| "attempt timestamp exceeds u64 nanoseconds")
}

/// Private success-only POC contract. Never export bodies, keys, or endpoints.
/// Timing failures are reported as data so telemetry cannot turn a completed
/// write into a retryable operation failure.
pub(super) fn attempt_payload<'py>(
    py: Python<'py>,
    diagnostics: &DiagnosticsContext,
) -> PyResult<Bound<'py, PyDict>> {
    let reference_instant = Instant::now();
    let reference_system = SystemTime::now();
    let payload = PyDict::new_bound(py);
    payload.set_item("schema_version", 1)?;
    payload.set_item("request_count", diagnostics.request_count())?;
    payload.set_item(
        "retained_request_count",
        diagnostics.retained_request_count(),
    )?;
    payload.set_item("error", py.None())?;
    let attempts = PyList::empty_bound(py);
    for request in diagnostics.requests().iter() {
        let times = (|| {
            let start = epoch_nanos(request.started_at(), reference_instant, reference_system)?;
            let end = request
                .completed_at()
                .map(|instant| epoch_nanos(instant, reference_instant, reference_system))
                .transpose()?;
            if end.is_some_and(|end| end < start) {
                return Err("attempt completion precedes its start");
            }
            Ok((start, end))
        })();
        let (start, end) = match times {
            Ok(times) => times,
            Err(message) => {
                payload.set_item("error", message)?;
                payload.set_item("attempts", PyList::empty_bound(py))?;
                return Ok(payload);
            }
        };
        let row = PyDict::new_bound(py);
        row.set_item("start_ns", start)?;
        row.set_item("end_ns", end)?;
        // This is a driver status, not proof of a received HTTP response.
        row.set_item(
            "driver_status_code",
            u16::from(request.status().status_code()),
        )?;
        row.set_item("execution_context", request.execution_context().as_str())?;
        attempts.append(row)?;
    }
    payload.set_item("attempts", attempts)?;
    Ok(payload)
}

// ---------------------------------------------------------------------------
// Binding-invocation counter (a check for the perf drill, not part of serving
// requests)
// ---------------------------------------------------------------------------
//
// Process-wide count at explicit increment sites, including driver runners,
// retained feed-page calls, and local feed-range subset checks. Several sites
// precede driver lookup, so an increment does not prove driver execution, a network
// request, or success. Earlier extraction failures and uninstrumented paths
// (such as metadata lookup) are not counted. Workload deltas include concurrent
// callers in this process. Relaxed ordering does not synchronize other state.
pub(crate) static BINDING_OP_COUNT: AtomicU64 = AtomicU64::new(0);

/// Sum of `request_count()` from diagnostics passed to `record_diagnostics`.
///
/// The driver's count includes compacted attempts for each supplied context.
/// Coverage depends on callers reaching the recording path with diagnostics;
/// cancellations and early errors can bypass it. There is no fixed attempts-per-
/// operation ratio, and neither counter is used to control requests.
pub(crate) static BINDING_ATTEMPT_COUNT: AtomicU64 = AtomicU64::new(0);
/// Number of retained request records whose execution context is not `initial`.
/// Compacted-away records are not inspected, so this is not a complete retry total.
pub(crate) static BINDING_RETRY_COUNT: AtomicU64 = AtomicU64::new(0);

/// Return this process's instrumented runner-entry count.
#[pyfunction(name = "_debug_operation_count")]
pub(crate) fn operation_count() -> u64 {
    BINDING_OP_COUNT.load(Ordering::Relaxed)
}

/// Return summed attempt counts from the diagnostics recorded by this binding.
#[pyfunction(name = "_debug_attempt_count")]
pub(crate) fn attempt_count() -> u64 {
    BINDING_ATTEMPT_COUNT.load(Ordering::Relaxed)
}

/// Return the count of retained non-`initial` records from recorded diagnostics.
#[pyfunction(name = "_debug_retry_count")]
pub(crate) fn retry_count() -> u64 {
    BINDING_RETRY_COUNT.load(Ordering::Relaxed)
}

/// Add one diagnostics context to the process-wide counters and format it.
/// Call once per result path carrying diagnostics, including response-less errors
/// when their diagnostics are available; this function does not deduplicate calls.
///
/// Appends one `pipeline_type/transport_kind` pair per retained request record.
/// Compaction can make this list shorter than `request_count()`, so it does not
/// describe every attempt. Iteration and string formatting add measurement work;
/// their latency impact is not established by these counters.
pub(super) fn record_diagnostics(diag: Arc<DiagnosticsContext>) -> String {
    BINDING_ATTEMPT_COUNT.fetch_add(diag.request_count() as u64, Ordering::Relaxed);
    let requests = diag.requests();
    let retries = requests
        .iter()
        .filter(|req| req.execution_context().as_str() != "initial")
        .count() as u64;
    BINDING_RETRY_COUNT.fetch_add(retries, Ordering::Relaxed);

    let mut summary = diag.to_string();
    append_transport_summary(
        &mut summary,
        requests.iter().map(|request| {
            (
                request.pipeline_type().as_str(),
                request.transport_kind().as_str(),
            )
        }),
    );
    summary
}

fn append_transport_summary<'a>(
    summary: &mut String,
    attempts: impl IntoIterator<Item = (&'a str, &'a str)>,
) {
    summary.push_str(" transports=[");
    for (index, (pipeline_type, transport_kind)) in attempts.into_iter().enumerate() {
        if index > 0 {
            summary.push(',');
        }
        summary.push_str(pipeline_type);
        summary.push('/');
        summary.push_str(transport_kind);
    }
    summary.push(']');
}

#[cfg(test)]
mod tests {
    use super::{append_transport_summary, epoch_nanos};
    use std::time::{Duration, Instant, UNIX_EPOCH};

    #[test]
    fn attempt_times_use_checked_clock_translation() {
        let reference = Instant::now();
        let system = UNIX_EPOCH + Duration::from_secs(10);
        assert_eq!(
            epoch_nanos(reference - Duration::from_millis(25), reference, system),
            Ok(9_975_000_000)
        );
        // Windows Instant resolution can round a one-nanosecond increment away.
        assert!(epoch_nanos(reference + Duration::from_millis(1), reference, system).is_err());
        assert!(epoch_nanos(reference - Duration::from_secs(11), reference, system).is_err());
    }

    #[test]
    fn transport_summary_preserves_attempt_order_and_pipeline() {
        let mut summary = "activity=test requests=2".to_string();
        append_transport_summary(
            &mut summary,
            [("metadata", "gateway"), ("data_plane", "gateway_v2")],
        );

        assert_eq!(
            summary,
            "activity=test requests=2 transports=[metadata/gateway,data_plane/gateway_v2]"
        );
    }

    #[test]
    fn transport_summary_marks_operations_without_wire_attempts() {
        let mut summary = "activity=test requests=0".to_string();
        append_transport_summary(&mut summary, std::iter::empty());

        assert_eq!(summary, "activity=test requests=0 transports=[]");
    }
}

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
#[pyfunction]
pub(crate) fn operation_count() -> u64 {
    BINDING_OP_COUNT.load(Ordering::Relaxed)
}

/// Return summed attempt counts from the diagnostics recorded by this binding.
#[pyfunction]
pub(crate) fn attempt_count() -> u64 {
    BINDING_ATTEMPT_COUNT.load(Ordering::Relaxed)
}

/// Return the count of retained non-`initial` records from recorded diagnostics.
#[pyfunction]
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
    use super::append_transport_summary;

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

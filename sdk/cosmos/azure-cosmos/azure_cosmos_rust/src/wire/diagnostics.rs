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

/// Internal fault-test evidence, separate from the endpoint-free telemetry POC.
pub(super) fn fault_payload<'py>(
    py: Python<'py>,
    diagnostics: &DiagnosticsContext,
) -> PyResult<Bound<'py, PyDict>> {
    let payload = PyDict::new_bound(py);
    payload.set_item("activity_id", diagnostics.activity_id().to_string())?;
    payload.set_item("request_count", diagnostics.request_count())?;
    payload.set_item(
        "retained_request_count",
        diagnostics.retained_request_count(),
    )?;
    let requests = PyList::empty_bound(py);
    for request in diagnostics.requests().iter() {
        let row = PyDict::new_bound(py);
        row.set_item("endpoint", request.endpoint())?;
        row.set_item("region", request.region().map(|region| region.as_str()))?;
        row.set_item("pipeline", request.pipeline_type().as_str())?;
        row.set_item("status", u16::from(request.status().status_code()))?;
        row.set_item(
            "sub_status",
            request
                .status()
                .sub_status()
                .map(|status| status.value())
                .unwrap_or(0),
        )?;
        let evaluations = PyList::empty_bound(py);
        for evaluation in request.fault_injection_evaluations() {
            let entry = PyDict::new_bound(py);
            entry.set_item("rule_id", evaluation.rule_id())?;
            entry.set_item("applied", evaluation.was_applied())?;
            evaluations.append(entry)?;
        }
        row.set_item("evaluations", evaluations)?;
        requests.append(row)?;
    }
    payload.set_item("requests", requests)?;
    Ok(payload)
}

/// Host of an endpoint URL, mirroring the Rust SDK's `server.address`.
fn server_address(endpoint: &str) -> Option<String> {
    url::Url::parse(endpoint)
        .ok()
        .and_then(|url| url.host_str().map(str::to_string))
}

/// Private telemetry contract. Never export bodies, keys, or full endpoints;
/// only the endpoint host is exported, as the Rust SDK does.
/// Timing failures are reported as data so telemetry cannot change the
/// database operation's outcome.
pub(super) fn attempt_payload<'py>(
    py: Python<'py>,
    diagnostics: &DiagnosticsContext,
) -> PyResult<Bound<'py, PyDict>> {
    let reference_instant = Instant::now();
    let reference_system = SystemTime::now();
    let payload = PyDict::new_bound(py);
    payload.set_item("schema_version", 2)?;
    payload.set_item("request_count", diagnostics.request_count())?;
    payload.set_item(
        "retained_request_count",
        diagnostics.retained_request_count(),
    )?;
    payload.set_item("error", py.None())?;
    let status = diagnostics.effective_status();
    payload.set_item(
        "status_code",
        status.map(|status| u16::from(status.status_code())),
    )?;
    payload.set_item(
        "sub_status_code",
        status.and_then(|status| status.sub_status().map(|sub| sub.value())),
    )?;
    payload.set_item("failed", diagnostics.is_failure())?;
    payload.set_item("request_charge", diagnostics.total_request_charge().value())?;
    payload.set_item(
        "contacted_regions",
        diagnostics
            .regions_contacted()
            .iter()
            .map(|region| region.as_str().to_string())
            .collect::<Vec<_>>(),
    )?;
    payload.set_item("machine_id", diagnostics.machine_id())?;
    payload.set_item("hedging_started", diagnostics.hedging_started())?;
    let hedge = diagnostics.hedge_diagnostics();
    payload.set_item(
        "hedge_region",
        hedge
            .and_then(|hedge| hedge.alternate_region())
            .map(|region| region.as_str().to_string()),
    )?;
    payload.set_item(
        "hedge_terminal_state",
        hedge.map(|hedge| hedge.terminal_state().as_str()),
    )?;
    payload.set_item(
        "requested_regions",
        diagnostics
            .requested_regions()
            .iter()
            .map(|requested| requested.region.as_str().to_string())
            .collect::<Vec<_>>(),
    )?;
    payload.set_item(
        "requested_regions_total",
        diagnostics.total_requested_regions(),
    )?;
    payload.set_item(
        "responded_regions",
        diagnostics
            .responded_regions()
            .iter()
            .map(|region| region.as_str().to_string())
            .collect::<Vec<_>>(),
    )?;
    payload.set_item(
        "responded_regions_total",
        diagnostics.total_responded_regions(),
    )?;
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
        row.set_item(
            "sub_status_code",
            request.status().sub_status().map(|sub| sub.value()),
        )?;
        row.set_item("failed", !request.status().is_success())?;
        row.set_item("request_charge", request.request_charge().value())?;
        row.set_item(
            "region",
            request.region().map(|region| region.as_str().to_string()),
        )?;
        row.set_item("server_address", server_address(request.endpoint()))?;
        row.set_item(
            "activity_id",
            request.activity_id().map(|id| id.as_str().to_string()),
        )?;
        row.set_item("operation_name", request.operation_name())?;
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
// precede retaining a driver reference, so an increment does not prove driver execution, a network
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
    use super::{append_transport_summary, epoch_nanos, server_address};
    use std::time::{Duration, Instant, UNIX_EPOCH};

    #[test]
    fn server_address_exports_only_the_endpoint_host() {
        assert_eq!(
            server_address("https://acct-westus.documents.azure.com:443/dbs/x?sig=secret")
                .as_deref(),
            Some("acct-westus.documents.azure.com")
        );
        assert_eq!(server_address("not a url"), None);
    }

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

    // Test-only prototype: preserve production behavior and the Python header contract.
    struct DeferredDiagnostics {
        context: std::sync::Arc<azure_data_cosmos_driver::diagnostics::DiagnosticsContext>,
        text: std::sync::OnceLock<String>,
    }

    impl DeferredDiagnostics {
        fn new(
            context: std::sync::Arc<azure_data_cosmos_driver::diagnostics::DiagnosticsContext>,
        ) -> Self {
            use super::{BINDING_ATTEMPT_COUNT, BINDING_RETRY_COUNT};
            use std::sync::atomic::Ordering;

            // Mirror the eager counter work; parity is checked against record_diagnostics.
            BINDING_ATTEMPT_COUNT.fetch_add(context.request_count() as u64, Ordering::Relaxed);
            let retries = context
                .requests()
                .iter()
                .filter(|request| request.execution_context().as_str() != "initial")
                .count() as u64;
            BINDING_RETRY_COUNT.fetch_add(retries, Ordering::Relaxed);
            Self {
                context,
                text: std::sync::OnceLock::new(),
            }
        }

        fn text(&self) -> &str {
            self.text.get_or_init(|| {
                let mut summary = self.context.to_string();
                append_transport_summary(
                    &mut summary,
                    self.context.requests().iter().map(|request| {
                        (
                            request.pipeline_type().as_str(),
                            request.transport_kind().as_str(),
                        )
                    }),
                );
                summary
            })
        }
    }

    #[test]
    #[ignore = "offline microbenchmark; use --release --ignored --nocapture --test-threads=1"]
    fn measure_deferred_diagnostics() {
        use super::{record_diagnostics, BINDING_ATTEMPT_COUNT, BINDING_RETRY_COUNT};
        use std::hint::black_box;
        use std::sync::atomic::Ordering;
        use std::sync::Arc;

        assert!(!cfg!(debug_assertions), "Use --release for this benchmark");
        let runtime = tokio::runtime::Runtime::new().unwrap();
        let (created, read, conflict) =
            runtime.block_on(crate::wire::response::tests::create_read_and_conflict());
        let counts = || {
            (
                BINDING_ATTEMPT_COUNT.load(Ordering::Relaxed),
                BINDING_RETRY_COUNT.load(Ordering::Relaxed),
            )
        };
        for context in [
            created.diagnostics(),
            read.diagnostics(),
            conflict.response().unwrap().diagnostics(),
        ] {
            let before = counts();
            let expected = record_diagnostics(context.clone());
            let after_eager = counts();
            let deferred = DeferredDiagnostics::new(context);
            let after_deferred = counts();
            assert_eq!(
                (after_eager.0 - before.0, after_eager.1 - before.1),
                (
                    after_deferred.0 - after_eager.0,
                    after_deferred.1 - after_eager.1
                )
            );
            assert!(deferred.text.get().is_none());
            assert_eq!(deferred.text(), expected);
            assert!(std::ptr::eq(
                deferred.text().as_ptr(),
                deferred.text().as_ptr()
            ));
            assert_eq!(counts(), after_deferred, "inspection must not recount");
        }

        let context = read.diagnostics();
        let expected = record_diagnostics(context.clone());
        let weak = Arc::downgrade(&context);
        let deferred = DeferredDiagnostics::new(context.clone());
        drop(read);
        drop(context);
        assert!(weak.upgrade().is_some());
        std::thread::spawn(move || {
            assert_eq!(deferred.text(), expected);
            assert_eq!(deferred.text(), expected);
        })
        .join()
        .unwrap();
        assert!(
            weak.upgrade().is_none(),
            "drop must release retained context"
        );

        let (_, read, _) =
            runtime.block_on(crate::wire::response::tests::create_read_and_conflict());
        let context = read.diagnostics();
        let iterations = 50_000;
        let samples = 12;
        let labels = [
            "eager_unused",
            "deferred_unused",
            "eager_once",
            "deferred_once",
            "eager_three_reads",
            "deferred_three_reads",
        ];
        let mut measurements: [Vec<f64>; 6] = std::array::from_fn(|_| Vec::new());
        let run = |mode: usize| {
            let reads = [0, 1, 3][mode / 2];
            let context = black_box(context.clone());
            if mode % 2 == 0 {
                let text = record_diagnostics(context);
                for _ in 0..reads {
                    black_box(text.as_str());
                }
                drop(black_box(text));
            } else {
                let deferred = DeferredDiagnostics::new(context);
                for _ in 0..reads {
                    black_box(deferred.text());
                }
                drop(black_box(deferred));
            }
        };
        for _ in 0..2_000 {
            for mode in 0..labels.len() {
                run(mode);
            }
        }
        for sample in 0..samples {
            for offset in 0..labels.len() {
                let position = if sample % 2 == 0 {
                    offset
                } else {
                    labels.len() - 1 - offset
                };
                let mode = (sample / 2 + position) % labels.len();
                let start = Instant::now();
                for _ in 0..iterations {
                    run(mode);
                }
                measurements[mode].push(start.elapsed().as_nanos() as f64 / f64::from(iterations));
            }
        }
        let timings: std::collections::BTreeMap<_, _> =
            labels.into_iter().zip(measurements).collect();
        println!(
            "DEFERRED_DIAGNOSTICS_BENCHMARK={}",
            serde_json::json!({
                "scope": "Windows local release microbenchmark; one completed in-memory read; native diagnostics only; no Python conversion or network",
                "iterations_per_sample": iterations,
                "samples": samples,
                "request_count": context.request_count(),
                "retained_request_count": context.requests().len(),
                "nanoseconds_per_operation": timings,
                "content_and_counter_parity": true,
                "cached_reads_do_not_recount": true,
                "context_survives_response_drop_and_thread_transfer": true,
                "context_released_on_holder_drop": true,
                "retention": "Arc retains full diagnostics until holder drop, including after formatting",
                "production_header_contract_changed": false
            })
        );
    }
}

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Per-exporter, content-free observations of evaluation telemetry delivery."""

import json
import logging
from dataclasses import asdict, dataclass
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from azure.core.pipeline import PipelineResponse

from .._model_configurations import AppInsightsConfig


@dataclass
class _ExportObservations:
    """Keep local event attempts separate from ingestion response observations."""

    result_count: int
    event_emitted_count: int = 0
    event_failed_count: int = 0
    attempted_event_count: int = 0
    export_batch_count: int = 0
    export_status: str = "unknown"
    response_count: int = 0
    acknowledged_response_count: int = 0
    unacknowledged_response_count: int = 0
    items_received: Optional[int] = None
    items_accepted: Optional[int] = None
    items_rejected: Optional[int] = None
    count_scope: str = "response_observations_including_retries_and_offline_storage"
    attempt_scope: str = "events_submitted_to_exporter_batches"


class _AppInsightsExportDiagnostics:
    """Own thread-safe observations and correlation identifiers for one emitter."""

    def __init__(self, config: AppInsightsConfig, result_count: int) -> None:
        """Copy diagnostic identifiers without retaining credentials or event content."""
        self._identifiers = {key: config.get(key) for key in ("run_id", "project_id", "correlation_id", "resource_id")}
        self._observations = _ExportObservations(result_count)
        self._http_status_codes: set[int] = set()
        self._lock = Lock()

    def record_events(self, *, emitted: int = 0, failed: int = 0) -> None:
        """Count event construction and submission, not ingestion acceptance."""
        with self._lock:
            self._observations.event_emitted_count += emitted
            self._observations.event_failed_count += failed

    def start_export(self, event_count: int) -> None:
        """Count attempts at the exporter boundary, including repeated batches."""
        with self._lock:
            self._observations.export_batch_count += 1
            self._observations.attempted_event_count += event_count

    def finish_export(self, status: str) -> None:
        """Retain failures even if later exporter batches succeed."""
        priority = {"unknown": 0, "success": 1, "failure": 2, "exception": 3}
        with self._lock:
            if priority[status] > priority[self._observations.export_status]:
                self._observations.export_status = status

    def response_hook(self, response: PipelineResponse) -> None:
        """Observe only HTTP status and validated ingestion acknowledgement counts."""
        status = None
        counts = None
        try:
            status = response.http_response.status_code
            if type(status) is not int or not 100 <= status <= 599:
                status = None
            if status in (200, 206):
                counts = self._read_acknowledgement(response)
        except Exception:  # pylint: disable=broad-except
            # Diagnostics must not turn an unreadable acknowledgement into a failed export.
            counts = None
        with self._lock:
            self._record_response(status, counts)

    @staticmethod
    def _read_acknowledgement(response: PipelineResponse) -> Optional[Tuple[int, int]]:
        """Read fixed count fields without retaining ingestion error messages."""
        body = json.loads(response.http_response.text())
        if not isinstance(body, dict):
            return None
        received, accepted = body.get("itemsReceived"), body.get("itemsAccepted")
        if type(received) is int and type(accepted) is int and 0 <= accepted <= received:
            return received, accepted
        return None

    def _record_response(self, status: Optional[int], counts: Optional[Tuple[int, int]]) -> None:
        """Accumulate response observations while the caller holds the lock."""
        observations = self._observations
        observations.response_count += 1
        if status is not None:
            self._http_status_codes.add(status)
        if counts is None:
            observations.unacknowledged_response_count += 1
            return
        received, accepted = counts
        observations.acknowledged_response_count += 1
        observations.items_received = (observations.items_received or 0) + received
        observations.items_accepted = (observations.items_accepted or 0) + accepted
        observations.items_rejected = (observations.items_rejected or 0) + received - accepted

    def attach_response_hook(self, options: Dict[str, Any]) -> None:
        """Preserve a supplied Azure Core hook when attaching these observations."""
        previous: Optional[Callable[[PipelineResponse], None]] = options.get("raw_response_hook")
        if previous is None:
            options["raw_response_hook"] = self.response_hook
            return

        def observe_response(response: PipelineResponse) -> None:
            """Observe the response and preserve the caller's hook behavior."""
            self.response_hook(response)
            previous(response)

        options["raw_response_hook"] = observe_response

    def log_flush_failure(self, logger: logging.Logger, flush_status: str) -> None:
        """Expose flush failures before potentially blocking exporter shutdown."""
        context = {**self._identifiers, "flush_status": flush_status}
        logger.warning(
            "App Insights evaluation result export flush failed: %s",
            json.dumps(context, sort_keys=True),
            extra=context,
        )

    def log_summary(self, logger: logging.Logger, flush_status: str, emit_failed: bool, shutdown_status: str) -> None:
        """Emit a snapshot without claiming that flush establishes ingestion success."""
        with self._lock:
            summary = {**self._identifiers, **asdict(self._observations)}
            statuses = sorted(self._http_status_codes)
            outcome = self._outcome(flush_status, emit_failed, shutdown_status == "failure", statuses)
        summary.update(
            http_status_codes=statuses,
            flush_status=flush_status,
            shutdown_status=shutdown_status,
            outcome=outcome,
        )
        level = logging.INFO if outcome == "flush_completed" else logging.WARNING
        if outcome in ("emit_exception", "export_failure"):
            level = logging.ERROR
        logger.log(
            level,
            "App Insights evaluation result export summary: %s",
            json.dumps(summary, sort_keys=True),
            extra=summary,
        )

    def _outcome(self, flush_status: str, emit_failed: bool, shutdown_failed: bool, statuses: List[int]) -> str:
        """Select a bounded outcome while preserving all evidence in separate fields."""
        observations = self._observations
        outcomes = (
            (emit_failed, "emit_exception"),
            (flush_status == "timeout", "flush_timeout"),
            (observations.export_status in ("failure", "exception"), "export_failure"),
            (observations.event_failed_count > 0, "event_failure"),
            (206 in statuses or bool(observations.items_rejected), "partial_rejection"),
            (shutdown_failed, "shutdown_failure"),
            (any(status >= 400 for status in statuses), "http_error_observed"),
        )
        return next((outcome for condition, outcome in outcomes if condition), "flush_completed")


class _ExportResultTrackingLogExporter:
    """Delegate to the exporter while retaining failures for every authentication mode."""

    def __init__(self, exporter: Any, diagnostics: _AppInsightsExportDiagnostics, success: Any, failure: Any) -> None:
        """Retain this emitter's exporter and result constants."""
        self._exporter = exporter
        self._diagnostics = diagnostics
        self._success = success
        self._failure = failure

    def export(self, batch: Sequence[Any]) -> Any:
        """Record actual batch attempts without treating their size as accepted events."""
        self._diagnostics.start_export(len(batch))
        try:
            result = self._exporter.export(batch)
        except Exception:  # pylint: disable=broad-except
            self._diagnostics.finish_export("exception")
            # Returning failure keeps OTel best-effort without logging arbitrary exception text.
            return self._failure
        status = "success" if result == self._success else "failure" if result == self._failure else "unknown"
        self._diagnostics.finish_export(status)
        return result

    def shutdown(self) -> None:
        """Shut down the wrapped exporter without changing storage or retry behavior."""
        self._exporter.shutdown()

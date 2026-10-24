# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Offline regressions for content-free evaluation export diagnostics."""

import json
import logging
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.ai.evaluation._evaluate._evaluate import emit_eval_result_events_to_app_insights


LogExportResult = pytest.importorskip("opentelemetry.sdk._logs.export").LogExportResult
AzureMonitorLogExporter = pytest.importorskip("azure.monitor.opentelemetry.exporter").AzureMonitorLogExporter


LOGGER_NAME = "azure.ai.evaluation._evaluate._evaluate"
SUMMARY_MESSAGE = "App Insights evaluation result export summary"
SENSITIVE = "secret-token;InstrumentationKey=private-key;private explanation"


class _Response:
    """Expose only the public response surface used by an Azure Core hook."""

    def __init__(self, status, body):
        """Retain a synthetic ingestion response."""
        self.status_code = status
        self._body = body

    def text(self, encoding=None):
        """Return the ingestion body without involving a network."""
        return json.dumps(self._body)


class _Exporter:
    """Replace the external exporter while retaining the real OTel pipeline."""

    def __init__(self, responses=(), result=LogExportResult.SUCCESS, error=None, barrier=None):
        """Configure boundary responses and exporter completion."""
        self.responses = responses
        self.result = result
        self.error = error
        self.barrier = barrier
        self.options = None
        self.batches = []

    def create(self, **options):
        """Capture public exporter constructor options."""
        self.options = options
        return self

    def export(self, batch):
        """Simulate ingestion responses at the public callback boundary."""
        self.batches.append(tuple(batch))
        if self.barrier:
            self.barrier.wait(timeout=10)
        hook = self.options.get("raw_response_hook")
        for status, body in self.responses:
            if hook:
                hook(SimpleNamespace(http_response=_Response(status, body)))
        if self.error:
            raise self.error
        return self.result

    def shutdown(self):
        """Satisfy the exporter lifecycle without external resources."""


class _IngestionResponse(HttpResponse):
    """Supply a real Azure Core response with a synthetic ingestion body."""

    def __init__(self, request, status, body):
        """Populate only the HTTP response fields needed by the real exporter."""
        super().__init__(request, None)
        self.status_code = status
        self.headers = {"content-type": "application/json"}
        self.reason = "Synthetic response"
        self._body = json.dumps(body).encode("utf-8")

    def body(self):
        """Return bytes consumed by Azure Core's response deserializer."""
        return self._body


class _IngestionTransport(HttpTransport):
    """Exercise the real exporter and HTTP pipeline without network access."""

    def __init__(self, responses):
        """Retain the ordered HTTP responses for this test."""
        self._responses = iter(responses)
        self.request_count = 0

    def open(self):
        """Open no external resources."""

    def close(self):
        """Close no external resources."""

    def __enter__(self):
        """Return the in-memory transport."""
        return self

    def __exit__(self, *args):
        """Exit without external resources."""

    def send(self, request, **kwargs):
        """Return the next response at the HTTP boundary."""
        self.request_count += 1
        status, body = next(self._responses)
        return _IngestionResponse(request, status, body)


def _config(credential_type="ApiKey", suffix="one"):
    """Build a synthetic config with diagnostic-only identifiers."""
    config = {
        "connection_string": "InstrumentationKey=00000000-0000-0000-0000-000000000000",
        "run_id": "run-" + suffix,
        "project_id": "project-" + suffix,
        "correlation_id": "correlation-" + suffix,
        "resource_id": "resource-" + suffix,
    }
    if credential_type is not None:
        config["credential_type"] = credential_type
    if credential_type == "ProjectManagedIdentity":
        config["credential"] = MagicMock()
    return config


def _results(count=2):
    """Return one result object containing multiple criterion events."""
    return [{"results": [{"metric": "coherence", "score": 4} for _ in range(count)], "datasource_item": {}}]


def _summary(caplog, run_id="run-one"):
    """Require exactly one correlated, content-free terminal summary."""
    records = [
        record
        for record in caplog.records
        if record.getMessage().startswith(SUMMARY_MESSAGE) and getattr(record, "run_id", None) == run_id
    ]
    assert len(records) == 1
    record = records[0]
    assert SENSITIVE not in str(record.__dict__)
    assert "connection_string" not in record.__dict__
    assert "Successfully logged" not in caplog.text
    return record


def _emit(exporter, caplog, config=None, results=None):
    """Exercise the production emitter with only the exporter boundary replaced."""
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME), patch(
        "azure.monitor.opentelemetry.exporter.AzureMonitorLogExporter", side_effect=exporter.create
    ):
        emit_eval_result_events_to_app_insights(config or _config(), results if results is not None else _results())
    return _summary(caplog)


@pytest.mark.parametrize("credential_type", ["ApiKey", None, "ProjectManagedIdentity"])
def test_export_failure_never_becomes_flush_success(credential_type, caplog):
    """All authentication paths retain failed export evidence after a completed flush."""
    exporter = _Exporter(result=LogExportResult.FAILURE)
    record = _emit(exporter, caplog, config=_config(credential_type))
    assert record.export_status == "failure"
    assert record.flush_status == "completed"
    assert record.attempted_event_count == 2
    assert record.result_count == 1
    assert record.items_accepted is None
    assert record.levelno >= logging.WARNING


def test_acknowledgement_counts_are_not_result_counts(caplog):
    """Only the ingestion acknowledgement supplies received and accepted counts."""
    exporter = _Exporter(responses=[(200, {"itemsReceived": 2, "itemsAccepted": 2, "errors": []})])
    record = _emit(exporter, caplog)
    assert (record.items_received, record.items_accepted, record.items_rejected) == (2, 2, 0)
    assert record.attempted_event_count == 2
    assert record.result_count == 1
    assert record.export_status == "success"
    assert record.http_status_codes == [200]
    assert record.response_count == record.acknowledged_response_count == 1
    assert record.count_scope == "response_observations_including_retries_and_offline_storage"
    assert record.project_id == "project-one"
    assert record.correlation_id == "correlation-one"
    assert record.resource_id == "resource-one"
    attributes = exporter.batches[0][0].log_record.attributes
    assert "correlation_id" not in attributes and "resource_id" not in attributes
    assert "correlation-one" not in str(attributes) and "resource-one" not in str(attributes)


def test_partial_rejection_remains_explicit_and_content_free(caplog):
    """A partial response cannot be promoted to success even if the exporter returns success."""
    body = {"itemsReceived": 2, "itemsAccepted": 1, "errors": [{"statusCode": 400, "message": SENSITIVE}]}
    record = _emit(_Exporter(responses=[(206, body)]), caplog)
    assert (record.items_received, record.items_accepted, record.items_rejected) == (2, 1, 1)
    assert record.http_status_codes == [206]
    assert record.outcome == "partial_rejection"
    assert record.levelno >= logging.WARNING
    assert SENSITIVE not in caplog.text


def test_flush_timeout_does_not_imply_delivery(caplog):
    """A flush timeout stays explicit even when shutdown later drains the queue."""
    with patch("opentelemetry.sdk._logs.LoggerProvider.force_flush", return_value=False):
        record = _emit(_Exporter(), caplog)
    assert record.flush_status == "timeout"
    assert record.outcome == "flush_timeout"
    assert record.items_accepted is None
    assert record.levelno >= logging.WARNING


def test_thrown_exporter_error_is_best_effort_and_redacted(caplog):
    """An exporter exception is counted without exposing its arbitrary message."""
    record = _emit(_Exporter(error=RuntimeError(SENSITIVE)), caplog)
    assert record.export_status == "exception"
    assert record.items_accepted is None
    assert SENSITIVE not in caplog.text


def test_no_response_keeps_acceptance_unknown(caplog):
    """Successful exporter completion and flush alone cannot establish ingestion."""
    record = _emit(_Exporter(), caplog)
    assert record.export_status == "success"
    assert record.outcome == "flush_completed"
    assert record.items_received is record.items_accepted is record.items_rejected is None
    assert record.response_count == record.acknowledged_response_count == 0


@pytest.mark.parametrize("body", [{"message": SENSITIVE}, {"itemsReceived": 2, "itemsAccepted": 3}, "not an object"])
def test_invalid_acknowledgement_counts_are_unknown(body, caplog):
    """Malformed or inconsistent ingestion counts are never inferred."""
    record = _emit(_Exporter(responses=[(200, body)]), caplog)
    assert record.response_count == 1
    assert record.acknowledged_response_count == 0
    assert record.items_accepted is None
    assert record.unacknowledged_response_count == 1


def test_http_error_response_does_not_expose_body(caplog):
    """A service error provides status, not a fabricated accepted count or response text."""
    record = _emit(_Exporter(responses=[(403, {"message": SENSITIVE})], result=LogExportResult.FAILURE), caplog)
    assert record.http_status_codes == [403]
    assert record.items_accepted is None
    assert record.outcome == "export_failure"
    assert SENSITIVE not in caplog.text


def test_event_construction_failure_is_counted_without_content(caplog):
    """Failed events stay visible even if the remaining events export successfully."""
    results = _results()
    results[0]["results"][0]["sample"] = SENSITIVE
    record = _emit(_Exporter(), caplog, results=results)
    assert record.event_failed_count == 1
    assert record.event_emitted_count == record.attempted_event_count == 1
    assert record.outcome == "event_failure"
    assert SENSITIVE not in caplog.text


def test_exporter_initialization_failure_has_correlated_summary(caplog):
    """Initialization errors remain best-effort and correlated without raw exception text."""
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME), patch(
        "azure.monitor.opentelemetry.exporter.AzureMonitorLogExporter", side_effect=RuntimeError(SENSITIVE)
    ):
        emit_eval_result_events_to_app_insights(_config(), _results())
    record = _summary(caplog)
    assert record.outcome == "emit_exception"
    assert record.flush_status == "not_attempted"
    assert record.items_accepted is None
    assert SENSITIVE not in caplog.text


def test_concurrent_runs_do_not_mutate_global_provider_or_mix_context(caplog):
    """Two simultaneous emitters own independent identifiers and response counters."""
    barrier = Barrier(2)
    exporters = {
        "one": _Exporter(responses=[(200, {"itemsReceived": 2, "itemsAccepted": 2})], barrier=barrier),
        "two": _Exporter(responses=[(206, {"itemsReceived": 2, "itemsAccepted": 1})], barrier=barrier),
    }

    def create(**options):
        """Route synthetic exporters by their supplied connection string."""
        key = options["connection_string"]
        return exporters[key].create(**options)

    configs = [_config(suffix=key) for key in exporters]
    for config, key in zip(configs, exporters):
        config["connection_string"] = key
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME), patch(
        "azure.monitor.opentelemetry.exporter.AzureMonitorLogExporter", side_effect=create
    ), patch("opentelemetry._logs.set_logger_provider") as global_setter, ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda config: emit_eval_result_events_to_app_insights(config, _results()), configs))
    global_setter.assert_not_called()
    for key, accepted in [("one", 2), ("two", 1)]:
        record = _summary(caplog, "run-" + key)
        assert record.items_accepted == accepted
        assert record.project_id == "project-" + key
        assert record.correlation_id == "correlation-" + key
        assert record.resource_id == "resource-" + key


def test_multiple_batches_and_retries_count_observations_not_unique_events(caplog):
    """Retried acknowledgements are explicitly scoped observations, never deduplicated claims."""
    responses = [(500, {"message": SENSITIVE}), (200, {"itemsReceived": 1, "itemsAccepted": 1})]
    with patch.dict("os.environ", {"OTEL_BLRP_MAX_EXPORT_BATCH_SIZE": "1"}):
        record = _emit(_Exporter(responses=responses), caplog)
    assert record.export_batch_count == 2
    assert record.attempted_event_count == 2
    assert record.response_count == 4
    assert record.acknowledged_response_count == 2
    assert record.unacknowledged_response_count == 2
    assert record.items_accepted == 2
    assert record.http_status_codes == [200, 500]
    assert record.count_scope == "response_observations_including_retries_and_offline_storage"


def test_supplied_response_hook_is_preserved(caplog):
    """Adding observations never replaces a caller's existing response hook."""
    from azure.ai.evaluation._evaluate._app_insights_export import _AppInsightsExportDiagnostics

    diagnostics = _AppInsightsExportDiagnostics(_config(), 1)
    original = MagicMock()
    options = {"raw_response_hook": original}
    diagnostics.attach_response_hook(options)
    response = SimpleNamespace(http_response=_Response(200, {"itemsReceived": 3, "itemsAccepted": 3}))
    options["raw_response_hook"](response)
    original.assert_called_once_with(response)
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        diagnostics.log_summary(logging.getLogger(LOGGER_NAME), "completed", False, "completed")
    assert _summary(caplog).items_accepted == 3


def test_unreadable_response_does_not_interrupt_export(caplog):
    """Response-reader exceptions are represented as unknown counts without leaking details."""
    from azure.ai.evaluation._evaluate._app_insights_export import _AppInsightsExportDiagnostics

    diagnostics = _AppInsightsExportDiagnostics(_config(), 1)
    response = SimpleNamespace(http_response=MagicMock(status_code=200))
    response.http_response.text.side_effect = RuntimeError(SENSITIVE)
    diagnostics.response_hook(response)
    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        diagnostics.log_summary(logging.getLogger(LOGGER_NAME), "completed", False, "completed")
    record = _summary(caplog)
    assert record.unacknowledged_response_count == 1
    assert record.items_accepted is None
    assert SENSITIVE not in caplog.text


def test_shutdown_exception_is_reported_without_content(caplog):
    """Exporter shutdown failures remain best-effort and visible."""
    exporter = _Exporter()
    exporter.shutdown = MagicMock(side_effect=RuntimeError(SENSITIVE))
    record = _emit(exporter, caplog)
    assert record.shutdown_status == "failure"
    assert record.outcome == "shutdown_failure"
    assert SENSITIVE not in caplog.text


def test_flush_exception_is_reported_without_content(caplog):
    """Flush exceptions remain distinct from timeout and exporter result failures."""
    with patch("opentelemetry.sdk._logs.LoggerProvider.force_flush", side_effect=RuntimeError(SENSITIVE)):
        record = _emit(_Exporter(), caplog)
    assert record.flush_status == "exception"
    assert record.outcome == "emit_exception"
    assert SENSITIVE not in caplog.text


@pytest.mark.parametrize("raises", [False, True])
def test_flush_failure_is_logged_before_shutdown(raises, caplog):
    """A stalled shutdown must not hide an already observed flush failure."""
    from opentelemetry.sdk._logs import LoggerProvider

    original_shutdown = LoggerProvider.shutdown
    observed_before_shutdown = []

    def shutdown(provider):
        """Observe diagnostics before allowing the real shutdown to drain."""
        observed_before_shutdown.append(
            any(
                record.getMessage().startswith("App Insights evaluation result export flush failed")
                and getattr(record, "run_id", None) == "run-one"
                for record in caplog.records
            )
        )
        original_shutdown(provider)

    behavior = {"side_effect": RuntimeError(SENSITIVE)} if raises else {"return_value": False}
    with patch.object(LoggerProvider, "force_flush", **behavior), patch.object(
        LoggerProvider, "shutdown", autospec=True, side_effect=shutdown
    ):
        record = _emit(_Exporter(), caplog)
    assert observed_before_shutdown[0] is True
    assert record.flush_status == ("exception" if raises else "timeout")


def test_shared_extra_attributes_are_not_modified(caplog):
    """Caller-owned event attributes do not retain run identifiers across emitters."""
    config = _config()
    config["extra_attributes"] = {"source": "test"}
    _emit(_Exporter(), caplog, config=config)
    assert config["extra_attributes"] == {"source": "test"}


@pytest.mark.parametrize("retry", [False, True])
def test_public_hook_reaches_real_exporter_http_pipeline(retry, caplog):
    """Validate constructor hook forwarding and real Azure Core retry observations."""
    responses = [(500, {"message": "synthetic retry"})] if retry else []
    responses.append((200, {"itemsReceived": 2, "itemsAccepted": 2, "errors": []}))
    transport = _IngestionTransport(responses)

    def create(**options):
        """Use the real exporter with in-memory I/O and no background collection."""
        return AzureMonitorLogExporter(
            **options, transport=transport, disable_offline_storage=True, retry_backoff_factor=0
        )

    environment = {
        "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED": "true",
        "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
        "APPLICATIONINSIGHTS_SDKSTATS_DISABLED": "true",
    }
    with patch.dict("os.environ", environment), caplog.at_level(logging.INFO, logger=LOGGER_NAME), patch(
        "azure.monitor.opentelemetry.exporter.AzureMonitorLogExporter", side_effect=create
    ):
        emit_eval_result_events_to_app_insights(_config(), _results())
    record = _summary(caplog)
    assert record.items_received == record.items_accepted == 2
    assert record.items_rejected == 0
    assert record.response_count == transport.request_count == (2 if retry else 1)
    assert record.http_status_codes == ([200, 500] if retry else [200])

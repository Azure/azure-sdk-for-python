# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
from os import environ
from warnings import warn

from opentelemetry.environment_variables import (
    OTEL_LOGS_EXPORTER,
    OTEL_METRICS_EXPORTER,
    OTEL_TRACES_EXPORTER,
)
from opentelemetry.instrumentation.distro import (
    BaseDistro,
)
from opentelemetry.sdk.environment_variables import (
    _OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED,
)

from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.monitor.opentelemetry._constants import (
    _is_attach_enabled,
    _PREVIEW_ENTRY_POINT_WARNING,
)
from azure.monitor.opentelemetry._diagnostics.diagnostic_logging import (
    AzureDiagnosticLogging,
    _ATTACH_FAILURE_DISTRO,
    _ATTACH_SUCCESS_DISTRO,
)
from azure.monitor.opentelemetry._diagnostics.status_logger import (
    AzureStatusLogger,
)

_CONFIG_FAILED_MSG = "Azure Monitor OpenTelemetry Distro failed during configuration: %s"

_logger = logging.getLogger(__name__)


class AzureMonitorDistro(BaseDistro):
    def _configure(self, **kwargs) -> None:
        if not _is_attach_enabled():
            warn(_PREVIEW_ENTRY_POINT_WARNING)
        try:
            _configure_auto_instrumentation()
        except Exception as exc:
            AzureDiagnosticLogging.error(
                "Error occurred auto-instrumenting AzureMonitorDistro" % exc,
                _ATTACH_FAILURE_DISTRO,
            )
            raise exc


def _configure_auto_instrumentation() -> None:
    try:
        AzureStatusLogger.log_status(False, "Distro being configured.")
        environ.setdefault(
            OTEL_METRICS_EXPORTER, "azure_monitor_opentelemetry_exporter"
        )
        environ.setdefault(
            OTEL_TRACES_EXPORTER, "azure_monitor_opentelemetry_exporter"
        )
        environ.setdefault(
            OTEL_LOGS_EXPORTER, "azure_monitor_opentelemetry_exporter"
        )
        environ.setdefault(
            _OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED, "true"
        )
        settings.tracing_implementation = OpenTelemetrySpan
        AzureStatusLogger.log_status(True)
        AzureDiagnosticLogging.info(
            "Azure Monitor OpenTelemetry Distro configured successfully.",
            _ATTACH_SUCCESS_DISTRO
        )
    except Exception as exc:
        AzureStatusLogger.log_status(False, reason=str(exc))
        AzureDiagnosticLogging.error(
            _CONFIG_FAILED_MSG % exc,
            _ATTACH_FAILURE_DISTRO,
        )
        raise exc

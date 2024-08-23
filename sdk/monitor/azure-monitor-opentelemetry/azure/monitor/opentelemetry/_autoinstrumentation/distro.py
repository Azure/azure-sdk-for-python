# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------
from os import environ
from warnings import warn

from opentelemetry.instrumentation.distro import ( # type: ignore
    BaseDistro,
)
from opentelemetry.sdk.environment_variables import (
    _OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED,
    OTEL_EXPERIMENTAL_RESOURCE_DETECTORS,
)

from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.monitor.opentelemetry.exporter._utils import _is_attach_enabled # pylint: disable=import-error,no-name-in-module
from azure.monitor.opentelemetry._constants import (
    _AZURE_APP_SERVICE_RESOURCE_DETECTOR_NAME,
    _AZURE_SDK_INSTRUMENTATION_NAME,
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
from azure.monitor.opentelemetry._utils.configurations import (
    _get_otel_disabled_instrumentations,
)


class AzureMonitorDistro(BaseDistro):
    def _configure(self, **kwargs) -> None:
        if not _is_attach_enabled():
            warn(_PREVIEW_ENTRY_POINT_WARNING)
        try:
            _configure_auto_instrumentation()
            AzureStatusLogger.log_status(True)
            AzureDiagnosticLogging.info(
                "Azure Monitor OpenTelemetry Distro configured successfully.",
                _ATTACH_SUCCESS_DISTRO
            )
        except Exception as e:
            AzureStatusLogger.log_status(False, reason=str(e))
            AzureDiagnosticLogging.error(
                "Azure Monitor OpenTelemetry Distro failed during configuration: %s" % str(e),
                _ATTACH_FAILURE_DISTRO,
            )
            raise e


def _configure_auto_instrumentation() -> None:
    environ.setdefault(
        _OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED, "true"
    )
    environ.setdefault(
        OTEL_EXPERIMENTAL_RESOURCE_DETECTORS, _AZURE_APP_SERVICE_RESOURCE_DETECTOR_NAME
    )
    otel_disabled_instrumentations = _get_otel_disabled_instrumentations()
    if _AZURE_SDK_INSTRUMENTATION_NAME not in otel_disabled_instrumentations:
        settings.tracing_implementation = OpenTelemetrySpan

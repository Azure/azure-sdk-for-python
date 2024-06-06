# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------


from os import environ
from warnings import warn

from opentelemetry.environment_variables import (
    OTEL_LOGS_EXPORTER,
    OTEL_METRICS_EXPORTER,
    OTEL_TRACES_EXPORTER,
)
from opentelemetry.sdk._configuration import _OTelSDKConfigurator

from azure.monitor.opentelemetry.exporter import ApplicationInsightsSampler # pylint: disable=import-error,no-name-in-module
from azure.monitor.opentelemetry.exporter._utils import _is_attach_enabled # pylint: disable=import-error,no-name-in-module
from azure.monitor.opentelemetry._constants import (
    _PREVIEW_ENTRY_POINT_WARNING,
    LOG_EXPORTER_NAMES_ARG,
    METRIC_EXPORTER_NAMES_ARG,
    SAMPLER_ARG,
    TRACE_EXPORTER_NAMES_ARG,
)
from azure.monitor.opentelemetry._diagnostics.diagnostic_logging import (
    AzureDiagnosticLogging,
    _ATTACH_FAILURE_CONFIGURATOR,
    _ATTACH_SUCCESS_CONFIGURATOR,
)
from azure.monitor.opentelemetry._diagnostics.status_logger import (
    AzureStatusLogger,
)


class AzureMonitorConfigurator(_OTelSDKConfigurator):
    def _configure(self, **kwargs):
        if not _is_attach_enabled():
            warn(_PREVIEW_ENTRY_POINT_WARNING)
        try:
            if environ.get(OTEL_TRACES_EXPORTER, "").lower().strip() != "none":
                kwargs.setdefault(TRACE_EXPORTER_NAMES_ARG, ["azure_monitor_opentelemetry_exporter"])
                try:
                    sample_rate = float(environ.get("OTEL_TRACES_SAMPLER_ARG", 1.0))
                except ValueError:
                    sample_rate = 1.0
                kwargs.setdefault(SAMPLER_ARG, ApplicationInsightsSampler(sample_rate))
            if environ.get(OTEL_METRICS_EXPORTER, "").lower().strip() != "none":
                kwargs.setdefault(METRIC_EXPORTER_NAMES_ARG, ["azure_monitor_opentelemetry_exporter"])
            if environ.get(OTEL_LOGS_EXPORTER, "").lower().strip() != "none":
                kwargs.setdefault(LOG_EXPORTER_NAMES_ARG, ["azure_monitor_opentelemetry_exporter"])
            # As of OTel SDK 1.25.0, exporters passed as kwargs will be added to those specified in env vars.
            super()._configure(**kwargs)
            AzureStatusLogger.log_status(True)
            AzureDiagnosticLogging.info(
                "Azure Monitor Configurator configured successfully.",
                _ATTACH_SUCCESS_CONFIGURATOR
            )
        except Exception as e:
            AzureDiagnosticLogging.error(
                "Azure Monitor Configurator failed during configuration: %s" % str(e),
                _ATTACH_FAILURE_CONFIGURATOR,
            )
            raise e

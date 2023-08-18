# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------
from logging import getLogger
from typing import Dict, cast

from opentelemetry._logs import get_logger_provider, set_logger_provider
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import get_tracer_provider, set_tracer_provider
from pkg_resources import iter_entry_points  # type: ignore

from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.monitor.opentelemetry._constants import (
    DISABLE_AZURE_CORE_TRACING_ARG,
    DISABLE_LOGGING_ARG,
    DISABLE_METRICS_ARG,
    DISABLE_TRACING_ARG,
    DISABLED_INSTRUMENTATIONS_ARG,
    LOGGING_EXPORT_INTERVAL_MS_ARG,
    SAMPLING_RATIO_ARG,
)
from azure.monitor.opentelemetry._types import ConfigurationValue
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.dependencies import (
    get_dependency_conflicts,
)
from azure.monitor.opentelemetry._vendor.v0_40b0.opentelemetry.instrumentation.instrumentor import (
    BaseInstrumentor,
)
from azure.monitor.opentelemetry.exporter import (  # pylint: disable=import-error
    ApplicationInsightsSampler,
    AzureMonitorLogExporter,
    AzureMonitorMetricExporter,
    AzureMonitorTraceExporter,
)
from azure.monitor.opentelemetry.util._configurations import _get_configurations

_logger = getLogger(__name__)


_SUPPORTED_INSTRUMENTED_LIBRARIES_DEPENDENCIES_MAP = {
    "django": ("django >= 1.10",),
    "fastapi": ("fastapi ~= 0.58",),
    "flask": ("flask >= 1.0, < 3.0",),
    "psycopg2": ("psycopg2 >= 2.7.3.1",),
    "requests": ("requests ~= 2.0",),
    "urllib": tuple(),
    "urllib3": ("urllib3 >= 1.0.0, < 3.0.0",),
}


def configure_azure_monitor(**kwargs) -> None:
    """
    This function works as a configuration layer that allows the
    end user to configure OpenTelemetry and Azure monitor components. The
    configuration can be done via arguments passed to this function.
    :keyword str connection_string: Connection string for your Application Insights resource.
    :keyword ManagedIdentityCredential/ClientSecretCredential credential: Token credential, such as
    ManagedIdentityCredential or ClientSecretCredential, used for Azure Active Directory (AAD) authentication. Defaults
    to None.
    :keyword bool disable_offline_storage: Boolean value to determine whether to disable storing failed telemetry
    records for retry. Defaults to `False`.
    :keyword str storage_directory: Storage directory in which to store retry files. Defaults to
    `<tempfile.gettempdir()>/Microsoft/AzureMonitor/opentelemetry-python-<your-instrumentation-key>`.
    :rtype: None
    """

    configurations = _get_configurations(**kwargs)

    disable_tracing = configurations[DISABLE_TRACING_ARG]
    disable_logging = configurations[DISABLE_LOGGING_ARG]
    disable_metrics = configurations[DISABLE_METRICS_ARG]

    # Setup tracing pipeline
    if not disable_tracing:
        _setup_tracing(configurations)

    # Setup logging pipeline
    if not disable_logging:
        _setup_logging(configurations)

    # Setup metrics pipeline
    if not disable_metrics:
        _setup_metrics(configurations)

    # Setup instrumentations
    # Instrumentations need to be setup last so to use the global providers
    # instanstiated in the other setup steps
    _setup_instrumentations(configurations)


def _setup_tracing(configurations: Dict[str, ConfigurationValue]):
    sampling_ratio = configurations[SAMPLING_RATIO_ARG]
    tracer_provider = TracerProvider(
        sampler=ApplicationInsightsSampler(sampling_ratio=cast(float, sampling_ratio)),
    )
    set_tracer_provider(tracer_provider)
    trace_exporter = AzureMonitorTraceExporter(**configurations)
    span_processor = BatchSpanProcessor(
        trace_exporter,
    )
    get_tracer_provider().add_span_processor(span_processor)
    disable_azure_core_tracing = configurations[DISABLE_AZURE_CORE_TRACING_ARG]
    if not disable_azure_core_tracing:
        settings.tracing_implementation = OpenTelemetrySpan


def _setup_logging(configurations: Dict[str, ConfigurationValue]):
    # TODO: Remove after upgrading to OTel SDK 1.18
    logging_export_interval_ms = configurations[LOGGING_EXPORT_INTERVAL_MS_ARG]
    logger_provider = LoggerProvider()
    set_logger_provider(logger_provider)
    log_exporter = AzureMonitorLogExporter(**configurations)
    log_record_processor = BatchLogRecordProcessor(
        log_exporter,
        schedule_delay_millis=cast(int, logging_export_interval_ms),
    )
    get_logger_provider().add_log_record_processor(log_record_processor)
    handler = LoggingHandler(logger_provider=get_logger_provider())
    getLogger().addHandler(handler)


def _setup_metrics(configurations: Dict[str, ConfigurationValue]):
    metric_exporter = AzureMonitorMetricExporter(**configurations)
    reader = PeriodicExportingMetricReader(metric_exporter)
    meter_provider = MeterProvider(
        metric_readers=[reader],
    )
    set_meter_provider(meter_provider)


def _setup_instrumentations(configurations: Dict[str, ConfigurationValue]):
    disabled_instrumentations = configurations[DISABLED_INSTRUMENTATIONS_ARG]

    # use pkg_resources for now until https://github.com/open-telemetry/opentelemetry-python/pull/3168 is merged
    for entry_point in iter_entry_points(
        "azure_monitor_opentelemetry_instrumentor"
    ):
        lib_name = entry_point.name
        if lib_name not in _SUPPORTED_INSTRUMENTED_LIBRARIES_DEPENDENCIES_MAP:
            continue
        if entry_point.name in disabled_instrumentations:
            _logger.debug(
                "Instrumentation skipped for library %s", entry_point.name
            )
            continue
        try:
            # Check if dependent libraries/version are installed
            instruments = _SUPPORTED_INSTRUMENTED_LIBRARIES_DEPENDENCIES_MAP[
                lib_name
            ]
            conflict = get_dependency_conflicts(instruments)
            if conflict:
                _logger.debug(
                    "Skipping instrumentation %s: %s",
                    entry_point.name,
                    conflict,
                )
                continue
            # Load the instrumentor via entrypoint
            instrumentor: BaseInstrumentor = entry_point.load()
            # tell instrumentation to not run dep checks again as we already did it above
            instrumentor().instrument(skip_dep_check=True)
        except Exception as ex:  # pylint: disable=broad-except
            _logger.warning(
                "Exception occurred when instrumenting: %s.",
                lib_name,
                exc_info=ex,
            )

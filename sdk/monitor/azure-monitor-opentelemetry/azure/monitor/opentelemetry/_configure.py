# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------
from logging import getLogger
from typing import Dict, List, cast

from opentelemetry._logs import set_logger_provider
from opentelemetry.instrumentation.dependencies import (
    get_dist_dependency_conflicts,
)
from opentelemetry.instrumentation.instrumentor import ( # type: ignore
    BaseInstrumentor,
)
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_tracer_provider
from pkg_resources import iter_entry_points  # type: ignore

from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.monitor.opentelemetry._constants import (
    _ALL_SUPPORTED_INSTRUMENTED_LIBRARIES,
    _AZURE_SDK_INSTRUMENTATION_NAME,
    DISABLE_LOGGING_ARG,
    DISABLE_METRICS_ARG,
    DISABLE_TRACING_ARG,
    ENABLE_LIVE_METRICS_ARG,
    LOGGER_NAME_ARG,
    RESOURCE_ARG,
    SAMPLING_RATIO_ARG,
    SPAN_PROCESSORS_ARG,
    VIEWS_ARG,
)
from azure.monitor.opentelemetry._types import ConfigurationValue
from azure.monitor.opentelemetry.exporter._quickpulse import enable_live_metrics  # pylint: disable=import-error,no-name-in-module
from azure.monitor.opentelemetry.exporter._quickpulse._processor import (  # pylint: disable=import-error,no-name-in-module
    _QuickpulseLogRecordProcessor,
    _QuickpulseSpanProcessor,
)
from azure.monitor.opentelemetry.exporter import (  # pylint: disable=import-error,no-name-in-module
    ApplicationInsightsSampler,
    AzureMonitorLogExporter,
    AzureMonitorMetricExporter,
    AzureMonitorTraceExporter,
)
from azure.monitor.opentelemetry.exporter._utils import _is_attach_enabled # pylint: disable=import-error,no-name-in-module
from azure.monitor.opentelemetry._diagnostics.diagnostic_logging import (
    _DISTRO_DETECTS_ATTACH,
    AzureDiagnosticLogging,
)
from azure.monitor.opentelemetry._utils.configurations import (
    _get_configurations,
    _is_instrumentation_enabled,
)

_logger = getLogger(__name__)


def configure_azure_monitor(**kwargs) -> None:  # pylint: disable=C4758
    """This function works as a configuration layer that allows the
    end user to configure OpenTelemetry and Azure monitor components. The
    configuration can be done via arguments passed to this function.

    :keyword str connection_string: Connection string for your Application Insights resource.
    :keyword credential: Token credential, such as `ManagedIdentityCredential` or `ClientSecretCredential`,
     used for Azure Active Directory (AAD) authentication. Defaults to `None`.
    :paramtype credential: ~azure.core.credentials.TokenCredential or None
    :keyword bool disable_offline_storage: Boolean value to determine whether to disable storing failed
     telemetry records for retry. Defaults to `False`.
    :keyword str logger_name: The name of the Python logger that telemetry will be collected.
    :keyword dict instrumentation_options: A nested dictionary that determines which instrumentations
     to enable or disable.  Instrumentations are referred to by their Library Names. For example,
     `{"azure_sdk": {"enabled": False}, "flask": {"enabled": False}, "django": {"enabled": True}}`
     will disable Azure Core Tracing and the Flask instrumentation but leave Django and the other default
     instrumentations enabled.
    :keyword ~opentelemetry.sdk.resources.Resource resource: OpenTelemetry Resource object. Passed in Resource
     Attributes take priority over default attributes and those from Resource Detectors.
    :keyword list[~opentelemetry.sdk.trace.SpanProcessor] span_processors: List of `SpanProcessor` objects
     to process every span prior to exporting. Will be run sequentially.
    :keyword bool enable_live_metrics: Boolean value to determine whether to enable live metrics feature.
     Defaults to `False`.
    :keyword str storage_directory: Storage directory in which to store retry files. Defaults to
     `<tempfile.gettempdir()>/Microsoft/AzureMonitor/opentelemetry-python-<your-instrumentation-key>`.
    :keyword list[~opentelemetry.sdk.metrics.view.View] views: List of `View` objects to configure and filter
     metric output.
    :rtype: None
    """

    _send_attach_warning()

    configurations = _get_configurations(**kwargs)

    disable_tracing = configurations[DISABLE_TRACING_ARG]
    disable_logging = configurations[DISABLE_LOGGING_ARG]
    disable_metrics = configurations[DISABLE_METRICS_ARG]
    enable_live_metrics_config = configurations[ENABLE_LIVE_METRICS_ARG]

    # Setup tracing pipeline
    if not disable_tracing:
        _setup_tracing(configurations)

    # Setup logging pipeline
    if not disable_logging:
        _setup_logging(configurations)

    # Setup metrics pipeline
    if not disable_metrics:
        _setup_metrics(configurations)

    # Setup live metrics
    if enable_live_metrics_config:
        _setup_live_metrics(configurations)

    # Setup instrumentations
    # Instrumentations need to be setup last so to use the global providers
    # instanstiated in the other setup steps
    _setup_instrumentations(configurations)


def _setup_tracing(configurations: Dict[str, ConfigurationValue]):
    resource: Resource = configurations[RESOURCE_ARG] # type: ignore
    sampling_ratio = configurations[SAMPLING_RATIO_ARG]
    tracer_provider = TracerProvider(
        sampler=ApplicationInsightsSampler(sampling_ratio=cast(float, sampling_ratio)),
        resource=resource
    )
    for span_processor in configurations[SPAN_PROCESSORS_ARG]: # type: ignore
        tracer_provider.add_span_processor(span_processor) # type: ignore
    if configurations.get(ENABLE_LIVE_METRICS_ARG):
        qsp = _QuickpulseSpanProcessor()
        tracer_provider.add_span_processor(qsp)
    trace_exporter = AzureMonitorTraceExporter(**configurations)
    bsp = BatchSpanProcessor(
        trace_exporter,
    )
    tracer_provider.add_span_processor(bsp)
    set_tracer_provider(tracer_provider)
    if _is_instrumentation_enabled(configurations, _AZURE_SDK_INSTRUMENTATION_NAME):
        settings.tracing_implementation = OpenTelemetrySpan


def _setup_logging(configurations: Dict[str, ConfigurationValue]):
    resource: Resource = configurations[RESOURCE_ARG] # type: ignore
    logger_provider = LoggerProvider(resource=resource)
    if configurations.get(ENABLE_LIVE_METRICS_ARG):
        qlp = _QuickpulseLogRecordProcessor()
        logger_provider.add_log_record_processor(qlp)
    log_exporter = AzureMonitorLogExporter(**configurations)
    log_record_processor = BatchLogRecordProcessor(
        log_exporter,
    )
    logger_provider.add_log_record_processor(log_record_processor)
    set_logger_provider(logger_provider)
    handler = LoggingHandler(logger_provider=logger_provider)
    logger_name: str = configurations[LOGGER_NAME_ARG] # type: ignore
    getLogger(logger_name).addHandler(handler)


def _setup_metrics(configurations: Dict[str, ConfigurationValue]):
    resource: Resource = configurations[RESOURCE_ARG] # type: ignore
    views: List[View] = configurations[VIEWS_ARG] # type: ignore
    metric_exporter = AzureMonitorMetricExporter(**configurations)
    reader = PeriodicExportingMetricReader(metric_exporter)
    meter_provider = MeterProvider(
        metric_readers=[reader],
        resource=resource,
        views=views,
    )
    set_meter_provider(meter_provider)


def _setup_live_metrics(configurations):
    enable_live_metrics(**configurations)


def _setup_instrumentations(configurations: Dict[str, ConfigurationValue]):
    # use pkg_resources for now until https://github.com/open-telemetry/opentelemetry-python/pull/3168 is merged
    for entry_point in iter_entry_points(
        "opentelemetry_instrumentor"
    ):
        lib_name = entry_point.name
        if lib_name not in _ALL_SUPPORTED_INSTRUMENTED_LIBRARIES:
            continue
        if not _is_instrumentation_enabled(configurations, lib_name):
            _logger.debug(
                "Instrumentation skipped for library %s", entry_point.name
            )
            continue
        try:
            # Check if dependent libraries/version are installed
            conflict = get_dist_dependency_conflicts(entry_point.dist) # type: ignore
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


def _send_attach_warning():
    if _is_attach_enabled():
        AzureDiagnosticLogging.warning(
            "Distro detected that automatic attach may have occurred. Check your data to ensure "
            "that telemetry is not being duplicated. This may impact your cost.",
            _DISTRO_DETECTS_ATTACH)

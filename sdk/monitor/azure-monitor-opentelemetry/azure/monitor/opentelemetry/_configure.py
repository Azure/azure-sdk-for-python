# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------
from functools import cached_property
from logging import getLogger, Formatter
from typing import Dict, List, Optional, cast, Any

from opentelemetry.instrumentation.instrumentor import (  # type: ignore
    BaseInstrumentor,
)
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, MetricReader
from opentelemetry.sdk.metrics.view import View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import set_tracer_provider
from opentelemetry.util._importlib_metadata import (
    EntryPoint,
    distributions,
    entry_points,
)

from azure.monitor.opentelemetry._browser_sdk_loader import (
    setup_snippet_injection
)
from azure.monitor.opentelemetry._browser_sdk_loader._config import BrowserSDKConfig
from azure.monitor.opentelemetry._constants import (
    _ALL_SUPPORTED_INSTRUMENTED_LIBRARIES,
    _AZURE_SDK_INSTRUMENTATION_NAME,
    BROWSER_SDK_LOADER_CONFIG_ARG,
    DISABLE_LOGGING_ARG,
    DISABLE_METRICS_ARG,
    DISABLE_TRACING_ARG,
    ENABLE_LIVE_METRICS_ARG,
    ENABLE_PERFORMANCE_COUNTERS_ARG,
    LOGGER_NAME_ARG,
    LOGGING_FORMATTER_ARG,
    RESOURCE_ARG,
    SAMPLING_RATIO_ARG,
    SAMPLING_TRACES_PER_SECOND_ARG,
    SPAN_PROCESSORS_ARG,
    LOG_RECORD_PROCESSORS_ARG,
    METRIC_READERS_ARG,
    VIEWS_ARG,
    ENABLE_TRACE_BASED_SAMPLING_ARG,
    SAMPLING_ARG,
    SAMPLER_TYPE,
)
from azure.monitor.opentelemetry._types import ConfigurationValue
from azure.monitor.opentelemetry.exporter._quickpulse import (  # pylint: disable=import-error,no-name-in-module
    enable_live_metrics,
)
from azure.monitor.opentelemetry.exporter._performance_counters import (  # pylint: disable=import-error,no-name-in-module
    enable_performance_counters,
)
from azure.monitor.opentelemetry.exporter._performance_counters._processor import (  # pylint: disable=import-error,no-name-in-module
    _PerformanceCountersLogRecordProcessor,
    _PerformanceCountersSpanProcessor,
)
from azure.monitor.opentelemetry.exporter._quickpulse._processor import (  # pylint: disable=import-error,no-name-in-module
    _QuickpulseLogRecordProcessor,
    _QuickpulseSpanProcessor,
)
from azure.monitor.opentelemetry.exporter import (  # pylint: disable=import-error,no-name-in-module
    ApplicationInsightsSampler,
    AzureMonitorMetricExporter,
    AzureMonitorTraceExporter,
    RateLimitedSampler,
)
from azure.monitor.opentelemetry.exporter._utils import (  # pylint: disable=import-error,no-name-in-module
    _is_attach_enabled,
    _is_on_functions,
)
from azure.monitor.opentelemetry._diagnostics.diagnostic_logging import (
    _DISTRO_DETECTS_ATTACH,
    AzureDiagnosticLogging,
)
from azure.monitor.opentelemetry._utils.configurations import (
    _get_configurations,
    _is_instrumentation_enabled,
    _get_sampler_from_name,
)
from azure.monitor.opentelemetry._utils.instrumentation import (
    get_dist_dependency_conflicts,
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
    :keyword list[~opentelemetry.sdk._logs.LogRecordProcessor] log_record_processors: List of `LogRecordProcessor`
     objects to process every log record prior to exporting. Will be run sequentially.
    :keyword list[~opentelemetry.sdk.metrics.MetricReader] metric_readers: List of MetricReader objects to read and
     export metrics. Each reader can have its own exporter and collection interval.
    :keyword bool enable_live_metrics: Boolean value to determine whether to enable live metrics feature.
     Defaults to `False`.
    :keyword bool enable_performance_counters: Boolean value to determine whether to enable performance counters.
     Defaults to `True`.
    :keyword str storage_directory: Storage directory in which to store retry files. Defaults to
     `<tempfile.gettempdir()>/Microsoft/AzureMonitor/opentelemetry-python-<your-instrumentation-key>`.
    :keyword list[~opentelemetry.sdk.metrics.view.View] views: List of `View` objects to configure and filter
     metric output.
    :keyword bool enable_trace_based_sampling_for_logs: Boolean value to determine whether to enable trace based
     sampling for logs. Defaults to `False`
    :keyword dict browser_sdk_loader_config: Configuration dictionary for browser SDK loader behavior.
     Supports keys like 'connection_string' (separate connection string for browser SDK), 'enabled' (boolean),
     and framework-specific options. Defaults to `{}`.
    :rtype: None
    """

    _send_attach_warning()

    configurations = _get_configurations(**kwargs)

    disable_tracing = configurations[DISABLE_TRACING_ARG]
    disable_logging = configurations[DISABLE_LOGGING_ARG]
    disable_metrics = configurations[DISABLE_METRICS_ARG]
    enable_live_metrics_config = configurations[ENABLE_LIVE_METRICS_ARG]

    # Set up metrics pipeline
    # Set up metrics with Performance Counters before _PerformanceCountersSpanProcessor and
    # _PerformanceCountersLogRecordProcessor. This avoids a circular dependency in the case that Performance Counter
    # setup produces a log.
    if not disable_metrics:
        _setup_metrics(configurations)

    # Set up live metrics
    if enable_live_metrics_config:
        _setup_live_metrics(configurations)

    # Set up tracing pipeline
    if not disable_tracing:
        _setup_tracing(configurations)

    # Set up logging pipeline
    if not disable_logging:
        _setup_logging(configurations)

    # Set up instrumentations
    # Instrumentations need to be set up last so to use the global providers
    # instantiated in the other setup steps
    _setup_instrumentations(configurations)

    # Setup browser SDK loader for supported frameworks
    _setup_browser_sdk_loader(configurations)


def _setup_tracing(configurations: Dict[str, ConfigurationValue]):
    resource: Resource = configurations[RESOURCE_ARG]  # type: ignore
    enable_performance_counters_config = configurations[ENABLE_PERFORMANCE_COUNTERS_ARG]
    if SAMPLING_ARG in configurations:
        sampler_arg = configurations[SAMPLING_ARG]
        sampler_type = configurations[SAMPLER_TYPE]
        sampler = _get_sampler_from_name(sampler_type, sampler_arg)
        tracer_provider = TracerProvider(sampler=sampler, resource=resource)
    elif SAMPLING_TRACES_PER_SECOND_ARG in configurations:
        traces_per_second = configurations[SAMPLING_TRACES_PER_SECOND_ARG]
        tracer_provider = TracerProvider(
            sampler=RateLimitedSampler(target_spans_per_second_limit=cast(float, traces_per_second)), resource=resource
        )
    else:
        sampling_ratio = configurations[SAMPLING_RATIO_ARG]
        tracer_provider = TracerProvider(
            sampler=ApplicationInsightsSampler(sampling_ratio=cast(float, sampling_ratio)), resource=resource
        )

    for span_processor in configurations[SPAN_PROCESSORS_ARG]:  # type: ignore
        tracer_provider.add_span_processor(span_processor)  # type: ignore
    if configurations.get(ENABLE_LIVE_METRICS_ARG):
        qsp = _QuickpulseSpanProcessor()
        tracer_provider.add_span_processor(qsp)
    if enable_performance_counters_config:
        pcsp = _PerformanceCountersSpanProcessor()
        tracer_provider.add_span_processor(pcsp)
    trace_exporter = AzureMonitorTraceExporter(**configurations)
    bsp = BatchSpanProcessor(
        trace_exporter,
    )
    tracer_provider.add_span_processor(bsp)
    set_tracer_provider(tracer_provider)

    if _is_instrumentation_enabled(configurations, _AZURE_SDK_INSTRUMENTATION_NAME):
        try:
            from azure.core.settings import settings
            from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan

            settings.tracing_implementation = OpenTelemetrySpan
        except ImportError as ex:
            # This could possibly be due to breaking change in upstream OpenTelemetry
            # Advise user to upgrade to latest OpenTelemetry version
            _logger.warning(  # pylint: disable=do-not-log-exceptions-if-not-debug
                "Exception occurred when importing Azure SDK Tracing."
                "Please upgrade to the latest OpenTelemetry version: %s.",
                ex,
            )
        except Exception as ex:  # pylint: disable=broad-except
            _logger.warning(  # pylint: disable=do-not-log-exceptions-if-not-debug
                "Exception occurred when setting Azure SDK Tracing: %s.",
                ex,
            )


def _setup_logging(configurations: Dict[str, ConfigurationValue]):
    # Setup logging
    # Use try catch while signal is experimental
    try:
        from opentelemetry._logs import set_logger_provider
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from azure.monitor.opentelemetry.exporter.export.logs._processor import _AzureBatchLogRecordProcessor

        from azure.monitor.opentelemetry.exporter import (  # pylint: disable=import-error,no-name-in-module
            AzureMonitorLogExporter,
        )

        resource: Resource = configurations[RESOURCE_ARG]  # type: ignore
        enable_performance_counters_config = configurations[ENABLE_PERFORMANCE_COUNTERS_ARG]
        logger_provider = LoggerProvider(resource=resource)
        enable_trace_based_sampling_for_logs = configurations[ENABLE_TRACE_BASED_SAMPLING_ARG]
        for custom_log_record_processor in configurations[LOG_RECORD_PROCESSORS_ARG]:  # type: ignore
            logger_provider.add_log_record_processor(custom_log_record_processor)  # type: ignore
        if configurations.get(ENABLE_LIVE_METRICS_ARG):
            qlp = _QuickpulseLogRecordProcessor()
            logger_provider.add_log_record_processor(qlp)
        if enable_performance_counters_config:
            pclp = _PerformanceCountersLogRecordProcessor()
            logger_provider.add_log_record_processor(pclp)
        log_exporter = AzureMonitorLogExporter(**configurations)
        log_record_processor = _AzureBatchLogRecordProcessor(
            log_exporter,
            {"enable_trace_based_sampling_for_logs": enable_trace_based_sampling_for_logs},
        )
        logger_provider.add_log_record_processor(log_record_processor)
        set_logger_provider(logger_provider)
        logger_name: str = configurations[LOGGER_NAME_ARG]  # type: ignore
        logging_formatter: Optional[Formatter] = configurations.get(LOGGING_FORMATTER_ARG)  # type: ignore
        logger = getLogger(logger_name)
        # Only add OpenTelemetry LoggingHandler if logger does not already have the handler
        # This is to prevent most duplicate logging telemetry
        if not any(isinstance(handler, LoggingHandler) for handler in logger.handlers):
            handler = LoggingHandler(logger_provider=logger_provider)
            if logging_formatter:
                try:
                    handler.setFormatter(logging_formatter)
                except Exception as ex:  # pylint: disable=broad-except
                    _logger.warning(  # pylint: disable=do-not-log-exceptions-if-not-debug
                        "Exception occurred when adding logging Formatter: %s.",
                        ex,
                    )
            logger.addHandler(handler)

        # Setup Events
        try:
            from opentelemetry._events import _set_event_logger_provider
            from opentelemetry.sdk._events import EventLoggerProvider

            event_provider = EventLoggerProvider(logger_provider)
            _set_event_logger_provider(event_provider, False)
        except ImportError as ex:
            # If the events is not available, we will not set it up.
            # This could possibly be due to breaking change in upstream OpenTelemetry
            # Advise user to upgrade to latest OpenTelemetry version
            _logger.warning(  # pylint: disable=do-not-log-exceptions-if-not-debug
                "Exception occurred when setting up Events. Please upgrade to the latest OpenTelemetry version: %s.",
                ex,
            )
    except ImportError as ex:
        # If the events is not available, we will not set it up.
        # This could possibly be due to breaking change in upstream OpenTelemetry
        # Advise user to upgrade to latest OpenTelemetry version
        _logger.warning(  # pylint: disable=do-not-log-exceptions-if-not-debug
            "Exception occurred when setting up Logging. Please upgrade to the latest OpenTelemetry version: %s.",
            ex,
        )


def _setup_metrics(configurations: Dict[str, ConfigurationValue]):
    resource: Resource = configurations[RESOURCE_ARG]  # type: ignore
    views: List[View] = configurations[VIEWS_ARG]  # type: ignore
    readers: list[MetricReader] = configurations[METRIC_READERS_ARG]  # type: ignore
    enable_performance_counters_config = configurations[ENABLE_PERFORMANCE_COUNTERS_ARG]
    metric_exporter = AzureMonitorMetricExporter(**configurations)
    readers.append(PeriodicExportingMetricReader(metric_exporter))
    meter_provider = MeterProvider(
        metric_readers=readers,
        resource=resource,
        views=views,
    )
    if enable_performance_counters_config:
        enable_performance_counters(meter_provider=meter_provider)
    set_meter_provider(meter_provider)


def _setup_live_metrics(configurations):
    enable_live_metrics(**configurations)


class _EntryPointDistFinder:
    @cached_property
    def _mapping(self):
        return {self._key_for(ep): dist for dist in distributions() for ep in dist.entry_points}

    def dist_for(self, entry_point: EntryPoint):
        dist = getattr(entry_point, "dist", None)
        if dist:
            return dist

        return self._mapping.get(self._key_for(entry_point))

    @staticmethod
    def _key_for(entry_point: EntryPoint):
        return f"{entry_point.group}:{entry_point.name}:{entry_point.value}"


def _setup_instrumentations(configurations: Dict[str, ConfigurationValue]):
    entry_point_finder = _EntryPointDistFinder()
    # use pkg_resources for now until https://github.com/open-telemetry/opentelemetry-python/pull/3168 is merged
    for entry_point in entry_points(group="opentelemetry_instrumentor"):
        lib_name = entry_point.name
        if lib_name not in _ALL_SUPPORTED_INSTRUMENTED_LIBRARIES:
            continue
        if not _is_instrumentation_enabled(configurations, lib_name):
            _logger.debug("Instrumentation skipped for library %s", entry_point.name)
            continue
        try:
            # Check if dependent libraries/version are installed
            entry_point_dist = entry_point_finder.dist_for(entry_point)  # type: ignore
            conflict = get_dist_dependency_conflicts(entry_point_dist)  # type: ignore
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
    _setup_additional_azure_sdk_instrumentations(configurations)


def _send_attach_warning():
    if _is_attach_enabled() and not _is_on_functions():
        AzureDiagnosticLogging.warning(
            "Distro detected that automatic attach may have occurred. Check your data to ensure "
            "that telemetry is not being duplicated. This may impact your cost.",
            _DISTRO_DETECTS_ATTACH,
        )


def _setup_additional_azure_sdk_instrumentations(configurations: Dict[str, ConfigurationValue]):
    if _AZURE_SDK_INSTRUMENTATION_NAME not in _ALL_SUPPORTED_INSTRUMENTED_LIBRARIES:
        return

    if not _is_instrumentation_enabled(configurations, _AZURE_SDK_INSTRUMENTATION_NAME):
        _logger.debug("Instrumentation skipped for library azure_sdk")
        return

    instrumentors = [
        ("azure.ai.inference.tracing", "AIInferenceInstrumentor"),
        ("azure.ai.agents.telemetry", "AIAgentsInstrumentor"),
        ("azure.ai.projects.telemetry", "AIProjectInstrumentor"),
    ]

    for module_path, class_name in instrumentors:
        instrumentor_imported = False
        try:
            module = __import__(module_path, fromlist=[class_name])
            instrumentor_imported = True
        except Exception as ex:  # pylint: disable=broad-except
            _logger.debug(
                "Failed to import %s from %s",
                class_name,
                module_path,
                exc_info=ex,
            )

        if instrumentor_imported:
            try:
                instrumentor_class = getattr(module, class_name)
                instrumentor_class().instrument()
            except Exception as ex:  # pylint: disable=broad-except
                _logger.warning(
                    "Exception occurred when instrumenting using: %s.",
                    class_name,
                    exc_info=ex,
                )

def _setup_browser_sdk_loader(configurations: Dict[str, ConfigurationValue]):
    """Setup browser SDK loader for supported frameworks.

    :param configurations: Configuration dictionary containing browser SDK loader settings.
    :type configurations: Dict[str, ConfigurationValue]
    """
    try:
        # Get browser SDK loader configuration
        browser_sdk_loader_config_value = configurations.get(BROWSER_SDK_LOADER_CONFIG_ARG)
        if isinstance(browser_sdk_loader_config_value, dict):
            browser_sdk_loader_config = browser_sdk_loader_config_value
        else:
            # Create typed empty dict to satisfy mypy
            browser_sdk_loader_config = cast(Dict[str, Any], {})

        # Check if browser SDK loader should be enabled (default False)
        enabled = browser_sdk_loader_config.get("enabled", False)
        if not enabled:
            _logger.debug("Browser SDK loader disabled via configuration")
            return

        # Get connection string (use browser SDK config first, then main config)
        connection_string = (browser_sdk_loader_config.get("connection_string") or
                           cast(str, configurations.get("connection_string", "")))
        if not connection_string or not isinstance(connection_string, str):
            _logger.debug("No valid connection string - skipping browser SDK loader setup")
            return

        # Create BrowserSDKConfig object
        browser_config = BrowserSDKConfig(
            enabled=enabled,
            connection_string=connection_string
        )

        # Setup snippet injection for supported frameworks
        setup_snippet_injection(browser_config)

    except Exception as ex:  # pylint: disable=broad-except
        _logger.debug("Failed to setup browser SDK loader: %s", ex, exc_info=True)

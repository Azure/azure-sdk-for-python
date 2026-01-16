# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from logging import getLogger, Formatter
from os import environ
from typing import Dict

from opentelemetry.environment_variables import (
    OTEL_LOGS_EXPORTER,
    OTEL_METRICS_EXPORTER,
    OTEL_TRACES_EXPORTER,
)
from opentelemetry.instrumentation.environment_variables import (
    OTEL_PYTHON_DISABLED_INSTRUMENTATIONS,
)
from opentelemetry.sdk.environment_variables import (
    OTEL_EXPERIMENTAL_RESOURCE_DETECTORS,
    OTEL_TRACES_SAMPLER_ARG,
    OTEL_TRACES_SAMPLER,
)
from opentelemetry.sdk.resources import Resource

from opentelemetry.sdk.trace.sampling import (
    TraceIdRatioBased,
    ALWAYS_OFF,
    ALWAYS_ON,
    ParentBased,
)

from azure.monitor.opentelemetry._constants import (
    _AZURE_APP_SERVICE_RESOURCE_DETECTOR_NAME,
    _AZURE_VM_RESOURCE_DETECTOR_NAME,
    _FULLY_SUPPORTED_INSTRUMENTED_LIBRARIES,
    _PREVIEW_INSTRUMENTED_LIBRARIES,
    BROWSER_SDK_LOADER_CONFIG_ARG,
    DISABLE_LOGGING_ARG,
    DISABLE_METRICS_ARG,
    DISABLE_TRACING_ARG,
    DISTRO_VERSION_ARG,
    ENABLE_LIVE_METRICS_ARG,
    ENABLE_PERFORMANCE_COUNTERS_ARG,
    INSTRUMENTATION_OPTIONS_ARG,
    LOGGER_NAME_ARG,
    LOGGER_NAME_ENV_ARG,
    LOGGING_FORMATTER_ARG,
    LOGGING_FORMAT_ENV_ARG,
    RESOURCE_ARG,
    SAMPLING_RATIO_ARG,
    SAMPLING_TRACES_PER_SECOND_ARG,
    SPAN_PROCESSORS_ARG,
    LOG_RECORD_PROCESSORS_ARG,
    METRIC_READERS_ARG,
    VIEWS_ARG,
    RATE_LIMITED_SAMPLER,
    FIXED_PERCENTAGE_SAMPLER,
    ENABLE_TRACE_BASED_SAMPLING_ARG,
    SUPPORTED_OTEL_SAMPLERS,
    ALWAYS_OFF_SAMPLER,
    ALWAYS_ON_SAMPLER,
    TRACE_ID_RATIO_SAMPLER,
    PARENT_BASED_ALWAYS_ON_SAMPLER,
    PARENT_BASED_ALWAYS_OFF_SAMPLER,
    PARENT_BASED_TRACE_ID_RATIO_SAMPLER,
    SAMPLING_ARG,
    SAMPLER_TYPE,
)
from azure.monitor.opentelemetry._types import ConfigurationValue
from azure.monitor.opentelemetry._version import VERSION


_INVALID_FLOAT_MESSAGE = "Value of %s must be a float. Defaulting to %s: %s"
_INVALID_TRACES_PER_SECOND_MESSAGE = "Value of %s must be a positive number for traces per second. Defaulting to %s: %s"
_SUPPORTED_RESOURCE_DETECTORS = (
    _AZURE_APP_SERVICE_RESOURCE_DETECTOR_NAME,
    _AZURE_VM_RESOURCE_DETECTOR_NAME,
)

_logger = getLogger(__name__)


def _get_configurations(**kwargs) -> Dict[str, ConfigurationValue]:
    configurations = {}

    for key, val in kwargs.items():
        configurations[key] = val
    configurations[DISTRO_VERSION_ARG] = VERSION

    _default_disable_logging(configurations)
    _default_disable_metrics(configurations)
    _default_disable_tracing(configurations)
    _default_logger_name(configurations)
    _default_logging_formatter(configurations)
    _default_resource(configurations)
    _default_sampling_ratio(configurations)
    _default_instrumentation_options(configurations)
    _default_span_processors(configurations)
    _default_log_record_processors(configurations)
    _default_metric_readers(configurations)
    _default_enable_live_metrics(configurations)
    _default_enable_performance_counters(configurations)
    _default_views(configurations)
    _default_enable_trace_based_sampling(configurations)
    _default_browser_sdk_loader(configurations)

    return configurations


def _default_disable_logging(configurations):
    default = False
    if OTEL_LOGS_EXPORTER in environ:
        if environ[OTEL_LOGS_EXPORTER].lower().strip() == "none":
            default = True
    configurations[DISABLE_LOGGING_ARG] = default


def _default_disable_metrics(configurations):
    default = False
    if OTEL_METRICS_EXPORTER in environ:
        if environ[OTEL_METRICS_EXPORTER].lower().strip() == "none":
            default = True
    configurations[DISABLE_METRICS_ARG] = default


def _default_disable_tracing(configurations):
    default = False
    if OTEL_TRACES_EXPORTER in environ:
        if environ[OTEL_TRACES_EXPORTER].lower().strip() == "none":
            default = True
    configurations[DISABLE_TRACING_ARG] = default


def _default_logger_name(configurations):
    if LOGGER_NAME_ARG in configurations:
        return
    if LOGGER_NAME_ENV_ARG in environ:
        configurations[LOGGER_NAME_ARG] = environ[LOGGER_NAME_ENV_ARG]
    else:
        configurations.setdefault(LOGGER_NAME_ARG, "")


def _default_logging_formatter(configurations):
    formatter = configurations.get(LOGGING_FORMATTER_ARG)
    if formatter:
        if not isinstance(formatter, Formatter):
            configurations[LOGGING_FORMATTER_ARG] = None
            return
    elif LOGGING_FORMAT_ENV_ARG in environ:
        try:
            configurations[LOGGING_FORMATTER_ARG] = Formatter(environ[LOGGING_FORMAT_ENV_ARG])
        except Exception as ex:  # pylint: disable=broad-exception-caught
            _logger.warning(  # pylint: disable=do-not-log-exceptions-if-not-debug
                "Exception occurred when creating logging Formatter from format: %s, %s.",
                environ[LOGGING_FORMAT_ENV_ARG],
                ex,
            )
            configurations[LOGGING_FORMATTER_ARG] = None


def _default_resource(configurations):
    environ.setdefault(OTEL_EXPERIMENTAL_RESOURCE_DETECTORS, ",".join(_SUPPORTED_RESOURCE_DETECTORS))
    if RESOURCE_ARG not in configurations:
        configurations[RESOURCE_ARG] = Resource.create()
    else:
        configurations[RESOURCE_ARG] = Resource.create(configurations[RESOURCE_ARG].attributes)


# pylint: disable=too-many-statements,too-many-branches
def _default_sampling_ratio(configurations):
    default_value = 1.0
    sampler_type = environ.get(OTEL_TRACES_SAMPLER)
    sampler_arg = environ.get(OTEL_TRACES_SAMPLER_ARG)

    # Handle rate-limited sampler
    if sampler_type == RATE_LIMITED_SAMPLER:
        try:
            sampler_value = float(sampler_arg) if sampler_arg is not None else default_value
            if sampler_value < 0.0:
                _logger.error("Invalid value for OTEL_TRACES_SAMPLER_ARG. It should be a non-negative number.")
                sampler_value = default_value
            else:
                _logger.info("Using rate limited sampler: %s traces per second", sampler_value)
            configurations[SAMPLING_TRACES_PER_SECOND_ARG] = sampler_value
        except ValueError as e:
            _logger.error(  # pylint: disable=C
                _INVALID_TRACES_PER_SECOND_MESSAGE,
                OTEL_TRACES_SAMPLER_ARG,
                default_value,
                e,
            )
            configurations[SAMPLING_TRACES_PER_SECOND_ARG] = default_value

    # Handle fixed percentage sampler
    elif sampler_type in (FIXED_PERCENTAGE_SAMPLER, "microsoft.fixed.percentage"):  # to support older string
        try:
            sampler_value = float(sampler_arg) if sampler_arg is not None else default_value
            if sampler_value < 0.0 or sampler_value > 1.0:
                _logger.error("Invalid value for OTEL_TRACES_SAMPLER_ARG. It should be a value between 0 and 1.")
                sampler_value = default_value
            else:
                _logger.info("Using sampling ratio: %s", sampler_value)
            configurations[SAMPLING_RATIO_ARG] = sampler_value
        except ValueError as e:
            _logger.error(  # pylint: disable=C
                _INVALID_FLOAT_MESSAGE,
                OTEL_TRACES_SAMPLER_ARG,
                default_value,
                e,
            )
            configurations[SAMPLING_RATIO_ARG] = default_value

    # Handle always_on sampler
    elif sampler_type == ALWAYS_ON_SAMPLER:
        configurations[SAMPLING_ARG] = 1.0
        configurations[SAMPLER_TYPE] = ALWAYS_ON_SAMPLER

    # Handle always_off sampler
    elif sampler_type == ALWAYS_OFF_SAMPLER:
        configurations[SAMPLING_ARG] = 0.0
        configurations[SAMPLER_TYPE] = ALWAYS_OFF_SAMPLER

    # Handle trace_id_ratio sampler
    elif sampler_type == TRACE_ID_RATIO_SAMPLER:
        try:
            sampler_value = float(sampler_arg) if sampler_arg is not None else default_value
            if sampler_value < 0.0 or sampler_value > 1.0:
                _logger.error("Invalid value for OTEL_TRACES_SAMPLER_ARG. It should be a value between 0 and 1.")
                sampler_value = default_value
            else:
                _logger.info("Using sampling value: %s", sampler_value)
            configurations[SAMPLING_ARG] = sampler_value
        except ValueError as e:
            _logger.error(  # pylint: disable=C
                _INVALID_FLOAT_MESSAGE,
                OTEL_TRACES_SAMPLER_ARG,
                default_value,
                e,
            )
            configurations[SAMPLING_ARG] = default_value
        configurations[SAMPLER_TYPE] = TRACE_ID_RATIO_SAMPLER

    # Handle parentbased_always_on sampler
    elif sampler_type == PARENT_BASED_ALWAYS_ON_SAMPLER:
        configurations[SAMPLING_ARG] = 1.0
        configurations[SAMPLER_TYPE] = PARENT_BASED_ALWAYS_ON_SAMPLER

    # Handle parentbased_always_off sampler
    elif sampler_type == PARENT_BASED_ALWAYS_OFF_SAMPLER:
        configurations[SAMPLING_ARG] = 0.0
        configurations[SAMPLER_TYPE] = PARENT_BASED_ALWAYS_OFF_SAMPLER

    # Handle parentbased_trace_id_ratio sampler
    elif sampler_type == PARENT_BASED_TRACE_ID_RATIO_SAMPLER:
        try:
            sampler_value = float(sampler_arg) if sampler_arg is not None else default_value
            if sampler_value < 0.0 or sampler_value > 1.0:
                _logger.error("Invalid value for OTEL_TRACES_SAMPLER_ARG. It should be a value between 0 and 1.")
                sampler_value = default_value
            else:
                _logger.info("Using sampling value: %s", sampler_value)
            configurations[SAMPLING_ARG] = sampler_value
        except ValueError as e:
            _logger.error(  # pylint: disable=C
                _INVALID_FLOAT_MESSAGE,
                OTEL_TRACES_SAMPLER_ARG,
                default_value,
                e,
            )
            configurations[SAMPLING_ARG] = default_value
        configurations[SAMPLER_TYPE] = PARENT_BASED_TRACE_ID_RATIO_SAMPLER

    # Handle all other cases (no sampler type specified or unsupported sampler type)
    else:
        if configurations.get(SAMPLING_RATIO_ARG) is None:
            configurations[SAMPLING_RATIO_ARG] = default_value
        if sampler_type is not None:
            _logger.error(  # pylint: disable=C
                "Invalid argument for the sampler to be used for tracing. "
                "Supported values are %s. Defaulting to %s: %s",
                SUPPORTED_OTEL_SAMPLERS,
                FIXED_PERCENTAGE_SAMPLER,
                configurations[SAMPLING_RATIO_ARG],
            )


def _default_instrumentation_options(configurations):
    otel_disabled_instrumentations = _get_otel_disabled_instrumentations()

    merged_instrumentation_options = {}
    instrumentation_options = configurations.get(INSTRUMENTATION_OPTIONS_ARG, {})
    for lib_name in _FULLY_SUPPORTED_INSTRUMENTED_LIBRARIES:
        disabled_by_env_var = lib_name in otel_disabled_instrumentations
        options = {"enabled": not disabled_by_env_var}
        options.update(instrumentation_options.get(lib_name, {}))
        merged_instrumentation_options[lib_name] = options
    for lib_name in _PREVIEW_INSTRUMENTED_LIBRARIES:
        options = {"enabled": False}
        options.update(instrumentation_options.get(lib_name, {}))
        merged_instrumentation_options[lib_name] = options

    configurations[INSTRUMENTATION_OPTIONS_ARG] = merged_instrumentation_options


def _default_span_processors(configurations):
    configurations.setdefault(SPAN_PROCESSORS_ARG, [])


def _default_log_record_processors(configurations):
    configurations.setdefault(LOG_RECORD_PROCESSORS_ARG, [])


def _default_metric_readers(configurations):
    configurations.setdefault(METRIC_READERS_ARG, [])


def _default_enable_live_metrics(configurations):
    configurations.setdefault(ENABLE_LIVE_METRICS_ARG, False)


def _default_enable_performance_counters(configurations):
    configurations.setdefault(ENABLE_PERFORMANCE_COUNTERS_ARG, True)


def _default_views(configurations):
    configurations.setdefault(VIEWS_ARG, [])


def _default_browser_sdk_loader(configurations):
    """Set default browser SDK loader configuration.

    :param configurations: Configuration dictionary to update.
    :type configurations: dict
    """
    # Use cast to Dict[str, Any] to avoid MyPy ConfigurationValue Union type issues
    from typing import cast, Any
    configurations.setdefault(BROWSER_SDK_LOADER_CONFIG_ARG, cast(Dict[str, Any], {}))


def _get_otel_disabled_instrumentations():
    disabled_instrumentation = environ.get(OTEL_PYTHON_DISABLED_INSTRUMENTATIONS, "")
    disabled_instrumentation = disabled_instrumentation.split(",")
    # to handle users entering "requests , flask" or "requests, flask" with spaces
    disabled_instrumentation = [x.strip() for x in disabled_instrumentation]
    return disabled_instrumentation


def _is_instrumentation_enabled(configurations, lib_name):
    if INSTRUMENTATION_OPTIONS_ARG not in configurations:
        return False
    instrumentation_options = configurations[INSTRUMENTATION_OPTIONS_ARG]
    if lib_name not in instrumentation_options:
        return False
    library_options = instrumentation_options[lib_name]
    if "enabled" not in library_options:
        return False
    return library_options["enabled"] is True


def _default_enable_trace_based_sampling(configurations):
    configurations.setdefault(ENABLE_TRACE_BASED_SAMPLING_ARG, False)


def _get_sampler_from_name(sampler_type, sampler_arg):
    if sampler_type == ALWAYS_ON_SAMPLER:
        return ALWAYS_ON
    if sampler_type == ALWAYS_OFF_SAMPLER:
        return ALWAYS_OFF
    if sampler_type == TRACE_ID_RATIO_SAMPLER:
        ratio = float(sampler_arg) if sampler_arg is not None else 1.0
        return TraceIdRatioBased(ratio)
    if sampler_type == PARENT_BASED_ALWAYS_OFF_SAMPLER:
        return ParentBased(ALWAYS_OFF)
    if sampler_type == PARENT_BASED_TRACE_ID_RATIO_SAMPLER:
        ratio = float(sampler_arg) if sampler_arg is not None else 1.0
        return ParentBased(TraceIdRatioBased(ratio))
    return ParentBased(ALWAYS_ON)

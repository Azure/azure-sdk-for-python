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
    OTEL_TRACES_SAMPLER
)
from opentelemetry.sdk.resources import Resource

from azure.monitor.opentelemetry._constants import (
    _AZURE_APP_SERVICE_RESOURCE_DETECTOR_NAME,
    _AZURE_VM_RESOURCE_DETECTOR_NAME,
    _FULLY_SUPPORTED_INSTRUMENTED_LIBRARIES,
    _PREVIEW_INSTRUMENTED_LIBRARIES,
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
    VIEWS_ARG,
    RATE_LIMITED_SAMPLER,
    FIXED_PERCENTAGE_SAMPLER,
    ENABLE_TRACE_BASED_SAMPLING_ARG,
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
    _default_enable_live_metrics(configurations)
    _default_enable_performance_counters(configurations)
    _default_views(configurations)
    _default_enable_trace_based_sampling(configurations)

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


def _default_sampling_ratio(configurations):
    default_value = 1.0
    sampler_type = environ.get(OTEL_TRACES_SAMPLER)
    sampler_arg = environ.get(OTEL_TRACES_SAMPLER_ARG)

    # Handle rate-limited sampler
    if sampler_type == RATE_LIMITED_SAMPLER:
        try:
            sampler_value = float(sampler_arg)
            if sampler_value < 0:
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
    elif sampler_type == FIXED_PERCENTAGE_SAMPLER:
        try:
            sampler_value = float(sampler_arg)
            if sampler_value < 0:
                _logger.error("Invalid value for OTEL_TRACES_SAMPLER_ARG. It should be a non-negative number.")
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

    # Handle all other cases (no sampler type specified or unsupported sampler type)
    else:
        if configurations.get(SAMPLING_RATIO_ARG) is None:
            configurations[SAMPLING_RATIO_ARG] = default_value
        if sampler_type is not None:
            _logger.error(  # pylint: disable=C
                "Invalid argument for the sampler to be used for tracing. "
                "Supported values are %s and %s. Defaulting to %s: %s",
                RATE_LIMITED_SAMPLER,
                FIXED_PERCENTAGE_SAMPLER,
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


def _default_enable_live_metrics(configurations):
    configurations.setdefault(ENABLE_LIVE_METRICS_ARG, False)


def _default_enable_performance_counters(configurations):
    configurations.setdefault(ENABLE_PERFORMANCE_COUNTERS_ARG, True)


def _default_views(configurations):
    configurations.setdefault(VIEWS_ARG, [])


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
    if not lib_name in instrumentation_options:
        return False
    library_options = instrumentation_options[lib_name]
    if "enabled" not in library_options:
        return False
    return library_options["enabled"] is True

def _default_enable_trace_based_sampling(configurations):
    configurations.setdefault(ENABLE_TRACE_BASED_SAMPLING_ARG, False)

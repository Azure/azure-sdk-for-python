# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from logging import getLogger
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
    INSTRUMENTATION_OPTIONS_ARG,
    LOGGER_NAME_ARG,
    RESOURCE_ARG,
    SAMPLING_RATIO_ARG,
    SPAN_PROCESSORS_ARG,
    VIEWS_ARG,
)
from azure.monitor.opentelemetry._types import ConfigurationValue
from azure.monitor.opentelemetry._version import VERSION


_INVALID_FLOAT_MESSAGE = "Value of %s must be a float. Defaulting to %s: %s"
_SUPPORTED_RESOURCE_DETECTORS = (
    _AZURE_APP_SERVICE_RESOURCE_DETECTOR_NAME,
    _AZURE_VM_RESOURCE_DETECTOR_NAME,
)
# TODO: remove when sampler uses env var instead
SAMPLING_RATIO_ENV_VAR = OTEL_TRACES_SAMPLER_ARG


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
    _default_resource(configurations)
    _default_sampling_ratio(configurations)
    _default_instrumentation_options(configurations)
    _default_span_processors(configurations)
    _default_enable_live_metrics(configurations)
    _default_views(configurations)

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
    configurations.setdefault(LOGGER_NAME_ARG, "")


def _default_resource(configurations):
    environ.setdefault(
        OTEL_EXPERIMENTAL_RESOURCE_DETECTORS,
        ",".join(_SUPPORTED_RESOURCE_DETECTORS)
    )
    if RESOURCE_ARG not in configurations:
        configurations[RESOURCE_ARG] = Resource.create()
    else:
        configurations[RESOURCE_ARG] = Resource.create(configurations[RESOURCE_ARG].attributes)


# TODO: remove when sampler uses env var instead
def _default_sampling_ratio(configurations):
    default = 1.0
    if SAMPLING_RATIO_ENV_VAR in environ:
        try:
            default = float(environ[SAMPLING_RATIO_ENV_VAR])
        except ValueError as e:
            _logger.error(
                _INVALID_FLOAT_MESSAGE,
                SAMPLING_RATIO_ENV_VAR,
                default,
                e,
            )
    configurations[SAMPLING_RATIO_ARG] = default


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


def _default_views(configurations):
    configurations.setdefault(VIEWS_ARG, [])


def _get_otel_disabled_instrumentations():
    disabled_instrumentation = environ.get(
        OTEL_PYTHON_DISABLED_INSTRUMENTATIONS, ""
    )
    disabled_instrumentation = disabled_instrumentation.split(",")
    # to handle users entering "requests , flask" or "requests, flask" with spaces
    disabled_instrumentation = [
        x.strip() for x in disabled_instrumentation
    ]
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
